from schemas import *
import sys
import re
import json
import logging



#####################################################
# TurnTracker class
# Need to figure out the actual names for this but this is the basic idea for the TurnTracker class
# round - a governor round
# turn - a player turn in a governor round
# action - any granular action
class TimeTracker:

	def __init__(self):

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

	def inc_turn(self):
		self.turnNum += 1

	def inc_event(self):
		self.eventNum += 1

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
		# Initialize Logger
		Logger = logging.getLogger()
		Logger.setLevel("INFO")

		logging.debug("Opening PR JSON log "+ log_name + "...")
		json_data = open(log_name)
		logging.debug("Parsing PR JSON log " +log_name + "...")
		self.data = json.load(json_data)
		#Is the following line accurate?
		self.totalTurns = len(self.data["data"]["data"])
		logging.debug("Total turns = " +str(self.totalTurns))
		self.initGame()
		self.active_player = None
		# Parse all turns
		# skip set-up turn
		#self.timeTrack = TimeTracker()

		self.currentMove = 1
		while self.currentMove < self.totalTurns:
			self.parseMove(self.currentMove)
			#self.timeTrack.inc_phase()
			self.currentMove += 1

	################################################
	# FUNCTION initGame()
	# Initializes the game entity

	def initGame(self):
		FullID = self.data["data"]["data"][0]["channel"]
		ID_index = re.search("\d+",FullID)
		gameID = FullID[ID_index.start():]
		# TODO: Add times
	# Computes the number of players in a game by analyzing
	# the first governor round
	# Initializes the player/plantation table entries
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
		#Initialize the game entity now that we know the number of players in the game. 
		Game(gameID = gameID, numOfPlayers = len(players))

		#Set the correct starting plantations and doubloons for each party and initializes
		#the player entries. 
		Players = []
		Plantations = []
		# Plantation ID for starting plantations determined as follows (pretty sure, needs to be confirmed with different player_nums):
		# 	Corn is 1-index and goes from 1 -> num_corn in the game. Then indigo ranges num_corn -> num_indigo
		# 	So, the first corn would be pla_id : 1, second corn would be pla_id : 2, and so on.
		for player_num, player in enumerate(players):
			if len(players) == 2:
				numDoubloons = 3
				# Is governor
				if player_num == 0:
					plantationType = "indigo"
					plantationID = 8
				elif player_num == 1:
					plantationType = "corn"
					plantationID = 1
			elif len(players) == 3:
				numDoubloons = 2
				if player_num == 0:
					plantationType = "indigo"
					plantationID = 11
				elif player_num == 1:
					plantationType = "indigo"
					plantationID = 12
				elif player_num == 2:
					plantationType = "corn"
					plantationID = 1
			elif len(players) == 4:
				numDoubloons = 3
				if player_num == 0:
					plantationType = "indigo"
					plantationID = 11
				elif player_num == 1:
					plantationType = "indigo"
					plantationID = 12
				elif player_num == 2:
					plantationType = "corn"
					plantationID = 1
				elif player_num == 3:
					plantationType == "corn"
					plantationID = 2
			elif len(players) == 5:
				numDoubloons = 4
				if player_num == 0:
					plantationType = "indigo"
					plantationID = 11
				elif player_num == 1:
					plantationType = "indigo"
					plantationID = 12
				elif player_num == 2:
					plantationType = "indigo"
					plantationID = 13
				elif player_num == 3:
					plantationType = "corn"
					plantationID = 1
				elif player_num == 5:
					plantationType = "corn"
					plantationID = 2

			self.game = Game[gameID]
			if self.game.gameVariant == "Balanced":
				if plantationType == "corn":
					numDoubloons -= 1

			print(str(player_num) + ", " + player + ", " + str(plantationID) + ", " + plantationType)
			Player(gameID = gameID, playerID = player_num, playerName = player, Doubloons = numDoubloons)
			Plantation(ownerID = (gameID, player_num), plantationID = plantationID,
										  plantationType = plantationType)
			# Update game to include number of players
			
			######################################################################
			#I think it may be easier to think of player position in terms of ABCD
			#rather than 1234. Not going to spend time implementing it now but 
			#putting this here as a placeholder for the concept.
			#if player_num == 0:
				#player_position == "A"
			#################################################################
			# Create necessary entities
			

	# end getPlayers
	################################################

	################################################
	# FUNCTION getNextPlantationID(int gameID, int playerID)
	# returns the next plantation ID which should be assigned
	#
	# This function is probably unecessary - we should probably use the
	# plantation ID that BGA specifies in the doc
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
			logging.debug(active_player + " selected " + rol)
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
			#logging.debug("No Role for move " + str(id))
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
	# FUNCTION doubloonsEarned(move, moveIndex)
	# checks if coins were earned by a particular move
	def doubloonsEarned(self, move, moveIndex, role):
		if 'type' in move[moveIndex]:
			if move[moveIndex]['type'] == 'doubloonsEarned':
				doubloons = move[moveIndex]['args']['delta']
				activePlayer = move[moveIndex]['args']['player_name']
				if 'factory' in move[moveIndex]['log']:
					logging.debug(activePlayer + " earned " + str(doubloons) + " doubloons from his factory")
				elif 'sale' in move[moveIndex]['log']:
					logging.debug(activePlayer + "earned" + str(doubloons) + " doubloons from sale of resources")
				elif 'small market' in move[moveIndex]['log']:
					logging.debug(activePlayer + "earned" + str(doubloons) + " doubloons from his small market")
				elif 'large market' in move[moveIndex]['log']:
					logging.debug(activePlayer + "earned" + str(doubloons) + " doubloons from his large market")
				else:
					logging.debug(activePlayer + " earned " + str(doubloons) + " doubloons from the "+ role)

	################################################
	# Role Parsing Functions

	def parseCraftsman(self, move):
		moveIndex = 0
		privilege = False
		while not self.isAction(move[moveIndex]['args'], 'stNextPlayerForRoleSelection'):
			if 'res_type' in move[moveIndex]['args']:
				numRes = move[moveIndex]['args']['delta']
				resType = move[moveIndex]['args']['res_type']
				activePlayer = move[moveIndex]['args']['player_name']
				logging.debug(activePlayer + " produced " + str(numRes) + " " + resType + ". privilege? " + str(privilege))
			elif self.isAction(move[moveIndex]['args'], 'stPlayerCraftsmanPrivilege'):
				privilege = True
			self.doubloonsEarned(move, moveIndex, "craftsman")
			move, moveIndex = self.incMoveIndex(move, moveIndex)

	# TODO : Add in University action handling
	def parseBuilder(self, move):
		moveIndex = 0
		while not self.isAction(move[moveIndex]['args'], 'stNextPlayerForRoleSelection'):
			if 'bld_type_tr' in move[moveIndex]['args']:
				bld_type = move[moveIndex]['args']['bld_type_tr']
				cost = move[moveIndex]['args']['cost']
				score_delta = move[moveIndex]['args']['score_delta']
				activePlayer = move[moveIndex]['args']['player_name']
				# Need to keep track of same bld id for settler
				building_id = move[moveIndex]['args']['bld_id']
				logging.debug(activePlayer + " built " + bld_type + " (bld_id: " + building_id + ")  for " + str(cost) + " doubloon, gaining " + score_delta + " victory points")
			self.doubloonsEarned(move, moveIndex, "builder")
			move, moveIndex = self.incMoveIndex(move, moveIndex)

	def parseProspector(self, move):
		moveIndex = 0
		while not self.isAction(move[moveIndex]['args'], 'stNextPlayerForRoleSelection'):
			if 'type' in move[moveIndex]:
				if move[moveIndex]['type'] == 'doubloonsEarned':
					doubloons = move[moveIndex]['args']['delta']
					activePlayer = move[moveIndex]['args']['player_name']
					logging.debug(activePlayer + " earned " + str(doubloons) + " doubloons from the prospector.")
			self.doubloonsEarned(move, moveIndex, "builder")
			move, moveIndex = self.incMoveIndex(move, moveIndex)

	def parseSettler(self, move):
		moveIndex = 0
		while not self.isAction(move[moveIndex]['args'], 'stNextPlayerForRoleSelection'):
			if 'res_type' in move[moveIndex]['args']:
				plantation_type = move[moveIndex]['args']['res_type']
				activePlayer = move[moveIndex]['args']['player_name']
				# Need to keep track of same plantation id for placing colonists
				plantation_id = move[moveIndex]['args']['pla_id']
				# Quarry is rock lol
				logging.debug(activePlayer + " chose a " + plantation_type + " plantation (pla_id: "+ plantation_id +")")
			#if self.isAction(move[moveIndex]['args'], 'stPlayerSettlerHacienda'):
			#if self.isAction(move[moveIndex]['args'], 'stPlayerSettlerHospice'):
			self.doubloonsEarned(move, moveIndex, "settler")
			move, moveIndex = self.incMoveIndex(move, moveIndex)

	def parseMayor(self, move):
		moveIndex = 0
		while not self.isAction(move[moveIndex]['args'], 'stNextPlayerForRoleSelection'):
			if 'type' in move[moveIndex]:
				moveType = move[moveIndex]['type']
				if 'player_name' in move[moveIndex]['args']:
					activePlayer = move[moveIndex]['args']['player_name']
				if 'delta' in move[moveIndex]['args']:
					colonist_delta = move[moveIndex]['args']['delta']
				if moveType == 'colonistsEarnedFromSupply':
					logging.debug(activePlayer + " takes " + str(colonist_delta) + " colonist from the supply as his privilege")
				elif moveType == 'colonistsEarnedFromShip':
					logging.debug(activePlayer + " takes " + str(colonist_delta) + " colonist from the ship")
				elif moveType == 'colonistToBuilding':
					building_id = move[moveIndex]['args']['bld_id']
					logging.debug(activePlayer + " moves " + str(colonist_delta) + " colonist to bld_id: " + building_id)
				elif moveType == 'colonistToPlantation':
					plantation_id = move[moveIndex]['args']['pla_id']
					logging.debug(activePlayer + " moves " + str(colonist_delta) + " colonist to pla_id: " + plantation_id)
			self.doubloonsEarned(move, moveIndex, "mayor")
			move, moveIndex = self.incMoveIndex(move, moveIndex)

	def parseCaptain(self, move):
		moveIndex = 0
		privilege = False
		harbor = False
		while not self.isAction(move[moveIndex]['args'], 'stNextPlayerForRoleSelection'):
			if 'type' in move[moveIndex]:
				moveType = move[moveIndex]['type']
				if 'player_name' in move[moveIndex]['args']:
					activePlayer = move[moveIndex]['args']['player_name']
				if moveType == 'selectShip':
					shipCapacity = move[moveIndex]['args']['capacity']
					shipId = move[moveIndex]['args']['shp_id']
					logging.debug(activePlayer + " selected the " + shipCapacity + " barrel ship (shp_id: " + shipId + ")")
				elif moveType == 'goodsShipped':
					res_type = move[moveIndex]['args']['res_type']
					shipId = move[moveIndex]['args']['shp_id']
					num_goods = move[moveIndex]['args']['delta']
					logging.debug(activePlayer + " shipped " + str(num_goods) + " " + res_type + " on ship " + str(shipId))
				elif moveType == 'victoryPointsEarned':
					num_victory = move[moveIndex]['args']['delta']
					if 'privilege' in move[moveIndex]['log']:
						privilege = True
						logging.debug(activePlayer + " recieved " + str(num_victory) + " vp from their privilege")
					elif 'harbor' in move[moveIndex]['log']:
						harbor = True
						logging.debug(activePlayer + " recieved " + str(num_victory) + " vp from their harbor")
					else:
						logging.debug(activePlayer + " recieved " + str(num_victory) + " vp for shipping goods")
			self.doubloonsEarned(move, moveIndex, "captain")
			move, moveIndex = self.incMoveIndex(move, moveIndex)

	# TODO: Sale is a separate action from doubloons earned -
	# maybe we want to combine these into a single action
	def parseTrader(self, move):
		moveIndex = 0
		while not self.isAction(move[moveIndex]['args'], 'stNextPlayerForRoleSelection'):
			if 'type' in move[moveIndex]['args']:
				if 'type' == 'resourceSold':
					player_name = move[moveIndex]['args']['player_name']
					res_type = move[moveIndex]['args']['res_type']
					logging.debug(player_name + " sold 1 " + res_type + " barrel")
			self.doubloonsEarned(move, moveIndex, "trader")
			move, moveIndex = self.incMoveIndex(move, moveIndex)

	# END Role Parsing Functions
	##################################################

#Players.append(Player(gameID = self.game.gameID, playerID = player_num, playerName = player,
	#colonists = 0, victoryPoints = 0, Doubloons = numDubloons))
#Plantations.append(Plantation(ownerID = (self.game.gameID, player_num), plantationID = self.getNextPlantationID(self.game.gameID, player_num),
	#plantationType = plantation, activated = False))
	# FUNCTION Update Player Entity

	#def updatePlayer(self, gameID, playerID, playerName, colonists):
		#return ""

# End PRParser class
####################################################

#################################################
# Main Code
#

if len(sys.argv) != 2:
	logging.debug(sys.argv[0], " requires the name of a PR JSON log")
	sys.exit(1)

# Sample parser instance
parser = PRParser(sys.argv[1])

# Can modify this statement to check the contents of any tables
with db_session:
	# .show() does a nice pretty logging.debug of whatever the contents
	# of that query object is
	Game.select().show()
	Plantation.select().show()
	Player.select().show()