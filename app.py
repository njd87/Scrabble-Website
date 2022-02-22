import os

from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from helpers import get_board, login_required, checkWord, getFormattedTime, getKey
from cs50 import SQL
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

# turn this file into a Flask application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies) (From pset9)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# open database
db = SQL("sqlite:///database.db")

# die letters from https://boardgames.stackexchange.com/questions/29264/boggle-what-is-the-dice-configuration-for-boggle-in-various-languages
letters = [
    ["R", "I", "F", "O", "B", "X"],
    ["I", "F", "E", "H", "E", "Y"],
    ["D", "E", "N", "O", "W", "S"],
    ["U", "T", "O", "K", "N", "D"],
    ["H", "M", "S", "R", "A", "O"],
    ["L", "U", "P", "E", "T", "S"],
    ["A", "C", "I", "T", "O", "A"],
    ["Y", "L", "G", "K", "U", "E"],
    ["Qu", "B", "M", "J", "O", "A"],
    ["E", "H", "I", "S", "P", "N"],
    ["V", "E", "T", "I", "G", "N"],
    ["B", "A", "L", "I", "Y", "T"],
    ["E", "Z", "A", "V", "N", "D"],
    ["R", "A", "L", "E", "S", "C"],
    ["U", "W", "I", "L", "R", "G"],
    ["P", "A", "C", "E", "M", "D"]
]
global BOARD
global score
global time
global opponent
global key

@app.route("/")
@login_required
def index():
    return render_template("index.html", singleScores=singleScores, doubleScores=doubleScores)

