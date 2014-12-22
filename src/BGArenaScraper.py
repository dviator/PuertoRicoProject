from bs4 import BeautifulSoup
import urllib
import sys
import time

for arg in sys.argv:
	url = arg

realURL = urllib.geturl(url)
print(realURL)
response = urllib.request.urlopen(url)
data = response.read()

f = open('logfile2.txt', 'wb')
f.write(data)


