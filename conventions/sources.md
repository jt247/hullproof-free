# Research and Source Tracking

Every claim in the standard traces to a recorded source. Sources are listed in `kit/docs/hullproof/REFERENCES.md` and cited by ID.

## Source ID

`SRC-[NUMBER]`, three digits, sequential, never reused. For example: `SRC-001`.

## Required fields

| Field | Example |
|-------|---------|
| ID | SRC-001 |
| Title | OWASP Application Security Verification Standard |
| Publisher | OWASP Foundation |
| URL | Canonical link to the exact version |
| Version | 5.0.0 |
| Accessed | 2026-10-02 (YYYY-MM-DD) |
| Type | STANDARD, VENDOR DOC, RESEARCH, ADVISORY, INCIDENT |
| License | Exact license, for example CC BY-SA 4.0, or "terms of use" with a link |
| Usage | LINK ONLY, SHORT QUOTE, or REUSE ALLOWED |

## Rules

1. Prefer primary sources: the standard body, the vendor's own documentation, or the original advisory.
2. Never invent statistics, quotes, or attributions. If a claim cannot be sourced, cut it or label it Unverified in the requirement text, with the instruction to check the current vendor documents.
3. Record the license before using a source. Text from share alike licenses (such as CC BY-SA) is never copied into either edition. Map to it by ID and link out.
4. Write requirements in Hullproof's own words. Mappings to other standards hold IDs and links only.
5. When a source publishes a new version, recheck every requirement that cites it and update the version field.
