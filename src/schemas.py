from pony.orm import *
import os

## Delete created database
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

class Turn(db.Entity):
	gameID = Required(Game)
	EventNum = PrimaryKey(int)
	RoundNum = Required(int)
	PhaseNum = Required(int)
	TurnNum = Required(int)
	EventType = Required(str)
	Governor = Set("Player")

class Player(db.Entity):
	gameID = Required(Game)
	playerID = Required(int)
	playerName = Required(str)
	colonists = Required(int)
	victoryPoints = Required(int)
	Doubloons = Required(int)
	Turns = Set("Turn")
	Buildings = Set("Building")
	Plantations = Set("Plantation")
	PrimaryKey(gameID, playerID)

# Game id is included in ownerID Foreign key
class Building(db.Entity):
	ownerID = Required(Player)
	buildingID = Required(int)
	activated = Required(bool)
	PrimaryKey(ownerID, buildingID)

# Game id is included in ownerID Foreign key
class Plantation(db.Entity):
	ownerID = Required(Player)
	plantationID = Required(int)
	plantationType = Required(str)
	activated = Required(bool)
	PrimaryKey(ownerID, plantationID)

class Ships(db.Entity):
	gameID = Required(Game)
	shipID = Required(int)
	Capacity = Required(int)
	CropType = Required(str)
	CropNum = Required(int)

# TURN ON DEBUGGING
sql_debug(False)

db.generate_mapping(create_tables=True)
