import os, csv

from datetime import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

#configure app
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
ALLOWED_EXTENSIONS = {'csv'}
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final_project.db")


#Start of helper functions-----------------------------------------
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


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


#End of helper functions-----------------------------------------


#Start of login/auth-----------------------------------------


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
        return redirect(url_for("index"))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for("index", file="Home"))


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
        return redirect(url_for("index"))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

#End of login/auth-----------------------------------------

#Start of main functions/body-----------------------------------------

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=['GET', 'POST'])
@login_required
def index():

    current_user_id = session["user_id"]

    try:
        NEW_DIR = '/workspaces/116363763/Lecture10/uploads/USER_UPLOAD_BY_SSID-' + str(current_user_id)
        files = os.listdir(NEW_DIR)
    except FileNotFoundError:
        return render_template('index.html', files=False)

    return render_template('index.html', files=files)


@app.route("/files/<file>", methods=['GET', 'POST'])
@login_required
def files(file):

    current_user_id = session["user_id"]
    CURRENT_DIR = '/workspaces/116363763/Lecture10/uploads/USER_UPLOAD_BY_SSID-' + str(current_user_id)

    csv_file = open(f'{CURRENT_DIR}/{str(file)}', mode='r')
    csv_file = csv.reader(csv_file)
    csv_file = [row for row in csv_file]

    return render_template('uploaded_files.html', csv_file=csv_file, file=file)


@app.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    #get variables
    search = request.args.get("search")
    file_name = request.args.get("file_name")
    column = request.args.get("column")
    request_type = request.args.get('request_type')

    #get the list of files
    try:
        current_user_id = session["user_id"]
        NEW_DIR = '/workspaces/116363763/Lecture10/uploads/USER_UPLOAD_BY_SSID-' + str(current_user_id)
        files = os.listdir(NEW_DIR)
    except FileNotFoundError:
        flash('No files loaded. Upload a file before trying to search')
        return redirect("/")

    #get the columns for  the selected file, try and open the file
    try:
        file = open(f'{NEW_DIR}/{str(file_name)}', mode='r')
        csv_reader = csv.reader(file)
        csv_file = []
        for row in csv_reader:
            csv_file.append(row)

    #if there's no file
    except FileNotFoundError:
        if request_type:
            return render_template('searched.html', items=None)

        #i know this is a redundancy, it's just for readability
        else:
            return render_template('search.html', files=files)

    #file is a 2d array
    def search_return(indexes, file, search_term, all):
        return_list = []

        #do this if we're searching through all columns
        if all:
            for i in file:
                for j in i:
                    if search_term in j:
                        return_list.append(j)

        #algorithm for single column
        else:
            for i in file:
                for j in indexes:
                    if search_term in i[j]:
                        return_list.append(i[j])

        return return_list

    #get the columns ready to return
    top_columns = csv_file[:1]
    top_columns = top_columns[0]
    search_results = csv_file[1:]

    #deciding what to send (i.e. what is it updating/loading)
    if request_type == 'update':
        return render_template('file_update.html', columns=top_columns)

    if request_type == 'search':

        #if there's nothing in the search field, check if file_name and column have something in them,
        #and if they don't, render the search field with nothing in it
        if not search:
            if file_name and column:
                pass
            else:
                return render_template('searched.html', items=None)

        #choosing which column to "search for"
        if column.lower() == "all columns":
            chosen_column = [i for i in range(len(top_columns))]
            items = search_return(chosen_column, search_results, search, True)
            return render_template('searched.html', items=items)
        else:
            chosen_column = [top_columns.index(column)]
            items = search_return(chosen_column, search_results, search, False)
            return render_template('searched.html', items=items)

    return render_template('search.html', files=files)


@app.route("/upload_file", methods=['GET', 'POST'])
@login_required
def upload_file():

    if request.method == "POST":

        #make sure there's even a file there
        if 'filename' not in request.files:
            flash('No file part')
            return redirect("/upload_file")

        file = request.files['filename']

        #making sure the user inputs a proper file
        if file.filename == '':
            flash('No selected file')
            return redirect("/upload_file")

        #if the file exists, and make sure the file is the wanted format (.csv)
        if file and allowed_file(file.filename):

            #variables
            current_user_id = session["user_id"]
            NEW_DIR = '/workspaces/116363763/Lecture10/uploads/USER_UPLOAD_BY_SSID-' + str(current_user_id)
            filename = secure_filename(file.filename)
            temp_file = filename.rsplit(".csv")
            app.config['UPLOAD_FOLDER'] = NEW_DIR
            file_ticker = 0

            #if there isn't a folder for this user, create one
            if not os.path.exists(NEW_DIR):
                os.makedirs(NEW_DIR, exist_ok=True)

            #count how many occurences filename has in the list
            for files in os.listdir(NEW_DIR):
                if temp_file[0] in files:
                    file_ticker += 1

            #rename file based on how many occurences there are
            if file_ticker != 0:
                filename = temp_file[0]+str(file_ticker)+".csv"

            try:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('File saved successfully')
            except Exception as e:
                flash('File upload error: ' + str(e))

            return redirect(url_for("index"))


        else:
            flash("Something went wrong with the file upload. Make sure you upload a .csv file")
            return render_template('upload_file.html')

    return render_template('upload_file.html')

#End of main functions/body-----------------------------------------