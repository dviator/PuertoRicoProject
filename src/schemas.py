from pony.orm import *

db = Database("sqlite", "sqlite.db", create_db=True)

class Game(db.Entity):
	gameID = PrimaryKey(int)
	numOfPlayers = Required(int)
	StartTime = Optional(str)
	EndTime = Optional(str)
	Turns = Set("Turn")
	Players = Set("Player")
	Buildings = Set("Building")
	Plantations = Set("Plantation")
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
	playerID = PrimaryKey(int)
	playerName = Required(str)
	colonists = int
	victoryPoints = int
	Doubloons = int
	Turns = Set("Turn")
	Buildings = Set("Building")
	Plantations = Set("Plantation")

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

db.generate_mapping(create_tables=True)

