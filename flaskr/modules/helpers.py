import re
from functools import wraps

from flask import render_template, redirect, request, url_for, g, session, Markup, flash

from modules.regex import REGEX


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # if "user" not in g or g.user is None:
        if "user" not in session or session["user"] is None:
            flash("Must be logged in", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def route_format(s):
    """Formats route segments with Awsome Fonts icons"""
    arabic = re.compile(REGEX["arabic"])
    if len(arabic.findall(s)) > 0:
        print(arabic.findall((s)))
        return Markup(s.replace("|", ' <i class="fa-solid fa-arrow-left"></i> '))
    return Markup(s.replace("|", ' <i class="fa-solid fa-arrow-right"></i> '))

