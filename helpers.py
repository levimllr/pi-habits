import requests
import time
import urllib.parse
import unicornhat as unicorn

import unicornhat as unicorn


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

<<<<<<< HEAD
def habit_light(adic):
    unicorn.brightness(0.7)
    unicorn.set_pixel(3, 0, 0, 64, 0)
    unicorn.set_pixel(2, 0, 0, 128, 0)
    unicorn.set_pixel(1, 0, 0, 192, 0)
    unicorn.set_pixel(0, 0, 0, 255, 0)
    unicorn.show()

=======
def unicorn_simple():
    """
    Turns each pixel on in turn and updates the display.
    If you're using a Unicorn HAT and only half the screen lights up,
    edit this example and  change 'unicorn.AUTO' to 'unicorn.HAT' below.
    Ripped from unicorn-hat git repository.
    """

    unicorn.set_layout(unicorn.AUTO)
    unicorn.rotation(0)
    unicorn.brightness(0.5)
    width,height=unicorn.get_shape()

    for y in range(height):
        for x in range(width):
            unicorn.set_pixel(x,y,255,0,255)
            unicorn.show()
            time.sleep(0.05)

    time.sleep(1)
>>>>>>> 80173f125389f241b106979aac5802f1c35cfacb
