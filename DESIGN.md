# OVERALL DESIGN
I wanted to use a very minimalistic design for this website, similar to what was used for pset9. The login and register code, as such, were used in this pset. But that's where the similarities end. The homepage is meant for interaction: it lets the users pick a mode or go to their history, scores, or pending requests. Flask made the transition from each page to the next easier, especially since user-specific data is required for most pages. I'll run through the different aspects of this project in detail.

Feel free to use any of my "de-bugging" accounts while the application is running:

username: nick
password: 123

username: nick2
password: 123

username: nick3
password: Test1234

# DATABASE
I have four main tables in my database:
    users (keeps track of the users and their passwords)
    multiMatches (keeps track of sent, pending, and finished matches)
    singleScores (keeps track of a user's scores in singleplayer)
    doubleScores (keeps track of a user's scores in multiplayer)

Keeping this data in 4 separate tables helped immensely when it came time for implementation in app.py. Keeping users separate is straight forward, but it may not seem obvious why keeping the scores separate would help. Loading history and high scores were much easier because all of these were kept separate, so a simple one-line was all I needed.

# THE GAME
This is where most of my troubles lay during the coding process. Until the very end, the board looked almost laughable, being apart of a quick HTML table I put together in 30 seconds, simply because I never got the game to work to the point where I could focus on front-end stuff. Here's the rundown:

1) Setting Up The Board
    Using information from online, I was able to obtain all 16 dice used in the game. I wrote them into a 2D LIST and developed a function called get_board to randomly assign the dice to different locations and then "roll" them by using the random python library. From there, just a jinja for loop was enough to get the board all set up.

2) Interpreting The Answers
    Getting word responses from the user was very simple (just a POST request was enough). However, seeing which answers were correct is a different story. It's easy for a human to see that a pattern exists, but for a machine, a recursive function had to be used. This function, checkWord, first makes sure the word submitted is long enough AND is a word in the English dictionary. Then, a different function called checkPattern is called (which is recursive) that goes through each letter of the submitted word and creates a new board, without that letter, and does the same for the rest (this also takes into account when there are multiple letters). If this returns true, points are awarded based on length.

3) Timer
    The timer was implemented using JavaScript. However, because words are submitted on POST requests, the same variable for ending time had to be used. So, I developed a function in python using datetime called getFormattedTime that formats the time to JavaScript two minutes from when the game starts.

4) Fairness in Multiplayer
    Of course, to make multiplayer fair, the same board should be used. However, since the board is randomized, I implemented a pseudorandom algorithm using a set "key" to make sure that multiplayer matches between 2 people use the same board (this key is stored in "multiMatches")

# FINAL NOTES
Some final things I want to add: my project changed slightly from my initial proposal. In particular, there is no "difficulty" setting (the code in helpers.py is all set for different sizes, but right now just runs on default), as its implementation casued some very weird boards (since Boggle doesn't have 25 dice!). In addition, I got rid of practice mode, just because I thought it didn't make sense: why have a practice mode on a game that's quickplay and is based on using different boards?

It's actually pretty interesting: on the proposal, I had invites as something I thought couldn't get done, but in reality, it was a focal point of my programming.