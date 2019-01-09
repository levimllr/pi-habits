import os
import re
import stat
import threading
import time
import calendar

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from sys import exit
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

import unicornhat as unicorn

from helpers import apology, login_required, habit_light

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:////home/pi/PiHabits/pi-habits/habits.db")

@app.route("/")
@login_required
def index():
    """Show habit heatmaps"""

    userrows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=session["user_id"])
    username = userrows[0]['username']

    activityrows = db.execute("SELECT * FROM activity WHERE userid = :userid", userid=session["user_id"])

    print(activityrows)

    activity_dict = {}
    for i in activityrows:
        activity_dict[str(i["time"])] = i["howmuch"]
    print(activity_dict)
    
    habit_light(activityrows)

    jsactivity = jsonify(activity_dict)
    print(jsactivity)
	
    return render_template("index.html", username=username, activity_dict=activity_dict)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add habits to track"""

    if request.method == "POST":

        habit = request.form.get("habit")
        frequency = int(request.form.get("howmuch"))
        print(habit)
        print(frequency)

        db.execute("INSERT INTO habits (userid, habit, frequency) VALUES (:userid, :habit, :frequency)",
                       userid=session["user_id"], habit=habit, frequency=frequency)

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("add.html")

@app.route("/remove", methods=["GET", "POST"])
@login_required
def remove():
    """Remove habits"""

    if request.method == "POST":

        habit = request.form.get("habit")

        db.execute("DELETE FROM habits WHERE userid = :user_id AND habit = :habit", user_id=session["user_id"], habit=habit)

        # Redirect user to home page
        return redirect("/")

    else:
        habits = db.execute("SELECT * FROM habits WHERE userid = :user_id", user_id=session["user_id"])
        print(habits)
        return render_template("remove.html", habits=habits)

@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    """Update habits"""

    if request.method == "POST":

        habitinfo = db.execute("SELECT * FROM habits WHERE userid = :user_id", user_id=session["user_id"])
        habit = habitinfo[0]["habit"]

        howmuch = int(request.form.get("howmuch"))
        print(howmuch)

        now = int(time.time())
        print(time)

        db.execute("INSERT INTO activity (userid, habit, howmuch, time) VALUES (:userid, :habit, :howmuch, :time)",
                userid=session["user_id"], habit=habit, howmuch=howmuch, time=now)

        # Redirect user to home page
        return redirect("/")

    else:
        habits = db.execute("SELECT * FROM habits WHERE userid = :user_id", user_id=session["user_id"])
        print(habits)
        return render_template("update.html", habits=habits)

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    userrows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=session["user_id"])
    portfolio = db.execute("SELECT * FROM transactions WHERE who = :user_id", user_id=session["user_id"])
    # print(portfolio)

    for i in range(0, len(portfolio)):
        if portfolio[i]["howmany"] < 0:
            portfolio[i]["type"] = "Sold"
        else:
            portfolio[i]["type"] = "Bought"

    # print(portfolio)

    return render_template("history.html", portfolio=portfolio)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        #
        symbol = lookup(request.form.get("symbol"))

        # Ensure stock ticker symbol was submitted
        if not request.form.get("symbol") or symbol == None:
            return apology("must provide valid stock ticker symbol", 400)

        # Redirect user to quoted page
        return render_template("quoted.html", symbol=symbol)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure passwords match.
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must match", 400)

        # Encrypt/hash password.
        hash = generate_password_hash(request.form.get("password"))

        # Insert username and hashed password into database.
        result = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                            username=request.form.get("username"), hash=hash)

        # If the username already exists...
        if not result:
            return apology("username already exists", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = result

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
