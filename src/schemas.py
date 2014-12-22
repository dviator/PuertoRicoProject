from pony.orm import *

db = Database("sqlite", ":memory:")

class Game(db.Entity):
	gameID = PrimaryKey(int)
	numOfPlayers = Required(int)
	StartTime = Required(str)
	EndTime = Required(str)

class Turn(db.Entity):
	gameID = set(Game)
	EventNum = PrimaryKey(int)
	RoundNum = Required(int)
	PhaseNum = Required(int)
	TurnNum = Required(int)
	EventType = str
	Governor = set(Player)

class Player(db.Entity):
	gameID = Required(Game)
	playerID = PrimaryKey(int)
	playerName = Required(str)
	colonists = int
	victoryPoints = int
	Doubloons = int

class Building(db.Entity):
	gameID = Required(Game)
	ownerID = Required(Player)
	buildingID = PrimaryKey(int)
	activated = bool

class Plantation(db.Entity):
	gameID = Required(Game)
	ownerID = Required(Player)
	plantationID = PrimaryKey(int)
	activated = bool

class Ships(db.Entity):
	gameID = Required(Game)
	shipID = Required(int)
	Capacity = int
	CropType = str
	CropNum = int
	


