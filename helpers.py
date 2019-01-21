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
    """
    Activate NEOpixels (individual pixels of UnicornHAT) according to habit activity.
    """
    # First, turn odff all pixels in case of previous program using the UnicornHAT.
    unicorn.off()
    # Half the brightness of the UnicornHAT (1.0 is blindingly bright)!
    unicorn.brightness(0.5)
    # What follows is a constant that converts UTC time to PST. Keep in mind that 
    utctopstsec = 28800
    # Classic print statements for troubleshooting!
    # print(len(adic))
    # print(adic[0]["time"])
	
    # Create an empty list to convert activity from SQL database.
    habitgrid = []

    # This loop appends a sublist to habitgrid consisting of the week number (first week of the year = 1), 
    # day number (Sunday = 1), and light intensity proportional to the day's actual activity divided by the daily goal.
    for i in adic:
        print(i)
        habitgrid.append([int(datetime.utcfromtimestamp(i["time"]-utctopstsec).strftime('%U')), int(datetime.utcfromtimestamp(i["time"]-utctopstsec).strftime('%w')), int(165*i["howmuch"]/most+90)])

    # print(habitgrid)

    # The following loop uses values from the habitgrid and implements them with the unicorn's set_pixel function in a way...
    # that will look good with the RPi's orientation. Unfortunately, pixel 7,7 is at the top-left in this design. 
    for j in habitgrid:
        print(j)
        if j[2] > 255:
            j[2] = 255
            # Note the lsat three numbers in the tuple. The penultimate entry sets the color to green, but this option...
            # could easily be changed. 
            # A reminder: set_pixel(x, y, R, G, B).
            unicorn.set_pixel(abs(j[0]-7), abs(j[1]-7), 0, j[2], 0)
    
    # This loop allows for a light in the bottom-most row to turn on when a week's worth of activity has occurred!
    # By the default the streak variable is set to one. If any day in a column lacks activity, streak = 0.
    # The bottom-most light of a week column lights up white when streak remains 1.
    for k in range(0,8):
        streak = 1
        for l in range(1,8):
            print(unicorn.get_pixel(k, l) == (0, 0, 0))
            if unicorn.get_pixel(k, l) == (0, 0, 0):
                streak = 0
        if streak == 1:
            unicorn.set_pixel(k, 0, 255, 255, 255)
    
    # Turn it up!
    unicorn.show()
