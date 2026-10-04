#!/usr/bin/env python3
"""Rebuild the final live policy, function and grant set from ordered SQL migrations.

Usage: policy_set.py [--no-platform-defaults] [--schemas public,app] PATH [PATH ...]
PATH is a migrations directory (files read in name order) or single .sql files.
Output is object names and counts only. No row data, no expressions.
Standard library only. Exit code is always 0 unless the input cannot be read.

Limits (ponytail): regex based parser, not a full SQL parser. It does not execute DO blocks
or dynamic SQL, and it ignores role membership and ownership. Treat output as a map to verify
against a live catalog, not as proof.
"""
import argparse
import os
import re
import sys

CLIENT = ("anon", "authenticated")
TABLE_PRIVS = {"select", "insert", "update", "delete", "truncate", "references", "trigger"}
ID = r'(?:"[^"]+"|[A-Za-z_][\w$]*)(?:\s*\.\s*(?:"[^"]+"|[A-Za-z_][\w$]*))?'
SENSITIVE_TOKENS = {"role", "roles", "plan", "credit", "credits", "admin", "status", "verified",
                    "stripe", "paddle", "tier", "balance", "superuser"}
HIGH_TOKENS = SENSITIVE_TOKENS - {"status"}
MULTIWORD_TYPE_START = {"double", "character", "timestamp", "time", "bit", "national", "interval"}


# ---------- lexing ----------
def clean_and_split(text):
    """Strip comments, split on top level semicolons. Returns list of (raw, masked) pairs.
    masked has string and dollar quote contents replaced by 'x' so structure can be matched."""
    raw, mask, stmts = [], [], []
    i, n = 0, len(text)

    def flush():
        r = "".join(raw).strip()
        m = "".join(mask).strip()
        if r:
            stmts.append((r, m))
        raw.clear()
        mask.clear()

    while i < n:
        c = text[i]
        two = text[i:i + 2]
        if two == "--":
            j = text.find("\n", i)
            i = n if j < 0 else j
            continue
        if two == "/*":
            j = text.find("*/", i + 2)
            i = n if j < 0 else j + 2
            raw.append(" ")
            mask.append(" ")
            continue
        if c == "'":
            j = i + 1
            while j < n:
                if text[j] == "'" and text[j + 1:j + 2] == "'":
                    j += 2
                    continue
                if text[j] == "'":
                    break
                j += 1
            seg = text[i:j + 1]
            raw.append(seg)
            mask.append("'" + "x" * (len(seg) - 2) + "'" if len(seg) >= 2 else seg)
            i = j + 1
            continue
        m = re.match(r"\$[A-Za-z_]*\$", text[i:i + 64]) if c == "$" else None
        if m:
            tag = m.group(0)
            j = text.find(tag, i + len(tag))
            j = n if j < 0 else j + len(tag)
            seg = text[i:j]
            raw.append(seg)
            mask.append(tag + "x" * max(len(seg) - 2 * len(tag), 0) + tag if len(seg) >= 2 * len(tag) else seg)
            i = j
            continue
        if c == ";":
            flush()
            i += 1
            continue
        raw.append(c)
        mask.append(c)
        i += 1
    flush()
    return stmts


