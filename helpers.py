import requests
import time
import urllib.parse
import unicornhat as unicorn

from datetime import datetime
from flask import redirect, render_template, request, session
from functools import wraps
from random import randint


def apology(message, code=400):
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
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def habit_light(adic, most):
	unicorn.off()
	unicorn.brightness(0.5)
	utctopstsec = 28800
	print(len(adic))
	print(adic[0]["time"])
	habitgrid = []
	
	for i in adic:
		print(i)
		habitgrid.append([int(datetime.utcfromtimestamp(i["time"]-utctopstsec).strftime('%W')), int(datetime.utcfromtimestamp(i["time"]-utctopstsec).strftime('%w')), int(165*i["howmuch"]/most+90)])
	
	print(habitgrid)
	
	for j in habitgrid:
		print(j)
		if j[2] > 255:
			j[2] = 255
		unicorn.set_pixel(abs(j[0]-7), abs(j[1]-7), 0, j[2], 0)
    
	unicorn.show()
