from pony.orm import *
import os


## Delete created database
#Check if database exists first.
if os.path.isfile("sqlite.db"):
	os.remove("sqlite.db")
db = Database("sqlite", "sqlite.db", create_db=True)

class Game(db.Entity):
	gameID = PrimaryKey(int)
	numOfPlayers = Required(int)
	StartTime = Optional(str)
	EndTime = Optional(str)
	Turns = Set("Turn")
	Players = Set("Player")
	Ships = Set("Ships")


class Player(db.Entity):
	gameID = Required(Game)
	playerID = Required(int)
	Turn = Set("Turn")
	playerName = Required(str)
	colonists = Required(int)
	victoryPoints = Required(int)
	Doubloons = Required(int)
	#Implementing crops as an attribute since there is nothing unique about each crop aside from it's type. Craftsman/Captain can be handled with arithmetic.
	#Crop Total/running out of crops is likely handled by internal game logic/is constant
	CornOwned = Required(int)
	IndigoOwned = Required(int)
	SugarOwned = Required(int)
	TobaccoOwned = Required(int)
	CoffeeOwned = Required(int)
	Buildings = Set("Building")
	Plantations = Set("Plantation")
	PrimaryKey(gameID,playerID)

class Turn(db.Entity):
	gameID = Required(Game)
	ActivePlayer = Required(Player)
	#Ticks up on every distinct game action/subsequent db write
	EventNum = Required(int)
	#Cycles once each new governor round
	RoundNum = Required(int)
	#Cycles once each new role phase
	PhaseNum = Required(int)
	#Cycles once each new player turn within a role
	TurnNum = Required(int)
	EventType = str
	Action = str
	Ships = Set("Ships")
	#Governor = Required(Player, reverse="playerName")
	PrimaryKey(gameID,EventNum)
	

# Game id is included in ownerID Foreign key
#Good call, I read this as I was wondering that exact thing.
class Building(db.Entity):
	ownerID = Required(Player)
	buildingID = Required(int)
	activated = Required(bool)
	PrimaryKey(ownerID,buildingID)
	
	#I think we need to put the turn as a foreign key or we cannot track changes to the building throughout the game.
	#It also has to be a part of the primary key, otherwise activate -> deactivate will lead to a non unique PK
# Game id is included in ownerID Foreign key
class Plantation(db.Entity):
	ownerID = Required(Player)
	plantationID = Required(int)
	plantationType = Required(str)
	activated = Required(bool)
	PrimaryKey(ownerID,plantationID)


class Ships(db.Entity):
	gameID = Required(Game)
	shipID = Required(int)
	Capacity = int
	CropType = str
	CropNum = int
	Turn = Required(Turn)
	PrimaryKey(gameID,shipID,Turn)

#Not ready to flesh out yet but I'm sure we'll need it. 
#class TradingHouse(db.Entity):

# TURN ON DEBUGGING
sql_debug(False)

db.generate_mapping(create_tables=True)
