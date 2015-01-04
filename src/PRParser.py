from schemas import *
import sys
import re
import json
from pprint import pprint



#####################################################
# TurnTracker class
# Need to figure out the actual names for this but this is the basic idea for the TurnTracker class
# round - a governor round
# turn - a player turn in a governor round
# action - any granular action
class TurnTracker:

	def __init__(self, num_players):
		# Relative counters (i.e. turn resets to 0 at end of round)
		self.num_players = num_players
		self.round = 0
		self.turn = 0
		self.action = 0

		# Absolute counters
		self.abs_round = 0
		self.abs_turn = 0
		self.abs_action = 0

	def inc_action(self):
		# increment absolute counter
		self.abs_action += 1
		self.action += 1

#	def inc_turn(self):

# end TurnTracker class
#####################################################

#####################################################
# PRParser class
class PRParser:

	#################################################
	# MEMBER VARIABLES
	# 	data - JSON data
	# 	numMoves - total number of moves in the game
	# 	players - list of all players in the game
	#	numPlayers - number of players in the game

	def __init__(self, data):
		self.data = data

	def __init__(self, log_name):
		print("Opening PR JSON log ", log_name, "...")
		json_data = open(log_name)
		print("Parsing PR JSON log ", log_name, "...")
		self.data = json.load(json_data)
		self.numMoves = len(self.data["data"]["data"])
		self.players = self.getPlayers()
		self.numPlayers = len(self.players)
		self.game = self.initGame()

	################################################
	# FUNCTION initGame()
	# Initializes the game entity
	def initGame(self):
		FullID = self.data["data"]["data"][0]["channel"]
		ID_index = re.search("\d+",FullID)
		ID = FullID[ID_index.start():]
		# TODO: Add times
		with db_session:
			return Game(gameID = ID, numOfPlayers = self.numPlayers)

	# FUNCTION getNumPlayers()
	# Computes the number of players in a game by analyzing
	# the first governor round
	def getPlayers(self):
		# loops through the moves, keeping track of each player seen
		# when a player name is repeated, know that that a full governor rotation
		# is completed
		players = []
		for index in range(1, self.numMoves):
			move = self.getMove(index)
			index += 1
			for i in range(0, len(move) - 1):
				if 'player_name' in move[i]["args"]:
					name = move[i]["args"]['player_name']
					if name not in players:
						players.append(move[i]["args"]['player_name'])
		return players

	################################################
	# FUNCTION getMove(int id)
	# Reads a 0-indexed move id and the parsed json data object
	# and returns a json array containing a number of "args" object
	def getMove(self, id):
		return self.data["data"]["data"][id]["data"]

	# end getMove
	################################################

	################################################
	# FUNCTION parseMove(int id)
	# Parses move number <id> and returns a dictionary of ORM entities
	# to be accessed/committed to the database
	def parseMove(self, id):
		move = self.getMove(id)
		# get the role type if there is one in the move
		rol = "None"
		if 'rol_type' in move[0]['args']:
			rol = move[0]['args']['rol_type']
			return self.parseRole(move)
		# if there is no role, move does something else (check json keys to figure out)

		# Check move type in conditional

	# end getMove
	################################################

	################################################
	# FUNCTION parseRole(json move)
	# Parses a move which is defined by a role
	# returns the correct ORM objects
	def parseRole(self, move):
		print(len(move))
		pprint(move[5]['args'])

# End PRParser class
####################################################

#################################################
# Main Code
#

if len(sys.argv) != 2:
	print(sys.argv[0], " requires the name of a PR JSON log")
	sys.exit(1)

# Sample parser instance
parser = PRParser(sys.argv[1])
