import sqlite3


#Opens a connection to the sqllite database, and stores it in the file database.db
db = sqlite3.connect('database.db')

#Create a cursor object, this is what we'll use to access the database.
cursor = db.cursor()

#Create a sample table in the database.
cursor.execute('''
	CREATE TABLE game(gameID string PRIMARY KEY, numOfPlayers integer)
	''')



#We need to close the connection now that we're done with it.
db.close()