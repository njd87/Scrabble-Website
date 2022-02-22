import random
from flask import session, redirect
from functools import wraps
from nltk.corpus import words
import datetime
from copy import copy, deepcopy

used_words = []
dictionary = words.words()

for i in range(len(dictionary)):
    dictionary[i] = dictionary[i].lower()


# from pset9
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

# get a key for randominzation
def getKey(size=4):
	key = ""

	# get initial value
	key = key + str(random.randint(0,9))

	# random values for each dice
	for i in range(size ** 2):
		key = key + str(random.randint(0,5))
	
	return key


# make the board, return a 2D list
def get_board(dice, size=4, key=None):
	used_words.clear()
	usableDice = deepcopy(dice)
	if key == None:
		random.shuffle(usableDice)
		board = []
		# go through all dice
		for i in range(size):
			board.append([])
		for i in range(size ** 2):
			# create board
			board[i % 4].append(usableDice[i][random.randint(0,5)])
		return board
	else:
		key = str(key)
		def tmp():
			return float("0." + key[0])
		random.shuffle(usableDice, tmp)
		board = []
		# go through all dice
		for i in range(size):
			board.append([])
		for i in range(size ** 2):
			# create board
			board[i % 4].append(usableDice[i][int(key[i+1])])
		return board


# check to make sure word is a real word, is at least 3 letters, and not already used
# if so, find if a pattern exists
# if it does, assigns points

def checkWord(word, board):
	if len(word) >= 3 and word in dictionary and word not in used_words:
		if checkPattern(word.upper(), board):
			used_words.append(word)
			if len(word) == 3 or len(word) == 4:
				return 1
			elif len(word) == 5:
				return 2
			elif len(word) == 6:
				return 3
			elif len(word) == 7:
				return 5
			elif len(word) >= 8:
				return 11
	return 0

# return true if word pattern is present
def checkPattern(word, board, starting = None):
	# see if you are returning
	if starting != None:

		# if this is the last time here, you're good!
		if len(word) == 1:
			return True

		# get continuations
		cPositions = getNearbyPositions(starting[0], starting[1], board, word[1])
		results = []

		# if there's no place to go, return false
		if not cPositions:
			return False

		# now, re-run the algorithm for each possible pattern
		for (x2,y2) in cPositions:
			results.append(checkPattern(word[1:], blockBoard(starting[0],starting[1],board), (x2,y2)))

		# return results
		return any(results)

	# first time here
	else:
		# get possible starting positions
		sPositions = findPlaces(word[0], board)

		# create some empty lists
		cPositions = []
		results = []

		# check to see which of the starting positions
		# leads to the next letter
		for (x,y) in sPositions:
			if word[1] in getSurrounding(x, y, board):
				cPositions.append((x,y))

		# if there's no place to go, return false
		if not cPositions:
			return False

		# now, re-run the algorithm for each possible pattern
		for (x,y) in cPositions:
			for (x2,y2) in getNearbyPositions(x, y, board, word[1]):
				results.append(checkPattern(word[1:], blockBoard(x,y,board), (x2,y2)))

		# return results
		return any(results)


	

# get surrounding letters of a given position
def getSurrounding(row, element, board):
	surroundings = []
	size = len(board[0])
    # check in downard direction
	if row + 1 < size:
		surroundings.append(board[row+1][element])
        # check right
		if element + 1 < size:
			surroundings.append(board[row][element + 1])
			surroundings.append(board[row + 1][element + 1])
        # check left
		if element - 1 >= 0:
			surroundings.append(board[row][element - 1])
			surroundings.append(board[row + 1][element - 1])
    # check in upward direction
	if row - 1 >= 0:
		surroundings.append(board[row - 1][element])
        # check right
		if element + 1 < size:
			surroundings.append(board[row][element + 1])
			surroundings.append(board[row - 1][element + 1])
        # check left
		if element - 1 >= 0:
			surroundings.append(board[row][element - 1])
			surroundings.append(board[row - 1][element - 1])

	return surroundings

# get positions of adjascent letters from word (NOTE: THIS IS THE SAME ALGORITHM FROM getSurrounding)
def getNearbyPositions(row, element, board, letter):
	positions = []
	size = len(board[0])
	if row + 1 < size:
		if board[row + 1][element] == letter:
			positions.append((row+1,element))
		if element + 1 < size:
			if board[row][element + 1] == letter:
				positions.append((row,element + 1))
			if board[row + 1][element + 1] == letter:
				positions.append((row + 1,element + 1))
		if element - 1 >= 0:
			if board[row][element - 1] == letter:
				positions.append((row,element - 1))
			if board[row + 1][element - 1] == letter:
				positions.append((row + 1,element - 1))
	if row - 1 >= 0:
		if board[row - 1][element] == letter:
			positions.append((row - 1,element))
		if element + 1 < size:
			if board[row][element + 1] == letter:
				positions.append((row, element + 1))
			if board[row - 1][element +1] == letter:
				positions.append((row - 1,element + 1))
		if element - 1 >= 0:
			if board[row][element - 1] == letter:
				positions.append((row,element - 1))
			if board[row - 1][element - 1] == letter:
				positions.append((row - 1,element - 1))

	return positions

# creates a new board without the given position
def blockBoard(row, element, board):
    # create temp board
	newBoard = deepcopy(board)

    # get rid of nonneeded position
	newBoard[row][element] = 1

    # return board
	return newBoard

# return location of letter in tuple form
def findPlaces(letter, board):
	positions = []
    # cycle through positions
	for row in range(len(board[0])):
		for position in range(len(board[0])):
            # if letter is there, add to positions
			if board[row][position] == letter:
				positions.append((row, position))
    
    # return positions
	return positions

# get formatted time for javascript timer
def getFormattedTime(time = 2.05):
	# get timer for 2 minutes
	unformattedTime = datetime.datetime.now() + datetime.timedelta(minutes=(-300 + time))
	# (mmm d, yyyy hr:mn:sc)

	return (unformattedTime.strftime("%B"))[:3] + " " + str(unformattedTime.day) + ", " + str(unformattedTime.year) + " " + str(unformattedTime.hour) + ":" + str(unformattedTime.minute) + ":" + str(unformattedTime.second)