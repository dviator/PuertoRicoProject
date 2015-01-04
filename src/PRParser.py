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
@db_session
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
		self.game = self.initGame()
		self.Players, self.Plantations = self.getPlayers()

	################################################
	# FUNCTION initGame()
	# Initializes the game entity
	def initGame(self):
		FullID = self.data["data"]["data"][0]["channel"]
		ID_index = re.search("\d+",FullID)
		ID = FullID[ID_index.start():]
		# TODO: Add times
		# Number of players will be updated once it is computed
		return Game(gameID = ID, numOfPlayers = 0)

	################################################
	# FUNCTION getNumPlayers()
	# Computes the number of players in a game by analyzing
	# the first governor round
	# Initializes the player/plantation table entries
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
		Players = []
		Plantations = []
		for player_num, player in enumerate(players):
			if len(players) == 2:
				numDubloons = 3
				# Is governor
				if player_num == 0:
					plantation = "indigo"
				else:
					plantation = "corn"
			elif len(players) == 3:
				numDubloons = 2
				if player_num == 0 or player_num == 1:
					plantation = "indigo"
				else:
					plantation = "corn"
			elif len(players) == 4:
				numDubloons = 3
				if player_num == 0 or player_num == 1:
					plantation = "indigo"
				else:
					plantation = "corn"
			# Create necessary entities
			Players.append(Player(gameID = self.game.gameID, playerID = player_num, playerName = player,
								  colonists = 0, victoryPoints = 0, Doubloons = numDubloons))
			Plantations.append(Plantation(ownerID = (self.game.gameID, player_num), plantationID = self.getNextPlantationID(self.game.gameID, player_num),
										  plantationType = plantation, activated = False))
			# Update game to include number of players
			self.game.numOfPlayers = len(players)
		return Players, Plantations

	# end getPlayers
	################################################

	################################################
	# FUNCTION getNextPlantationID(int gameID, int playerID)
	# returns the next plantation ID which should be assigned
	def getNextPlantationID(self, gameID, playerID):
		# Convert this to be a more true "PONY" function
		plants = Plantation.get(ownerID = (gameID, playerID))
		if plants is None:
			return 0
		else:
			return max(plants.plantationID)

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
			# if rol == 'craftsman':
			# 	parseCraftsman(move)
			# elif rol == 'builder':
			# 	parseBuilder(move)
			# elif rol == 'prospector':
			# 	parseProspector(move)
			# elif rol == 'settler':
			# 	parseSettler(move)
			# elif rol == 'mayor':
			# 	parseMayor(move)
		# if there is no role, move does something else (check json keys to figure out)

		# Check move type in conditional

	# end getMove
	################################################

	def parseCraftsman(self, move):
		return ""

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

# Can modify this statement to check the contents of any tables
with db_session:
	Plantation.select().show()
	Player.select().show()