from markupsafe import Markup
from flask import render_template_string


def bad(user_html, tpl):
    # ruleid: hullproof-python-safe-markup
    a = Markup(user_html)
    # ruleid: hullproof-python-safe-markup
    return render_template_string(tpl)


def good():
    # ok: hullproof-python-safe-markup
    return Markup("<b>fixed</b>")
