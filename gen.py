import nflgame
import math
import os
from pickle import dump

START_YEAR = 2009
CUR_YEAR = 2022
CUR_WEEK = 15
REG_WEEKS = 17
POST_WEEKS = 4
INIT_ELO = 1300
ELO_DIFF = 200
ELO_BASE = 4
SEASON_RESET = 0.25
ELO_CONSTANT = 28
RISING_STREAK_CONSTANT = 0.54
FALLING_STREAK_CONSTANT = 0.36
GAME_MAGNITUDE_CONSTANT = 0.27
STREAK_LIMIT = 5

def eloEval(eloA, eloB, scoreA, scoreB, streakA, streakB):
	if scoreA > scoreB:
		Sa = 1
		Sb = 0
	elif scoreA < scoreB:
		Sa = 0
		Sb = 1
	else:
		Sa = 0.5
		Sb = 0.5
	Ea = 1/(1 + ELO_BASE**((eloB - eloA)/ELO_DIFF))
	Eb = 1/(1 + ELO_BASE**((eloA - eloB)/ELO_DIFF))
	GAME_MAG = GAME_MAGNITUDE_CONSTANT*math.exp((eloA + eloB)/(2*INIT_ELO)-1)
	ELO_FACTOR = ELO_CONSTANT*(math.log(abs(scoreA - scoreB)+1) + 1)*GAME_MAG
	# winning a lot in a row makes you gain more per win, up to a limit (logistic growth) - losing also accumulates
	if scoreA > scoreB:
		if streakA >= 0: # ranges from 1 to STREAK_LIMIT
			STREAK_FACTOR_A = (-0.5)*STREAK_LIMIT + (1.5*STREAK_LIMIT)/((1.0 + math.exp((-1)*RISING_STREAK_CONSTANT*abs(streakA))))
		else:
			STREAK_FACTOR_A = 1
		if streakB < 0:
			STREAK_FACTOR_B = (-0.5)*STREAK_LIMIT + (1.5*STREAK_LIMIT)/((1.0 + math.exp((-1)*FALLING_STREAK_CONSTANT*abs(streakB))))
		else:
			STREAK_FACTOR_B = 1
	elif scoreB > scoreA:
		if streakA < 0:
			STREAK_FACTOR_A = (-0.5)*STREAK_LIMIT + (1.5*STREAK_LIMIT)/((1.0 + math.exp((-1)*FALLING_STREAK_CONSTANT*abs(streakA))))
		else:
			STREAK_FACTOR_A = 1
		if streakB >= 0:
			STREAK_FACTOR_B = (-0.5)*STREAK_LIMIT + (1.5*STREAK_LIMIT)/((1.0 + math.exp((-1)*RISING_STREAK_CONSTANT*abs(streakB))))
		else:
			STREAK_FACTOR_B = 1
	else:
		STREAK_FACTOR_A = 1
		STREAK_FACTOR_B = 1
	Ra = eloA + STREAK_FACTOR_A*ELO_FACTOR*(Sa - Ea)
	Rb = eloB + STREAK_FACTOR_B*ELO_FACTOR*(Sb - Eb)
	return Ra, Rb

WEEKS_PER_YEAR = REG_WEEKS + POST_WEEKS

# elos[teamid][week][year]
elos = =
streaks = [0 for i in range(len(nflgame.teams) - 1)]

team_to_index = {}

ind = 0
for i in nflgame.teams:
	if i[0] == "STL":
		continue
	team_to_index[i[0]] = ind
	elos[ind][0][0] = INIT_ELO
	ind += 1

for i in range(START_YEAR, CUR_YEAR + 1):
	print "Processing " + str(i) + " season"
	for j in range(1,WEEKS_PER_YEAR+1):
		try:
			if not (i == CUR_YEAR and j > CUR_WEEK):
				if(j <= REG_WEEKS):
					games = nflgame.games(i,week=j,kind='REG')
					#print "Processing Week " + str(j) + " of " + str(i) + " season"
				else:
					games = nflgame.games(i,week=j-REG_WEEKS,kind='POST')
					#print "Processing Postseason Week " + str(j-REG_WEEKS) + " of " + str(i) + " season"
				if len(games) > 0:
					for game in games:
						hname = nflgame.standard_team(game.home)
						aname = nflgame.standard_team(game.away)
						if(hname == "STL"):
							hname = "LA"
						if(aname == "STL"):
							aname = "LA"
						hteam = team_to_index[hname]
						ateam = team_to_index[aname]
						elos[hteam][j][i-START_YEAR], elos[ateam][j][i-START_YEAR] = eloEval(elos[hteam][j-1][i-START_YEAR], elos[ateam][j-1][i-START_YEAR], game.score_home, game.score_away, streaks[hteam], streaks[ateam])
						#update streaks
						if game.score_home > game.score_away:
							if streaks[hteam] >= 0:
								streaks[hteam] += 1
							else:
								streaks[hteam] = 0
							if streaks[ateam] <= 0:
								streaks[ateam] -= 1
							else:
								streaks[ateam] = 0
						elif game.score_away > game.score_home:
							if streaks[hteam] <= 0:
								streaks[hteam] -= 1
							else:
								streaks[hteam] = 0
							if streaks[ateam] >= 0:
								streaks[ateam] += 1
							else:
								streaks[ateam] = 0
						else: #if tie dont change
							pass
		except TypeError:
			if(j <= REG_WEEKS):
				print "Error in Week " + str(j) + " of " + str(i) + " season"
			else:
				print "Error in Postseason Week " + str(j-REG_WEEKS) + " of " + str(i) + " season"
		for x in range(len(nflgame.teams)-1): # check for byes
			if elos[x][j][i-START_YEAR] == 0:
				elos[x][j][i-START_YEAR] = elos[x][j-1][i-START_YEAR] 
		#end of year, smoosh everyone towards middle
	if i != CUR_YEAR:
		for x in range(len(nflgame.teams)-1):
			elos[x][0][i-START_YEAR+1] = (SEASON_RESET)*elos[x][WEEKS_PER_YEAR][i-START_YEAR] + (1-SEASON_RESET)*INIT_ELO

# print final elos
rank = []
for i in nflgame.teams:
	if i[0] == "STL":
		continue
	rank.append((elos[team_to_index[i[0]]][WEEKS_PER_YEAR][CUR_YEAR-START_YEAR],i[0]))

rank = sorted(rank, reverse=True)
print "Final ELO Rankings:"
for i in range(len(rank)):
	print str(i+1) + ": " + rank[i][1] + " - ELO: " + str(rank[i][0])

config = {}
config["ELO_DIFF"] = ELO_DIFF
config["ELO_BASE"] = ELO_BASE
config["START_YEAR"] = START_YEAR

if not os.path.exists("pkl/"):
	os.makedirs("pkl/")

fout = open("pkl/teamindex.pkl","wb")
dump(team_to_index,fout,protocol=2)
fout.close()
fout = open("pkl/elo.pkl","wb")
dump(elos,fout,protocol=2)
fout.close()
fout = open("pkl/config.pkl","wb")
dump(config,fout,protocol=2)
fout.close()

print "Done!"