# from pset9
@app.route("/login", methods = ["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return render_template("error.html", message="Username or password incorrect")

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/")
    return render_template("login.html")

# from pset9
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # get vars
        user, passw, confirmPassw = request.form.get("username"), request.form.get("password"), request.form.get("confirmation")

        # check if passwords are the same
        if passw != confirmPassw:
            return render_template("register.html", color="red", message="Passwords must match")
        # check if username already exists
        elif any((user == userName["username"]) for userName in db.execute("SELECT username FROM users")):
            return render_template("register.html", color="red", message="Username already exists")
        # check if password meets specifications
        elif (len(passw) < 8) or (not any((str(i) in passw) for i in range(11)) or not any(char.isupper() for char in passw)):
            return render_template("register.html", color="red", message="Password must be at least 8 chars, and have least 1 number and 1 capital letter")
        else:
            db.execute("INSERT INTO users (username, password) VALUES(?, ?)", user, generate_password_hash(passw))
            session["user_id"] = db.execute("SELECT user_id FROM users WHERE username = ?", user)[0]["id"]
            return redirect("/")
    return render_template("register.html", color="black", message="Password must be at least 8 chars, and have least 1 number and 1 capital letter")


# loading the game
@app.route("/gameTransfer", methods = ["GET", "POST"])
@login_required
def gameTransfer():
    if request.method == "POST":
        global score
        global time
        global BOARD
        score = 0
        time = getFormattedTime()
        BOARD = get_board(letters)
        return redirect("/game")
    
    return render_template("/")

# loading the game (versus)
@app.route("/gameTransferVersus", methods = ["GET", "POST"])
@login_required
def gameTransferVersus():
    if request.method == "POST":
        # update vars for game
        global score
        global time
        global key
        global BOARD
        score = 0
        time = getFormattedTime()
        BOARD = get_board(letters, key=key)
        return redirect("/versus/loading")
    
    return redirect("/")

# playing the game
@app.route("/game", methods = ["GET", "POST"])
@login_required
def game():
    global BOARD
    return render_template("gameTest.html", board=BOARD, score=score, time=time)

# checking words
@app.route("/game/loading", methods = ["GET", "POST"])
@login_required
def gameCheck():
    global score
    global time
    global BOARD
    if request.method == "POST":
        global score
        global time
        global BOARD
        # get word
        word = request.form.get("word")
        word = word.lower()

        # get points for word and add to score
        pts = checkWord(word, BOARD)
        score += pts

        return render_template("gameTest.html", board=BOARD, score=score, time=time)
    return render_template("gameTest.html", board=BOARD, score=score, time=time)

@app.route("/game/gameOver", methods = ["GET", "POST"])
@login_required
def gameOver():
    if request.method == "POST":
        # get score
        newScore = request.form.get("score")

        # insert into table
        db.execute("INSERT INTO singleScores (user_id, score) VALUES (?, ?)", session["user_id"], newScore)

        # send user back
        return redirect("/")
    return redirect("/")

# starting a game with another person
@app.route("/versus", methods = ["GET", "POST"])
@login_required
def versus():
    if request.method == "POST":
        # get username
        global opponent
        global key
        opponent = request.form.get("username")
        opponentID = db.execute("SELECT user_id FROM users WHERE username = ?", opponent)[0]["user_id"]
        selfUser = db.execute("SELECT username FROM users WHERE user_id = ?", session["user_id"])[0]["username"]
        key = getKey()

        # make sure user exists
        if not db.execute("SELECT * FROM users WHERE username = ?", opponent):
            return render_template("error.html", message="User does not exist")
        # make sure game doesn't already exist
        if db.execute("SELECT * FROM multiMatches WHERE status = ? AND (player1 = ? OR player2 = ?) AND (player1 = ? OR player2 = ?)", "pending", opponentID, opponentID, session["user_id"], session["user_id"]):
            return render_template("error.html", message="You already have a game with this user")
        # make sure user can't send a game if one already exists
        if opponent == selfUser:
            return render_template("error.html", message="You cannot play against yourself")
        return redirect("/gameTransferVersus", code=307)
    elif request.method == "GET":
        return render_template("invite.html")
        
    return render_template("invite.html")
        
# playing versus mode
@app.route("/versus/loading", methods = ["GET", "POST"])
@login_required
def versusCheck():
    global score
    global time
    global opponent
    global BOARD
    if request.method == "POST":
        global score
        global time
        global opponent
        global BOARD
        # get word
        word = request.form.get("word")
        word = word.lower()

        # get points for word and add to score
        pts = checkWord(word, BOARD)
        score += pts

        return render_template("versusGame.html", board=BOARD, score=score, time=time, opponent=opponent)

    return render_template("versusGame.html", board=BOARD, score=score, time=time, opponent=opponent)

# finishing versus mode
@app.route("/versus/gameOver", methods = ["GET", "POST"])
@login_required
def versusGameOver():
    if request.method == "POST":

        global score

        # add score to double score
        db.execute("INSERT INTO doubleScores (user_id, score) VALUES (?, ?)", session["user_id"], score)

        global opponent
        global key
        # get opponent's id
        if db.execute("SELECT user_id FROM users WHERE username = ?", opponent):
            opponentID = db.execute("SELECT user_id FROM users WHERE username = ?", opponent)[0]["user_id"]
        else:
            opponentID = opponent

        # check to see if this is a response or not
        if db.execute("SELECT * FROM multiMatches WHERE (player1 = ? AND player2 = ?) AND status = ?", opponentID, session["user_id"], "pending"):
            # if it is, update accordingly
            db.execute("UPDATE multiMatches SET status = ?, score2 = ? WHERE player1 = ? AND player2= ? AND status = ?", "finished", score, opponentID, session["user_id"], "pending")
        # if not, add to multiMatches
        else:
            db.execute("INSERT INTO multiMatches (player1, player2, status, score1, boardKey) VALUES (?, ?, ?, ?, ?)", session["user_id"], opponentID, "pending", score, key)
        
        return redirect("/")
    return redirect("/")

# display all pending matches

@app.route("/pending", methods = ["GET", "POST"])
@login_required
def pending():
    # get all invites
    invites = db.execute("SELECT * FROM multiMatches WHERE player2 = ? AND status = ? ORDER BY date", session["user_id"], "pending")

    # change all "player1" to the actual username
    for invite in invites:
        invite["player1"] = db.execute("SELECT username FROM users WHERE user_id = ?", invite["player1"])[0]["username"]

    return render_template("pending.html", invites=invites)

# respond to an invite
@app.route("/response", methods = ["GET", "POST"])
@login_required
def response():
    if request.method == "POST":

        # get global vars needed
        global key
        global opponent

        # get game info
        id = request.form.get("id")
        info = db.execute("SELECT * FROM multiMatches WHERE id = ?", id)

        key = info[0]["boardKey"]
        opponent = db.execute("SELECT username FROM users WHERE user_id = ?", info[0]["player1"])[0]["username"]

        return redirect("/gameTransferVersus", code=307)
    return redirect("/")

# show past matches
@app.route("/history", methods = ["GET", "POST"])
@login_required
def history():
    # get list of matches
    matches = db.execute("SELECT * FROM multiMatches WHERE (player1 = ? OR player2 = ?) AND status = ? ORDER BY date", session["user_id"], session["user_id"], "finished")

    # organize the matches
    for match in matches:
        # assign opponent
        if match["player1"] == session["user_id"]:
            # user is player1
            match["opponent"] = db.execute("SELECT username FROM users WHERE user_id = ?", match["player2"])[0]["username"]
            if match["score1"] > match["score2"]:
                match["outcome"] = "Win"
            elif match["score2"] > match["score1"]:
                match["outcome"] = "Loss"
            else:
                match["outcome"] = "Tie"
        else:
            # user is player2
            match["opponent"] = db.execute("SELECT username FROM users WHERE user_id = ?", match["player1"])[0]["username"]
            if match["score1"] > match["score2"]:
                match["outcome"] = "Loss"
            elif match["score2"] > match["score1"]:
                match["outcome"] = "Win"
            else:
                match["outcome"] = "Tie"
        
    return render_template("history.html", matches=matches)

# show scores for single player
@app.route("/singleScores", methods = ["GET", "POST"])
@login_required
def singleScores():
    # get list of scores

    singleScores = db.execute("SELECT score, date FROM singleScores WHERE user_id = ? ORDER BY score DESC", session["user_id"])

    return render_template("singleScores.html", scores=singleScores)

# show scores for multi player
@app.route("/doubleScores", methods = ["GET", "POST"])
@login_required
def doubleScores():
    # get list of scores

    doubleScores = db.execute("SELECT score, date FROM doubleScores WHERE user_id = ? ORDER BY score DESC", session["user_id"])

    return render_template("doubleScores.html", scores=doubleScores)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
