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
class TimeTracker:

	def __init__(self, num_players):

		self.num_players = num_players
		# Ticks up on every distinct game action/subsequent db write
		self.eventNum = 0
		# Cycles once each new governor round
		self.roundNum = 0
		# Cycles once each new role phase
		self.phaseNum = 0
		# Cycles once each new player turn within a role
		self.turnNum = 0

	# Increments the phase and if necessary increments the round
	def inc_phase(self):
		self.phaseNum += 1
		if self.phaseNum % self.num_players == 0:
			self.roundNum += 1

# end TurnTracker class
#####################################################

#####################################################
# PRParser class

@db_session
class PRParser:

	#################################################
	# MEMBER VARIABLES
	# This description needs to be updated
	# 	data - JSON data
	# 	totalTurns - total number of moves in the game
	# 	players - list of all players in the game
	#	numPlayers - number of players in the game

	def __init__(self, log_name):
		print("Opening PR JSON log ", log_name, "...")
		json_data = open(log_name)
		print("Parsing PR JSON log ", log_name, "...")
		self.data = json.load(json_data)
		self.totalTurns = len(self.data["data"]["data"])
		self.game = self.initGame()
		self.Players, self.Plantations = self.getPlayers()
		self.active_player = None
		# Parse all turns
		# skip set-up turn
		self.timeTrack = TimeTracker(len(self.Players))

		self.currentMove = 1
		while self.currentMove < self.totalTurns:
			self.parseMove(self.currentMove)
			self.timeTrack.inc_phase()
			self.currentMove += 1

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
		for index in range(1, self.totalTurns):
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
	# FUNCTION getCurrentMove
	# Gets the move pointed to by currentMove
	def getCurrentMove(self):
		return self.getMove(self.currentMove)

	# end getCurrentMove
	################################################

	################################################
	# FUNCTION parseMove(int id)
	# Parses move number <id> and returns a dictionary of ORM entities
	# to be accessed/committed to the database
	def parseMove(self, id):
		move = self.getMove(id)
		# get the role type if there is one in the move
		if 'rol_type' in move[0]['args']:
			rol = move[0]['args']['rol_type']
			active_player = move[0]['args']['player_name']
			print(active_player + " selected " + rol)
			if rol == 'craftsman':
				self.parseCraftsman(move)
			elif rol == 'builder':
				self.parseBuilder(move)
			elif rol == 'prospector':
				self.parseProspector(move)
			elif rol == 'settler':
				self.parseSettler(move)
			elif rol == 'mayor':
				self.parseMayor(move)
			elif rol == 'captain':
				self.parseCaptain(move)
			elif rol == 'trader':
				self.parseTrader(move)
		# this should be unreachable
		# all action between role actions should be parsed by that roles parse function
		#else:
			#print("No Role for move " + str(id))
	# end getMove
	################################################

	################################################
	# FUNCTION isAction(str args, str action)
	# Checks if the current move arg is the specified action
	def isAction(self, args, action):
		if 'action' in args and args['action'] == action:
			return True
		else:
			return False

	# END FUNCTION isAction
	################################################

	################################################
	# FUNCTION incMoveIndex(int moveIndex, str move)
	# increments the move index and returns the new
	# tuple (move, moveIndex)
	def incMoveIndex(self, move, moveIndex):
		if moveIndex < len(move)-1:
			moveIndex += 1
		else:
			self.currentMove += 1
			move = self.getCurrentMove()
			moveIndex = 0
		return move, moveIndex

	# END FUNCTION incMoveIndex
	################################################

	################################################
	# Role Parsing Functions

	def parseCraftsman(self, move):
		moveIndex = 0
		privilege = 'no'
		while not self.isAction(move[moveIndex]['args'], 'stNextPlayerForRoleSelection'):
			if 'res_type' in move[moveIndex]['args']:
				numRes = move[moveIndex]['args']['delta']
				resType = move[moveIndex]['args']['res_type']
				activePlayer = move[moveIndex]['args']['player_name']
				print(activePlayer + " produced " + str(numRes) + " " + resType + ". privilege? " +privilege)
			elif self.isAction(move[moveIndex]['args'], 'stPlayerCraftsmanPrivilege'):
				privilege = 'yes'
			if 'type' in move[moveIndex]:
				if move[moveIndex]['type'] == 'doubloonsEarned':
					doubloons = move[moveIndex]['args']['delta']
					activePlayer = move[moveIndex]['args']['player_name']
					if 'factory' in move[moveIndex]['log']:
						print(activePlayer + " earned " + str(doubloons) + " doubloons from his factory")
					else:
						print(activePlayer + " earned " + str(doubloons) + " doubloons from the craftsman")
			move, moveIndex = self.incMoveIndex(move, moveIndex)
		return ""

	# TODO : Add in University action handling
	def parseBuilder(self, move):
		moveIndex = 0
		while not self.isAction(move[moveIndex]['args'], 'stNextPlayerForRoleSelection'):
			if 'bld_type_tr' in move[moveIndex]['args']:
				bld_type = move[moveIndex]['args']['bld_type_tr']
				cost = move[moveIndex]['args']['cost']
				score_delta = move[moveIndex]['args']['score_delta']
				activePlayer = move[moveIndex]['args']['player_name']
				print(activePlayer + " built " + bld_type + " for " + str(cost) + " doubloon, gaining " + score_delta + " victory points")
			if 'type' in move[moveIndex]:
				if move[moveIndex]['type'] == 'doubloonsEarned':
					doubloons = move[moveIndex]['args']['delta']
					activePlayer = move[moveIndex]['args']['player_name']
					print(activePlayer + " earned " + str(doubloons) + " doubloons from the builder")
			move, moveIndex = self.incMoveIndex(move, moveIndex)
		return ""

	def parseProspector(self, move):
		moveIndex = 0
		while not self.isAction(move[moveIndex]['args'], 'stNextPlayerForRoleSelection'):
			if 'type' in move[moveIndex]:
				if move[moveIndex]['type'] == 'doubloonsEarned':
					doubloons = move[moveIndex]['args']['delta']
					activePlayer = move[moveIndex]['args']['player_name']
					print(activePlayer + " earned " + str(doubloons) + " doubloons from the prospector.")
			move, moveIndex = self.incMoveIndex(move, moveIndex)
		return ""

	def parseSettler(self, move):
		return ""

	def parseMayor(self, move):
		return ""

	def parseCaptain(self, move):
		return ""

	def parseTrader(self, move):
		return ""

	# END Role Parsing Functions
	##################################################
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
#with db_session:
	# .show() does a nice pretty print of whatever the contents
	# of that query object is
	#Plantation.select().show()
	#Player.select().show()