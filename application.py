import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

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
db = SQL("sqlite:///habits.db")


@app.route("/")
@login_required
def index():
    """Show habit heatmaps"""

    userrows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=session["user_id"])
    portfolio = db.execute(
        "SELECT what, SUM(howmany) AS allhowmany FROM transactions WHERE who = :user_id GROUP BY what", user_id=session["user_id"])
    # print(portfolio[0].get('what'))

    totalvalue = 0

    for i in range(0, len(portfolio)):
        ticker = portfolio[i].get('what')
        # print(ticker)
        symbol = lookup(ticker)
        # print(symbol)
        currentprice = symbol["price"]
        portfolio[i]["price"] = usd(currentprice)
        portfolio[i]["total"] = usd(portfolio[i]["allhowmany"] * currentprice)
        totalvalue += portfolio[i]["allhowmany"] * currentprice

    trace = 0
    for j in portfolio:
        if j["allhowmany"] == 0:
            del portfolio[trace]
        trace += 1

    currentcash = userrows[0]["cash"]
    stocktotal = totalvalue
    totalvalue += currentcash

    # print(currentcash)

    return render_template("index.html", currentcash=usd(currentcash), portfolio=portfolio, totalvalue=usd(totalvalue), stocktotal=usd(stocktotal))
    # return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":

        try:
            symbol = lookup(request.form.get("symbol"))
            name = symbol["name"]
            ticker = symbol["symbol"]
            price = symbol["price"]
        except:
            return apology("must provide valid stock ticker symbol", 400)

        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("must provide valid number of shares", 400)

        if not symbol or symbol == None:
            return apology("must provide valid stock ticker symbol", 400)
        if shares <= 0:
            return apology("must provide valid number of shares", 400)

        cost = price * shares
        # print(symbol)
        # print(ticker)
        # print(shares)
        # print(cost)

        # Ensure stock ticker symbol was submitted.
        # if not symbol or symbol == None:
        #    return apology("must provide valid stock ticker symbol", 400)

        # Ensure valid number of shares was submitted.
        # if not shares or shares <= 0 or not isinstance(shares, int):
        #    return apology("must provide valid number of shares", 400)

        # Get the user's cash.
        rows = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])
        cash = rows[0]["cash"]
        # print(cash)

        remainder = round(cash - cost, 2)

        # Ensure the user can afford the stock.
        if remainder > 0:
            db.execute("UPDATE users SET cash = :remainder WHERE id = :user_id", remainder=remainder, user_id=session["user_id"])
            db.execute("INSERT INTO transactions (who, what, howmany, whatprice) VALUES (:who, :what, :howmany, :whatprice)",
                       who=session["user_id"], what=ticker, howmany=shares, whatprice=price)
        else:
            return apology("you broke as hell")

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("buy.html")


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


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "POST":

        symbol = lookup(request.form.get("symbol"))
        name = symbol["name"]
        ticker = symbol["symbol"]
        price = symbol["price"]
        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("must provide valid number of shares", 400)

        if shares <= 0:
            return apology("must provide valid number of shares", 400)

        sale = price * shares

        # Ensure stock ticker symbol was submitted.
        if not symbol or symbol == None:
            return apology("must provide valid stock ticker symbol", 400)

        # Get the user's shares.
        usershares = db.execute(
            "SELECT SUM(howmany) AS allhowmany FROM transactions WHERE who = :user_id and what = :what GROUP BY what", user_id=session["user_id"], what=ticker)
        presentshares = usershares[0]["allhowmany"]
        # print(presentshares)
        # print(shares)

        if presentshares < shares:
            return apology("try selling fewer shares", 400)

        # Get the user's cash.
        rows = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])
        cash = rows[0]["cash"]

        # Figure the user's new balance.
        newbalance = round(cash + sale, 2)

        # Update the user's account.
        db.execute("UPDATE users SET cash = :newbalance WHERE id = :user_id", newbalance=newbalance, user_id=session["user_id"])
        db.execute("INSERT INTO transactions (who, what, howmany, whatprice) VALUES (:who, :what, :howmany, :whatprice)",
                   who=session["user_id"], what=ticker, howmany=-shares, whatprice=price)

        # Redirect user to home page
        return redirect("/")

    else:
        portfolio = db.execute(
            "SELECT what, SUM(howmany) AS allhowmany FROM transactions WHERE who = :user_id GROUP BY what", user_id=session["user_id"])
        return render_template("sell.html", portfolio=portfolio)


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
