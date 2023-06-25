import math

# Initial Elo rating for all teams
INITIAL_ELO = 1500

# K-factor determines how much the ratings change after each game
K_FACTOR = 32

# Historical data of NFL games (replace with your own data)
# Each entry should be in the format: (team1, team2, result)
# Result can be 1 for team1 win, 0.5 for a tie, or 0 for team2 win
historical_data = [
    ("Team A", "Team B", 1),
    ("Team C", "Team D", 0.5),
    # Add more historical data here
]

# Function to calculate expected win probability for a team
def expected_win_probability(team_rating, opponent_rating):
    return 1 / (1 + math.pow(10, (opponent_rating - team_rating) / 400))

# Function to calculate the K-factor based on the number of games played
def calculate_k_factor(team):
    if team['games_played'] < 30:
        return K_FACTOR
    elif 30 <= team['games_played'] < 50:
        return K_FACTOR / 2
    else:
        return K_FACTOR / 4

# Function to update Elo ratings based on match results
def update_elo_ratings(team_ratings, team, opponent, result):
    team_data = team_ratings.get(team, {'rating': INITIAL_ELO, 'games_played': 0})
    opponent_data = team_ratings.get(opponent, {'rating': INITIAL_ELO, 'games_played': 0})

    team_rating = team_data['rating']
    opponent_rating = opponent_data['rating']

    expected_team_win_prob = expected_win_probability(team_rating, opponent_rating)

    if result == 1:
        actual_team_win_prob = 1
    elif result == 0:
        actual_team_win_prob = 0
    else:
        actual_team_win_prob = 0.5

    delta = calculate_k_factor(team_data) * (actual_team_win_prob - expected_team_win_prob)
    team_data['rating'] = team_rating + delta
    team_data['games_played'] += 1

    team_ratings[team] = team_data

# Function to predict the outcome of a game
def predict_outcome(team_ratings, team, opponent):
    team_data = team_ratings.get(team, {'rating': INITIAL_ELO, 'games_played': 0})
    opponent_data = team_ratings.get(opponent, {'rating': INITIAL_ELO, 'games_played': 0})

    team_rating = team_data['rating']
    opponent_rating = opponent_data['rating']

    expected_team_win_prob = expected_win_probability(team_rating, opponent_rating)

    if expected_team_win_prob > 0.5:
        return team
    elif expected_team_win_prob < 0.5:
        return opponent
    else:
        return "Tie"

# Create a dictionary to store team ratings
team_ratings = {}

# Update Elo ratings based on historical data
for game in historical_data:
    team1, team2, result = game
    update_elo_ratings(team_ratings, team1, team2, result)

# Predict outcomes of future games
team1 = "Team A"
team2 = "Team B"
predicted_winner = predict_outcome(team_ratings, team1, team2)
print("Predicted winner:", predicted_winner)
