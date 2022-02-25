import nflgame
from termcolor import colored
from pickle import load
from lxml import html
import requests

#schedule URL
YEAR = 2022
WEEK = 16
URL = "http://www.espn.com/nfl/schedule/_/week/" + str(WEEK)

SORT_BY_CONFIDENCE = True
H_TEAM_ADV = 20

team_to_index = load( open( "pkl/teamindex.pkl", "rb"))
elos = load( open( "pkl/elo.pkl", "rb"))
config = load( open( "pkl/config.pkl", "rb"))

ELO_DIFF = config["ELO_DIFF"]
ELO_BASE = config["ELO_BASE"]
START_YEAR = config["START_YEAR"]

page = requests.get(URL)
tree = html.fromstring(page.content)

games1 = tree.xpath('//tr[@class="odd"]/td/a[@class="team-name"]/abbr/text()')
games2 = tree.xpath('//tr[@class="even"]/td/a[@class="team-name"]/abbr/text()')

games = []

#weave them
while not(len(games1) == 0 and len(games2) == 0):
	if len(games1) > 0:
		games.append((games1[0], games1[1]))
		games1.pop(0)
		games1.pop(0)
	if len(games2) > 0:
		games.append((games2[0], games2[1]))
		games2.pop(0)
		games2.pop(0)
cache = []
for game in games:
	hname = nflgame.standard_team(game[1])
	aname = nflgame.standard_team(game[0])
	if(hname == "STL"):
		hname = "LA"
	if(aname == "STL"):
		aname = "LA"
	hteam = team_to_index[hname]
	ateam = team_to_index[aname]
	eloA = elos[hteam][WEEK][YEAR-START_YEAR] + H_TEAM_ADV
	eloB = elos[ateam][WEEK][YEAR-START_YEAR]
	Ea = 1/(1 + ELO_BASE**((eloB - eloA)/ELO_DIFF))
	Eb = 1/(1 + ELO_BASE**((eloA - eloB)/ELO_DIFF))
	diff = abs(Ea - Eb)
	col="black"
	if Ea > Eb:
		hcname = colored(hname, col)
		acname = aname
	elif Eb > Ea:
		hcname = hname
		acname = colored(aname, col)
	else:
		pass
	cache.append((diff,acname + " @ " + hcname + ": " + aname + " - " + str(100*Eb) + "% | " + hname + " - " + str(100*Ea) + "% | Diff - " + str(100*diff) + "%"))

if(SORT_BY_CONFIDENCE):
	cache = sorted(cache, reverse=True)

print (str(YEAR) + " Season - Week " + str(WEEK) + " Predictions:")
print ("-------------------------------------")
print (colored("0%-20%", "black"), colored("20%-40%", "black"), colored("40%-60%", "black"), colored("60%-80%","black"), colored("80%+", "black"))
print ("-------------------------------------")
for i in cache:
	print i[1]
