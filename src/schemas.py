

class Game(db.Entity):
	gameID = PrimaryKey(int)
	numOfPlayers = Required(int)
	StartTime = Required(str)
	EndTime = Required(str)

class Turn(db.Entity):
	gameID = set("Game")
	EventNum = PrimaryKey(int)
	RoundNum = Required(int)
	PhaseNum = Required(int)
	TurnNum = Required(int)
	EventType = str
	Governor = set("Player")

class Player(db.Entity):
	gameID = Required(Game)
	playerID = PrimaryKey(int)
	playerName = Required(str)

class Building(db.Entity):
	gameID = Required(Game)
	ownerID = Required(Player)
	buildingID = PrimaryKey(int)
	activated = bool
	

