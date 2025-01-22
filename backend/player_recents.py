import requests
from datetime import datetime, UTC
import pytz
from sklearn.linear_model import LinearRegression
import numpy as np
from flask import jsonify
# API headers
headers = {
    "x-rapidapi-key": "b7ff177dc6msh0354e8083416a13p185307jsndfdc4d061346",
    "x-rapidapi-host": "api-nba-v1.p.rapidapi.com"
}

def get_player_team_code(player_id):
    """ Get the team code of a player based on their ID """
    url = "https://api-nba-v1.p.rapidapi.com/players/statistics"
    querystring = {"id": player_id, "season": "2024"}
    
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    
    # Safely access 'response' key and extract the team code
    games = data.get("response", [])
    if games:
        return games[0]['team'].get('code', None)
    return None

def get_team_id(team_name):
    """ Get the team ID based on team abbreviation """
    url = "https://nba-results-pro.p.rapidapi.com/nba/teams"

    response = requests.get(url, headers = {
	"x-rapidapi-key": "b7ff177dc6msh0354e8083416a13p185307jsndfdc4d061346",
	"x-rapidapi-host": "nba-results-pro.p.rapidapi.com"
})
    data = response.json()
    
    # Ensure 'teams' exists in the response
    teams = data.get("teams", [])
    if not teams:
        raise ValueError(f"Error: Missing 'teams' in API response.")
    
    # Create a mapping of team abbreviation to team_id
    team_dict = {team.get("team_abbreviation"): team.get("team_id") for team in teams}
    
    return team_dict.get(team_name, None)

def get_player_prediction(player_name):
    """ Get player prediction by analyzing their recent games and next opponent """
    
    # Get Player ID
    url = "https://api-nba-v1.p.rapidapi.com/players"
    response = requests.get(url, headers=headers, params={"search": player_name})
    player_data = response.json()
    player_id = player_data['response'][0]['id']
    
    # Get Recent Game Stats
    url = "https://api-nba-v1.p.rapidapi.com/players/statistics"
    response = requests.get(url, headers=headers, params={"id": player_id, "season": "2024"})
    data = response.json()
    games = data.get("response", [])[-5:]  # Get last 5 games
    
    player_stats = []
    recent_points = []
    
    for game in games:
        game_id = game['game']['id']
        game_response = requests.get("https://api-nba-v1.p.rapidapi.com/games", headers=headers, params={"id": game_id})
        game_info = game_response.json().get("response", [{}])[0]
        
        # Extract home and away teams safely
        home_team = game_info.get('teams', {}).get('home', {})
        away_team = game_info.get('teams', {}).get('visitors', {})
        
        home_team_id = home_team.get('id')
        away_team_id = away_team.get('id')
        
        # Check if ids are valid
        if home_team_id is None or away_team_id is None:
            print("Error: Missing 'id' in home or away team data.")
            continue
        
        # Determine opponent
        opponent = home_team['nickname'] if away_team_id == game['team']['id'] else away_team['nickname']
        
        # Convert game start date to LA timezone
        game_date = datetime.strptime(game_info.get('date', {}).get('start', 'Unknown'), '%Y-%m-%dT%H:%M:%S.000Z')
        game_date = pytz.utc.localize(game_date).astimezone(pytz.timezone('America/Los_Angeles')).strftime('%Y-%m-%d %H:%M:%S')
        
        # Calculate result
        result = "Win" if game_info['scores']['home']['points'] > game_info['scores']['visitors']['points'] else "Loss"
        
        # Save the stats
        stats = {
            "points": game.get("points", 0),
            "rebounds": game.get("totReb", 0),
            "assists": game.get("assists", 0),
            "game_id": game_id,
            "opponent": opponent,
            "game_date": game_date,
            "result": result
        }
        
        player_stats.append(stats)
        recent_points.append(game.get("points", 0))
    
    # Get Next Opponent
    team_name = get_player_team_code(player_id)
    if not team_name:
        print("Error: Could not retrieve team name.")
        return None
    
    sportsdata_headers = {"Ocp-Apim-Subscription-Key": "e66cbb3731f14beda2b155087756ad48"}
    response = requests.get("https://api.sportsdata.io/v3/nba/scores/json/Games/2025", headers=sportsdata_headers)
    games = response.json()
    
    today = datetime.now(UTC)
    next_game = next(
        (game for game in games if datetime.strptime(game.get("Day"), "%Y-%m-%dT%H:%M:%S").replace(tzinfo=UTC) > today and
         (game["HomeTeam"] == team_name or game["AwayTeam"] == team_name)), None)
    
    if not next_game:
        print("Error: No upcoming games found for the team.")
        return None
    
    next_opponent = next_game["AwayTeam"] if next_game["HomeTeam"] == team_name else next_game["HomeTeam"]
    next_opponent_date = next_game["Day"]
    
    # Get Opponent Allowed PPG
    team_id = get_team_id(next_opponent)
    if not team_id:
        print(f"Error: Could not find team ID for {next_opponent}")
        return None
    
    response = requests.get(f"https://nba-results-pro.p.rapidapi.com/nba/teams/{team_id}/season/information", headers= {
	"x-rapidapi-key": "b7ff177dc6msh0354e8083416a13p185307jsndfdc4d061346",
	"x-rapidapi-host": "nba-results-pro.p.rapidapi.com"
    })
    allowed_ppg = response.json().get("points_allowed_per_game", 0)
    
    # Predict Points using a simple linear regression model
    X = np.array([
        [25, 28, 22, 24, 30, 112],
        [15, 18, 12, 20, 22, 105],
        [35, 40, 38, 45, 37, 115],
        [10, 12, 8, 11, 9, 95],
        [20, 25, 22, 18, 26, 108],
        [30, 28, 25, 32, 31, 110],
        [18, 20, 22, 21, 19, 107],
        [40, 38, 42, 37, 35, 120],
        [12, 10, 8, 14, 11, 98],
        [22, 24, 25, 23, 27, 109]
    ])
    y = np.array([27, 19, 43, 10, 24, 29, 21, 41, 12, 26])
    
    model = LinearRegression()
    model.fit(X, y)
    
    prediction_input = recent_points + [int(allowed_ppg)]
    predicted_points = model.predict([prediction_input])[0]
    
    return jsonify({
        "player_name": player_name,
        "recent_games": player_stats,
        "recent_points": recent_points,
        "next_opponent": next_opponent,
        "next_opponent_date": next_opponent_date,
        "opponent_allowed_ppg": allowed_ppg,
        "predicted_points": predicted_points
    })