def match_paren(s, i):
    """s[i] is '('. Return index of the matching ')' or -1."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "(":
            depth += 1
        elif s[j] == ")":
            depth -= 1
            if depth == 0:
                return j
    return -1


def split_top(s, sep=","):
    out, depth, cur = [], 0, []
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == sep and depth == 0:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    tail = "".join(cur).strip()
    if tail:
        out.append(tail)
    return out


def norm_id(tok, default_schema="public"):
    parts = [p.strip() for p in re.split(r"\s*\.\s*", tok.strip()) if p.strip()]
    parts = [p[1:-1] if p.startswith('"') else p.lower() for p in parts]
    if len(parts) == 1:
        parts.insert(0, default_schema)
    return ".".join(parts[-2:])


def norm_role(tok):
    t = tok.strip()
    t = re.sub(r"^group\s+", "", t, flags=re.I)
    t = t[1:-1] if t.startswith('"') else t.lower()
    return "public" if t in ("public", "") else t


def show(name):
    return name[len("public."):] if name.startswith("public.") else name


# ---------- state ----------
class State:
    def __init__(self, platform_defaults):
        self.tables = {}      # name -> {"cols": set, "rls": bool, "force": bool, "order": int}
        self.policies = {}    # (table, policy) -> dict
        self.functions = {}   # key -> dict
        self.tpriv = {}       # table -> role -> set(priv)
        self.cpriv = {}       # table -> role -> priv -> set(cols)
        self.fgrant = {}      # fkey -> set(roles)
        self.def_tbl = {}     # role -> set(priv) for tables created later
        self.def_fn = {"public"}
        self.warnings = []
        if platform_defaults:
            for r in ("anon", "authenticated", "service_role"):
                self.def_tbl[r] = set(TABLE_PRIVS)
            self.def_fn |= {"anon", "authenticated", "service_role"}


def parse_roles(s):
    s = re.split(r"\bgranted\s+by\b|\bwith\s+grant\s+option\b|\bcascade\b|\brestrict\b", s, flags=re.I)[0]
    return [norm_role(r) for r in split_top(s) if r.strip()]


def fn_key(name, args_masked):
    """Identity is name plus input arg types. Names are dropped heuristically."""
    types = []
    for a in split_top(args_masked):
        a = re.split(r"\s+default\s+|\s*=\s*", a, flags=re.I)[0].strip()
        toks = a.split()
        while toks and toks[0].lower() in ("in", "out", "inout", "variadic"):
            if toks[0].lower() == "out":
                toks = []
                break
            toks = toks[1:]
        if not toks:
            continue
        if len(toks) > 1 and toks[0].lower() not in MULTIWORD_TYPE_START:
            toks = toks[1:]
        types.append(" ".join(toks).lower())
    return f"{norm_id(name)}({','.join(types)})"


# ---------- statement handlers ----------
def h_create_table(st, raw, m):
    mt = re.match(rf"create\s+(?:unlogged\s+|(?:global\s+|local\s+)?temp(?:orary)?\s+)?table\s+(?:if\s+not\s+exists\s+)?({ID})\s*\(", m, re.I)
    if not mt:
        return False
    name = norm_id(mt.group(1))
    start = mt.end() - 1
    end = match_paren(m, start)
    body = m[start + 1:end] if end > 0 else ""
    cols = set()
    for seg in split_top(body):
        first = seg.split()[0].strip('"') if seg.split() else ""
        if first.lower() in ("constraint", "primary", "foreign", "unique", "check", "like", "exclude"):
            continue
        cols.add(first.lower() if not seg.startswith('"') else first)
    if name not in st.tables:
        st.tables[name] = {"cols": cols, "rls": False, "force": False, "order": len(st.tables)}
    else:
        st.tables[name]["cols"] |= cols
    st.tpriv[name] = {r: set(p) for r, p in st.def_tbl.items()}
    st.cpriv[name] = {}
    return True


def h_alter_table(st, raw, m):
    mt = re.match(rf"alter\s+table\s+(?:if\s+exists\s+)?(?:only\s+)?({ID})\s+(.*)$", m, re.I | re.S)
    if not mt:
        return False
    name = norm_id(mt.group(1))
    t = st.tables.setdefault(name, {"cols": set(), "rls": False, "force": False, "order": len(st.tables), "external": True})
    for act in split_top(mt.group(2)):
        a = " ".join(act.split()).lower()
        if a == "enable row level security":
            t["rls"] = True
        elif a == "disable row level security":
            t["rls"] = False
        elif a == "force row level security":
            t["force"] = True
        elif a == "no force row level security":
            t["force"] = False
        else:
            mc = re.match(rf"add\s+(?:column\s+)?(?:if\s+not\s+exists\s+)?({ID})\s+\w", act, re.I)
            if mc and not re.match(r"add\s+(constraint|primary|foreign|unique|check|exclude)\b", act, re.I):
                t["cols"].add(mc.group(1).strip('"').lower())
            md = re.match(rf"drop\s+column\s+(?:if\s+exists\s+)?({ID})", act, re.I)
            if md:
                t["cols"].discard(md.group(1).strip('"').lower())
            mr = re.match(rf"rename\s+column\s+({ID})\s+to\s+({ID})", act, re.I)
            if mr:
                t["cols"].discard(mr.group(1).strip('"').lower())
                t["cols"].add(mr.group(2).strip('"').lower())
            mn = re.match(rf"rename\s+to\s+({ID})", act, re.I)
            if mn:
                new = norm_id(mn.group(1), name.split(".")[0])
                st.tables[new] = st.tables.pop(name)
                for d in (st.tpriv, st.cpriv):
                    if name in d:
                        d[new] = d.pop(name)
                for k in [k for k in st.policies if k[0] == name]:
                    p = st.policies.pop(k)
                    p["table"] = new
                    st.policies[(new, k[1])] = p
    return True


def h_drop_table(st, raw, m):
    mt = re.match(r"drop\s+table\s+(?:if\s+exists\s+)?(.*?)(?:\s+cascade|\s+restrict)?$", m, re.I | re.S)
    if not mt:
        return False
    for tok in split_top(mt.group(1)):
        name = norm_id(tok)
        st.tables.pop(name, None)
        st.tpriv.pop(name, None)
        st.cpriv.pop(name, None)
        for k in [k for k in st.policies if k[0] == name]:
            del st.policies[k]
    return True


def parse_policy_tail(rest_m, rest_raw, cur=None):
    """Parse [AS x] [FOR cmd] [TO roles] [USING (..)] [WITH CHECK (..)] into a dict of present fields."""
    out = {}
    pos = 0
    ma = re.match(r"\s*as\s+(permissive|restrictive)", rest_m, re.I)
    if ma:
        out["restrictive"] = ma.group(1).lower() == "restrictive"
        pos = ma.end()
    mf = re.match(r"\s*for\s+(all|select|insert|update|delete)", rest_m[pos:], re.I)
    if mf:
        out["cmd"] = mf.group(1).lower()
        pos += mf.end()
    mto = re.match(r"\s*to\s+(.+?)(?=\s+using\s*\(|\s+with\s+check\s*\(|$)", rest_m[pos:], re.I | re.S)
    if mto:
        out["roles"] = parse_roles(mto.group(1))
        pos += mto.end()
    for kw, field in (("using", "using"), ("with\\s+check", "check")):
        mk = re.search(rf"\b{kw}\s*\(", rest_m[pos:], re.I)
        if mk:
            s = pos + mk.end() - 1
            e = match_paren(rest_m, s)
            if e > 0:
                out[field] = True
                out[field + "_text"] = rest_raw[s:e + 1].lower()
    return out


def h_create_policy(st, raw, m):
    mt = re.match(rf'create\s+policy\s+({ID}|"[^"]+")\s+on\s+({ID})(.*)$', m, re.I | re.S)
    if not mt:
        return False
    pname = mt.group(1).strip('"') if mt.group(1).startswith('"') else mt.group(1).lower()
    table = norm_id(mt.group(2))
    tail_start = mt.start(3)
    p = {"table": table, "name": pname, "cmd": "all", "restrictive": False, "roles": None,
         "using": False, "check": False, "using_text": "", "check_text": ""}
    p.update(parse_policy_tail(mt.group(3), raw[tail_start:]))
    st.policies[(table, pname)] = p
    return True


def h_alter_policy(st, raw, m):
    mt = re.match(rf'alter\s+policy\s+({ID}|"[^"]+")\s+on\s+({ID})(.*)$', m, re.I | re.S)
    if not mt:
        return False
    pname = mt.group(1).strip('"') if mt.group(1).startswith('"') else mt.group(1).lower()
    table = norm_id(mt.group(2))
    p = st.policies.get((table, pname))
    if not p:
        st.warnings.append(f"ALTER POLICY on unknown policy {show(table)}.{pname}")
        return True
    rn = re.match(rf"\s*rename\s+to\s+({ID}|\"[^\"]+\")", mt.group(3), re.I)
    if rn:
        new = rn.group(1).strip('"') if rn.group(1).startswith('"') else rn.group(1).lower()
        del st.policies[(table, pname)]
        p["name"] = new
        st.policies[(table, new)] = p
        return True
    upd = parse_policy_tail(mt.group(3), raw[mt.start(3):])
    upd.pop("cmd", None)
    upd.pop("restrictive", None)
    p.update(upd)
    return True


def h_drop_policy(st, raw, m):
    mt = re.match(rf'drop\s+policy\s+(?:if\s+exists\s+)?({ID}|"[^"]+")\s+on\s+({ID})', m, re.I)
    if not mt:
        return False
    pname = mt.group(1).strip('"') if mt.group(1).startswith('"') else mt.group(1).lower()
    st.policies.pop((norm_id(mt.group(2)), pname), None)
    return True


def func_head(m):
    mt = re.match(rf"(?:create\s+(?:or\s+replace\s+)?|alter\s+|drop\s+)(?:function|procedure)\s+(?:if\s+exists\s+)?({ID})\s*\(", m, re.I)
    if not mt:
        return None
    s = mt.end() - 1
    e = match_paren(m, s)
    return mt.group(1), m[s + 1:e], e


def h_create_function(st, raw, m):
    if not re.match(r"create\s+(?:or\s+replace\s+)?(?:function|procedure)\b", m, re.I):
        return False
    head = func_head(m)
    if not head:
        return True
    name, args, e = head
    rest = m[e + 1:]
    key = fn_key(name, args)
    definer = bool(re.search(r"\bsecurity\s+definer\b", rest, re.I))
    sp = bool(re.search(r"\bset\s+search_path\b", rest, re.I))
    exists = key in st.functions
    st.functions[key] = {"name": norm_id(name), "definer": definer, "search_path": sp}
    if not exists:
        st.fgrant[key] = set(st.def_fn)
    return True


def h_alter_function(st, raw, m):
    if not re.match(r"alter\s+(?:function|procedure)\b", m, re.I):
        return False
    head = func_head(m)
    if not head:
        return True
    key = fn_key(head[0], head[1])
    rest = m[head[2] + 1:]
    f = st.functions.get(key)
    if not f:
        st.warnings.append(f"ALTER FUNCTION on unknown function {show(key)}")
        return True
    if re.search(r"\bsecurity\s+definer\b", rest, re.I):
        f["definer"] = True
    if re.search(r"\b(?:security\s+invoker|external\s+security\s+invoker)\b", rest, re.I):
        f["definer"] = False
    if re.search(r"\bset\s+search_path\b", rest, re.I):
        f["search_path"] = True
    if re.search(r"\breset\s+(search_path|all)\b", rest, re.I):
        f["search_path"] = False
    mr = re.search(rf"\brename\s+to\s+({ID})", rest, re.I)
    if mr:
        new = norm_id(mr.group(1), key.split(".")[0])
        newkey = new + key[key.index("("):]
        st.functions[newkey] = st.functions.pop(key)
        st.functions[newkey]["name"] = new
        st.fgrant[newkey] = st.fgrant.pop(key, set())
    return True


def h_drop_function(st, raw, m):
    mt = re.match(r"drop\s+(?:function|procedure)\s+(?:if\s+exists\s+)?(.*?)(?:\s+cascade|\s+restrict)?$", m, re.I | re.S)
    if not mt:
        return False
    for item in split_top(mt.group(1)):
        head = func_head("drop function " + item)
        if head:
            keys = [fn_key(head[0], head[1])]
        else:  # no arg list: drop every overload of that name
            nm = norm_id(item.strip())
            keys = [k for k in st.functions if k.startswith(nm + "(")]
        for k in keys:
            st.functions.pop(k, None)
            st.fgrant.pop(k, None)
    return True


def expand_privs(items, is_fn):
    """Return (table_level_privs, column_level {priv: cols})."""
    tbl, col = set(), {}
    for it in items:
        mc = re.match(r"(\w+(?:\s+privileges)?)\s*\((.*)\)\s*$", it.strip(), re.I | re.S)
        if mc:
            pr = mc.group(1).lower().split()[0]
            cols = {c.strip().strip('"').lower() for c in mc.group(2).split(",")}
            col.setdefault(pr, set()).update(cols)
            continue
        p = it.strip().lower()
        if p.startswith("all"):
            tbl |= {"execute"} if is_fn else set(TABLE_PRIVS)
        else:
            tbl.add(p)
    return tbl, col


def h_grant_revoke(st, raw, m):
    mt = re.match(r"(grant|revoke)\s+(grant\s+option\s+for\s+)?(.*?)\s+on\s+(.*?)\s+(to|from)\s+(.*)$", m, re.I | re.S)
    if not mt:
        return False
    is_grant = mt.group(1).lower() == "grant"
    privs = split_top(mt.group(3))
    target = " ".join(mt.group(4).split())
    roles = parse_roles(mt.group(6))
    tl = target.lower()
    if re.match(r"(schema|database|sequence|sequences|all sequences|type|domain|language|large object|foreign|tablespace)\b", tl) or "all sequences" in tl:
        return True
    is_fn = bool(re.match(r"(all\s+)?(functions|procedures|routines|function|procedure|routine)\b", tl))
    tbl_privs, col_privs = expand_privs(privs, is_fn)
    if is_fn:
        mall = re.match(r"all\s+(?:functions|procedures|routines)\s+in\s+schema\s+(.+)$", target, re.I)
        if mall:
            schemas = [s.strip().strip('"').lower() for s in mall.group(1).split(",")]
            keys = [k for k in st.functions if k.split(".")[0] in schemas]
        else:
            body = re.sub(r"^(?:function|procedure|routine)\s+", "", target, flags=re.I)
            keys = []
            for item in split_top(body):
                head = func_head("drop function " + item)
                if head:
                    keys.append(fn_key(head[0], head[1]))
                else:
                    nm = norm_id(item.strip())
                    keys += [k for k in st.functions if k.startswith(nm + "(")]
        for k in keys:
            g = st.fgrant.setdefault(k, set())
            for r in roles:
                if "execute" in tbl_privs:
                    (g.add if is_grant else g.discard)(r)
        return True
    mall = re.match(r"all\s+tables\s+in\s+schema\s+(.+)$", target, re.I)
    if mall:
        schemas = [s.strip().strip('"').lower() for s in mall.group(1).split(",")]
        tables = [t for t in st.tables if t.split(".")[0] in schemas]
    else:
        body = re.sub(r"^table\s+", "", target, flags=re.I)
        tables = [norm_id(t) for t in split_top(body)]
    for t in tables:
        tp = st.tpriv.setdefault(t, {})
        cp = st.cpriv.setdefault(t, {})
        for r in roles:
            if is_grant:
                tp.setdefault(r, set()).update(tbl_privs)
                for pr, cols in col_privs.items():
                    cp.setdefault(r, {}).setdefault(pr, set()).update(cols)
            else:
                tp.setdefault(r, set()).difference_update(tbl_privs)
                for pr in tbl_privs:
                    cp.get(r, {}).pop(pr, None)
                for pr, cols in col_privs.items():
                    cp.get(r, {}).get(pr, set()).difference_update(cols)
    return True


def h_default_privs(st, raw, m):
    mt = re.match(r"alter\s+default\s+privileges\s+(?:for\s+(?:role|user)\s+\S+\s+)?(?:in\s+schema\s+\S+\s+)?(grant|revoke)\s+(.*?)\s+on\s+(tables|functions|routines|sequences|types|schemas)\s+(to|from)\s+(.*)$", m, re.I | re.S)
    if not mt:
        return False
    kind = mt.group(3).lower()
    is_grant = mt.group(1).lower() == "grant"
    roles = parse_roles(mt.group(5))
    privs, _ = expand_privs(split_top(mt.group(2)), kind in ("functions", "routines"))
    if kind == "tables":
        for r in roles:
            cur = st.def_tbl.setdefault(r, set())
            cur.update(privs) if is_grant else cur.difference_update(privs)
    elif kind in ("functions", "routines") and "execute" in privs:
        for r in roles:
            (st.def_fn.add if is_grant else st.def_fn.discard)(r)
    return True


HANDLERS = [h_create_table, h_alter_table, h_drop_table, h_create_policy, h_alter_policy,
            h_drop_policy, h_create_function, h_alter_function, h_drop_function,
            h_default_privs, h_grant_revoke]


def squeeze(raw, masked):
    """Collapse whitespace runs outside strings in both texts, keeping them aligned."""
    ro, mo, prev = [], [], False
    for rc, mc in zip(raw, masked):
        if mc.isspace():
            if not prev:
                ro.append(" ")
                mo.append(" ")
            prev = True
        else:
            ro.append(rc)
            mo.append(mc)
            prev = False
    return "".join(ro), "".join(mo)


def apply(st, raw, masked):
    r, m = squeeze(raw, masked)
    for h in HANDLERS:
        if h(st, r, m):
            return


# ---------- analysis ----------
def eff_table_privs(st, table, role):
    tp = st.tpriv.get(table, {})
    return tp.get(role, set()) | tp.get("public", set())


def eff_col_privs(st, table, role, priv):
    cp = st.cpriv.get(table, {})
    return cp.get(role, {}).get(priv, set()) | cp.get("public", {}).get(priv, set())


def sensitive_cols(cols):
    out = []
    for c in sorted(cols):
        toks = set(re.split(r"[_\W]+", c.lower()))
        if toks & SENSITIVE_TOKENS:
            out.append(c)
    return out


def analyze(st, schemas):
    flags = []

    def add(sev, sec, code, obj, note=""):
        flags.append((sev, sec, code, obj, note))

    for (table, pname), p in sorted(st.policies.items()):
        obj = f"{show(table)}.{pname}"
        if p["roles"] is None or "public" in p["roles"]:
            add("MEDIUM", "SEC-DB-002", "POLICY_NO_ROLE", obj, "no TO clause, applies to PUBLIC including anon")
        if p["cmd"] in ("update", "all") and p["using"] and not p["check"]:
            add("LOW", "SEC-DB-002", "UPDATE_NO_WITH_CHECK", obj, "hygiene only, Postgres reuses USING as the check")
        if "user_metadata" in p["using_text"] + p["check_text"] or "raw_user_meta_data" in p["using_text"] + p["check_text"]:
            add("CRITICAL", "SEC-DB-006", "POLICY_USES_USER_METADATA", obj, "reads user editable claims")
    for key, f in sorted(st.functions.items()):
        if not f["definer"]:
            continue
        who = st.fgrant.get(key, set())
        if not f["search_path"]:
            add("HIGH", "PRO-EDITION", "DEFINER_NO_SEARCH_PATH", show(key))
        if "public" in who or "anon" in who:
            add("HIGH", "SEC-DB-008", "DEFINER_EXEC_ANON_OR_PUBLIC", show(key),
                "executable by " + ",".join(sorted(who & {"public", "anon"})))
        elif "authenticated" in who:
            add("INFO", "SEC-DB-008", "DEFINER_EXEC_AUTHENTICATED", show(key), "confirm identity derives from the session user")
    for table, t in sorted(st.tables.items()):
        if t.get("external") or table.split(".")[0] not in schemas:
            continue
        client_grants = any(eff_table_privs(st, table, r) or st.cpriv.get(table, {}).get(r) for r in CLIENT)
        if not t["rls"]:
            add("CRITICAL" if client_grants else "HIGH", "SEC-DB-001", "RLS_NOT_ENABLED", show(table),
                "client roles hold grants" if client_grants else "no client grants found")
        sens = sensitive_cols(t["cols"])
        if not sens:
            continue
        hit_cols, roles_hit, pols = set(), set(), set()
        for (tb, pname), p in st.policies.items():
            if tb != table or p["restrictive"] or p["cmd"] not in ("insert", "update", "all"):
                continue
            prole = set(p["roles"] or ["public"])
            prole = set(CLIENT) if "public" in prole else prole & set(CLIENT)
            for r in prole:
                cols = set()
                for pr in ("insert", "update"):
                    if p["cmd"] not in (pr, "all"):
                        continue
                    if pr in eff_table_privs(st, table, r):
                        cols |= set(sens)
                    else:
                        cols |= set(sens) & eff_col_privs(st, table, r, pr)
                if cols:
                    hit_cols |= cols
                    roles_hit.add(r)
                    pols.add(pname)
        if hit_cols:
            sev = "CRITICAL" if any(set(re.split(r"[_\W]+", c)) & HIGH_TOKENS for c in hit_cols) else "HIGH"
            add(sev, "SEC-DB-033", "CLIENT_WRITABLE_SENSITIVE_COLUMNS", show(table),
                "columns " + ",".join(sorted(hit_cols)) + " | roles " + ",".join(sorted(roles_hit)) +
                " | policies " + ",".join(sorted(pols)))
    order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
    return sorted(flags, key=lambda f: (order[f[0]], f[2], f[3]))


# ---------- report ----------
def report(st, flags, files, schemas):
    out = []
    w = out.append
    w(f"FILES {len(files)}")
    w("")
    w(f"TABLES {len(st.tables)}")
    for name, t in sorted(st.tables.items()):
        grants = []
        for r in sorted(set(st.tpriv.get(name, {})) | set(st.cpriv.get(name, {}))):
            tp = sorted(eff for eff in st.tpriv.get(name, {}).get(r, ()) if eff)
            cp = {k: sorted(v) for k, v in st.cpriv.get(name, {}).get(r, {}).items() if v}
            if tp or cp:
                s = r + ":" + (",".join(tp) if len(tp) < len(TABLE_PRIVS) else "all")
                if cp:
                    s += " cols[" + ";".join(f"{k}={','.join(v)}" for k, v in sorted(cp.items())) + "]"
                grants.append(s)
        w(f"  {show(name)} | rls={'on' if t['rls'] else 'off'} | columns={len(t['cols'])} | grants {' '.join(grants) or 'none'}")
    w("")
    w(f"POLICIES {len(st.policies)}")
    for (table, pname), p in sorted(st.policies.items()):
        w(f"  {show(table)}.{pname} | {p['cmd']} | {'restrictive' if p['restrictive'] else 'permissive'} | "
          f"to {','.join(p['roles']) if p['roles'] else 'none'} | using={'y' if p['using'] else 'n'} | check={'y' if p['check'] else 'n'}")
    w("")
    w(f"FUNCTIONS {len(st.functions)}")
    for key, f in sorted(st.functions.items()):
        who = ",".join(sorted(st.fgrant.get(key, set()))) or "owner only"
        w(f"  {show(key)} | {'definer' if f['definer'] else 'invoker'} | search_path={'set' if f['search_path'] else 'unset'} | execute {who}")
    w("")
    counts = {}
    for f in flags:
        counts[f[2]] = counts.get(f[2], 0) + 1
    w(f"FLAGS {len(flags)}")
    for sev, sec, code, obj, note in flags:
        w(f"  {sev} | {sec} | {code} | {obj}" + (f" | {note}" if note else ""))
    w("")
    w("COUNTS " + (" ".join(f"{k}={v}" for k, v in sorted(counts.items())) or "none"))
    for wmsg in st.warnings:
        w(f"WARNING {wmsg}")
    return "\n".join(out)


def collect(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, names in os.walk(p):
                files += [os.path.join(root, n) for n in names if n.endswith(".sql")]
        else:
            files.append(p)
    # ponytail: name order, which is chronological for Supabase timestamp names. Full path sort for a single dir.
    return sorted(files, key=lambda f: (os.path.basename(f), f))


def build(paths, platform_defaults=True, schemas=("public",)):
    files = collect(paths)
    st = State(platform_defaults)
    for f in files:
        with open(f, encoding="utf-8", errors="replace") as fh:
            for raw, masked in clean_and_split(fh.read()):
                apply(st, raw, masked)
    return st, files, analyze(st, set(schemas))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--no-platform-defaults", action="store_true",
                    help="do not assume Supabase default grants to anon, authenticated and service_role")
    ap.add_argument("--schemas", default="public", help="comma list of schemas to check for RLS and column flags")
    a = ap.parse_args(argv)
    try:
        st, files, flags = build(a.paths, not a.no_platform_defaults, a.schemas.split(","))
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(report(st, flags, files, a.schemas.split(",")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
