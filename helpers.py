import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session, url_for
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/auth")
        return f(*args, **kwargs)
    return decorated_function