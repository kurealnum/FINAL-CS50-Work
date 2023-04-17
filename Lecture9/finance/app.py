import os

from datetime import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():

    #variables
    #total_in_shares isn't very descriptive; it's just the total $ value for the shares in that line

    #variables that we use later on
    current_user_id = session["user_id"]

    '''
    iterable information (the stuff that goes in the table)
    also these variables names will be noticeably different because index just tends to have
    completely different variables
    '''
    symbols = db.execute(f"SELECT symbol FROM account_status WHERE user_id = ?", current_user_id)
    names = [lookup(i["symbol"])["name"] for i in symbols]
    shares = db.execute(f"SELECT num_shares FROM account_status WHERE user_id = ?", current_user_id)
    prices = db.execute(f"SELECT price FROM account_status WHERE user_id = ?", current_user_id)
    total_in_shares = [shares[i]["num_shares"]*prices[i]["price"] for i in range(len(symbols))]

    #"final counts" of stuff
    cash = db.execute(f"SELECT cash FROM users WHERE id = ?", current_user_id)
    total = int(cash[0]["cash"])+sum(total_in_shares)

    return render_template("index.html", symbols=symbols, names=names, shares=shares, prices=prices, total_in_shares=total_in_shares, cash=cash, total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    if request.method == "POST":

        #all of the variables
        symbol = lookup(request.form.get("symbol"))

        #failure checks
        if not symbol:
            return apology("must provide symbol/correct symbol", 400)

        #more variables
        current_user_id = session["user_id"]
        cash = db.execute(f"SELECT cash FROM users WHERE id = ?", current_user_id)[0]["cash"]
        num_shares = request.form.get("shares")

        #more failure check
        if not num_shares.isdigit():
            return apology("please enter a digit", 400)

        num_shares = float(num_shares)

        if not num_shares % 1 == 0:
            return apology("please enter a whole number", 400)

        if num_shares < 1:
            return apology("please enter a value greater than 0", 400)

        #we do this calculation later on
        price_of_stock = float(float(symbol["price"])*num_shares)

        if price_of_stock > cash:
            return apology("insufficient funds", 400)

        #actually doing stuff, taking money out of account here
        db.execute(f"UPDATE users SET cash = ? WHERE id = ?", float(cash) - float(price_of_stock), current_user_id)


        #inserting values into the db
        now = datetime.now()

        list_of_symbols = db.execute("SELECT symbol FROM account_status WHERE user_id = ?", current_user_id)

        if not list_of_symbols:
            db.execute(f"INSERT INTO account_status VALUES(?, ?, ?, ?, ?)", current_user_id, symbol["price"], symbol["symbol"], now.strftime("%b-%d-%Y-%H:%M:%S"), (num_shares))

        else:
            for d in list_of_symbols:
                if str(d["symbol"]) == str(symbol["symbol"]):
                    db.execute("UPDATE account_status SET num_shares = num_shares + ? WHERE user_id = ? and symbol = ?", num_shares, current_user_id, symbol["symbol"])
                    break
            else:
                db.execute(f"INSERT INTO account_status VALUES(?, ?, ?, ?, ?)", current_user_id, symbol["price"], symbol["symbol"], now.strftime("%b-%d-%Y-%H:%M:%S"), (num_shares))


        db.execute(f"INSERT INTO purchases VALUES(?, ?, ?, ?, ?)", current_user_id, symbol["price"], symbol["symbol"], now.strftime("%b-%d-%Y-%H:%M:%S"), (num_shares))


        return redirect("/")

    else:
        return render_template('buy.html')


@app.route("/history")
@login_required
def history():

    #main variables
    current_user_id = session["user_id"]

    #db executions
    sales_list = db.execute("SELECT * FROM sales WHERE user_id = ?", current_user_id)
    purchase_list = db.execute("SELECT * FROM purchases WHERE user_id = ?", current_user_id)
    sales_purchase_list = purchase_list + sales_list

    return render_template("history.html", sales_purchase_list=sales_purchase_list)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

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
    if request.method == "POST":

        symbol = lookup(request.form.get("symbol"))

        #failure checks
        if not symbol:
            return apology("must provide symbol/correct symbol", 400)

        return render_template('quoted.html', official_name=symbol["name"], price=symbol["price"], symbol=request.form.get("symbol"))

    else:
        return render_template('quote.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation_password = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

        #ensure confirmation password was submitted
        elif not confirmation_password:
            return apology("must provide confirmation password", 400)

        #ensure username is original
        for i in db.execute("SELECT username FROM users"):
            if str(i["username"]) == str(username):
                return apology("username is already in use", 400)

        #ensure password matches confirmation password
        if confirmation_password != password:
            return apology("password doesn't match confirmation password", 400)

        # Put username into database
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password")))

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    #if sold, take that info out of the account_status table
    if request.method == "POST":

        #variables
        try:
            current_user_id = session["user_id"]
            symbol = request.form['symbol']
            num_shares = request.form.get('shares')
            cash = db.execute(f"SELECT cash FROM users WHERE id = {current_user_id}")[0]["cash"]
        except:
            return apology("please fill out all fields", 400)

        #all the failure checks
        if not db.execute("SELECT ? FROM account_status WHERE user_id = ?", symbol, current_user_id):
            return apology("no shares of that stock are owned", 400)

        try:
            if int(num_shares) < 1:
                return apology("too few shares", 400)
        except:
            return apology("please enter a numerical value", 400)

        if not db.execute("SELECT num_shares FROM account_status WHERE user_id = ? and symbol = ? and num_shares >= ?", current_user_id, symbol, num_shares):
            return apology("too many shares being sold", 400)

        now = datetime.now()


        #all db updates
        db.execute("INSERT INTO sales VALUES(?, ?, ?, ?, ?)", current_user_id, lookup(symbol)["price"], symbol, now.strftime("%b-%d-%Y-%H:%M:%S"), -int(num_shares))
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash + (float(num_shares)*float(lookup(symbol)["price"])), current_user_id)

        #actually "selling" the shares
        shares_owned = db.execute("SELECT num_shares FROM account_status WHERE user_id = ? and symbol = ?", current_user_id, symbol)[0]["num_shares"]
        if int(shares_owned) == int(num_shares):
            db.execute("DELETE FROM account_status WHERE user_id = ? and symbol = ?", current_user_id, symbol)

        else:
            db.execute("UPDATE account_status SET num_shares = num_shares - ? WHERE user_id = ? and symbol = ?", num_shares, current_user_id, symbol)

        return redirect("/")

    else:

        #initial render
        current_user_id = session["user_id"]
        symbols = db.execute(f"SELECT symbol FROM account_status WHERE user_id = ?", current_user_id)

        return render_template("sell.html", symbols=symbols)


