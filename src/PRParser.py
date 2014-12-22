from pony.orm import *
import sys
import json
from pprint import pprint

#####################################################
# PRParser class
class PRParser:

	def __init__(self, data):
		self.data = data

	def __init__(self, log_name):
		print("Opening PR JSON log ", log_name, "...")
		json_data = open(log_name)
		print("Parsing PR JSON log ", log_name, "...")
		self.data = json.load(json_data)

	################################################
	# FUNCTION getMove(int id)
	# Reads a 1-indexed move id and the parsed json data object
	# and returns a json array containing a number of "args" object
	def getMove(self, id):
		return self.data["data"]["data"][id-1]["data"]
	# end getMove
	################################################

	################################################
	# FUNCTION parseMove(int id)
	# Reads a 1-indexed move id and the parsed json data object
	# and returns a json array containing a number of "args" object
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
pprint(parser.getMove(2))

