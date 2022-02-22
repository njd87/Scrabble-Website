# WHAT IS THE PROJECT
This project is an online application that allows users to play Boggle and save their scores, plus play against others! The program is run using Flask in the "final" directory. Languages used include: HTML, CSS, JavaScript, Python, and Jinja. Boggle, if you don't know, is a game owned by Hasbro Inc. that gives a user a 4x4 grid of randomized letters and asks users to find as many "patterned" words as possible in a give time limit (in this case of online Boggle, this is 2 minutes).

# HOW DO I USE IT
Run Flask in the final directory, using the "flask run" command. This should allow you to run the website (ideally, this would run on an actual server, but I wans't able to get that to work). You should be prompted with a Log In page. If you want, you may Register an account using the "Register" icon in the top right. (Note, sometimes running on a codespace may require multiple tries)

# WHAT TO DO WHEN LOGGED IN
When you Log In, you should be directed to the main page. Here, you have the option to Quickplay or Invite an opponent to play. Additionally, you may use the top navbar to access pending invites, past matches, and high scores.

# QUICKPLAY
In Quickplay, you will see a board! Try to find words connected horizontally, vertically, diagonally, or a combination of both! But be careful: you can't use more than one square! Submitting should award you points if the word exists AND it is present. When the time is up, you will be prompted to save and quit.

# VERSUS
You can input the username of someone you want to face (if you already have a match, it will tell you; you can't verse yourself, and you can't fight opponents that don't exist). The same rules will apply. This will send a pending request to the other user! Check your past matches to see if you won or not!

# LOGOUT
Feel free to logout whenever you're done!

# VIDEO EXAMPLE
https://www.youtube.com/watch?v=yLu6oCvI9LM