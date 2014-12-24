from pony.orm import *
import sys
import json
from pprint import pprint


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
		self.players = self.getNumPlayers()
		self.numPlayers = len(self.players)

	################################################
	# FUNCTION getNumPlayers()
	# Computes the number of players in a game by analyzing
	# the first governor round
	def getNumPlayers(self):
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
	# Reads a 1-indexed move id and the parsed json data object
	# and returns a json array containing a number of "args" object
	def getMove(self, id):
		return self.data["data"]["data"][id - 1]["data"]

	# end getMove
	################################################

	################################################
	# FUNCTION parseMove(int id)
	# Parses move number <id> and returns a dictionary of ORM entities
	# to be accessed/committed to the database
	def parseMove(self, id):
		move = self.getMove(id)
	# Check move type in conditional

	# end getMove
	################################################


# End PRParser class
####################################################

#################################################
# Main Code
#
db = Database('sqlite', ':memory:')
if len(sys.argv) != 2:
	print(sys.argv[0], " requires the name of a PR JSON log")
	sys.exit(1)

# Sample parser instance
parser = PRParser(sys.argv[1])
for i in range(1, parser.numMoves):
	parser.getMoveRole(i)