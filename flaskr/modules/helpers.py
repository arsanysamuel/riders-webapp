import re
from functools import wraps

from flask import render_template, redirect, request, url_for, g, session, Markup

from modules.regex import REGEX


def error(message, code=400, img="https://i.imgur.com/CsCgN7Ll.png"):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("error.html", top=code, bottom=escape(message), img=img), code


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # if "user" not in g or g.user is None:
        if "user" not in session or session["user"] is None:
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

