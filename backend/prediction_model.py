import requests
from datetime import datetime, UTC, timedelta, timezone
import pytz
from sklearn.linear_model import LinearRegression
import numpy as np
import os
from flask import jsonify
from dotenv import load_dotenv

load_dotenv()

sports_data_api = os.getenv("SPORTS_DATA_API")
nba_rapid_api =os.getenv("NBA_RAPID_API")

headers = {
    "x-rapidapi-key": nba_rapid_api,
    "x-rapidapi-host": "api-nba-v1.p.rapidapi.com"
}
# GET PLAYER RESULTS------------------------------------------------
def search_players(last_name):

    url = "https://api-nba-v1.p.rapidapi.com/players"
    response = requests.get(url, headers=headers, params={"search": last_name})
    player_data = response.json().get('response', [])

    if not player_data:
        return jsonify({"error": f"No players found for '{last_name}'"}), 404

    players = [{"id": p["id"], "name": f"{p['firstname']} {p['lastname']}"} for p in player_data]
    
    return jsonify(players)

# GET TEAM FROM PLAYER ID------------------------------------------------
def get_player_team_code(player_id):
    """ Get the team code of a player based on their ID """
    url = "https://api-nba-v1.p.rapidapi.com/players/statistics"
    querystring = {"id": player_id, "season": "2024"}
    
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()


    games = data.get("response", [])
    
    if games:
        team = games[0].get('team')
        if team:
            return team.get('code', None)
    return None

# GET TEAM ID FROM TEAM NAME------------------------------------------------
def get_team_id(team_name):
    """ Get the team ID based on team abbreviation """
    url = "https://nba-results-pro.p.rapidapi.com/nba/teams"

    response = requests.get(url, headers = {
	"x-rapidapi-key": nba_rapid_api,
	"x-rapidapi-host": "nba-results-pro.p.rapidapi.com"
})
    data = response.json()
    
    teams = data.get("teams", [])
    if not teams:
        print(f"Error: Missing 'teams' in API response.")
    
    team_dict = {team.get("team_abbreviation"): team.get("team_id") for team in teams}
    
    return team_dict.get(team_name, None)

# GET PREDICTION------------------------------------------------
def get_player_prediction(player_id):
    
    url = "https://api-nba-v1.p.rapidapi.com/players/statistics"
    response = requests.get(url, headers=headers, params={"id": player_id, "season": "2024"})
    data = response.json()
    games = data.get("response", [])[-5:] 
    
    # GET RECENT PLAYER STATS 
    player_stats = []
    recent_points = []
    for game in games:
        game_id = game['game']['id']
        game_response = requests.get(
            "https://api-nba-v1.p.rapidapi.com/games", headers=headers, params={"id": game_id}
        )

        game_json = game_response.json()
        if not game_json or "response" not in game_json or not game_json["response"]:
            continue  
        
        game_info = game_json["response"][0] 

        teams = game_info.get("teams")
        if not teams or "home" not in teams or "visitors" not in teams:
            print(f"Warning: Missing 'teams' in game data for game ID {game_id}")
            continue 
        
        home_team = teams.get("home", {})
        away_team = teams.get("visitors", {})
        home_team_id = home_team.get("id")
        away_team_id = away_team.get("id")

        if not home_team_id or not away_team_id:
            print(f"Warning: Missing 'id' in home or away team for game ID {game_id}")
            continue 

        # GET OPPONENT PER GAME
        opponent = home_team['nickname'] if away_team_id == game['team']['id'] else away_team['nickname']
        
        # CONVERTING TIME
        game_date = datetime.strptime(game_info.get('date', {}).get('start', 'Unknown'), '%Y-%m-%dT%H:%M:%S.000Z')
        game_date = game_date.replace(tzinfo=UTC).astimezone(pytz.timezone('America/Los_Angeles')).date()
        
        # DETERIME RESULT OF EACH GAME 
        home_team_points = game_info["scores"]["home"]["points"]
        away_team_points = game_info["scores"]["visitors"]["points"]

        player_team_id = game["team"]["id"]
        home_team_id = game_info["teams"]["home"]["id"]
        away_team_id = game_info["teams"]["visitors"]["id"]

        if "status" in game_info and game_info["status"]["long"] != "Finished":
            result = "Underway"
        else:
            if player_team_id == home_team_id:
                result = "W" if home_team_points > away_team_points else "L"
            else:
                result = "W" if away_team_points > home_team_points else "L"

        # PLAYER STATS OBJECT 
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
    
    # GET NEXT OPPONENT
    team_name = get_player_team_code(player_id)
    if not team_name:
        print("Error: Could not retrieve team name.")
        return None
    
    sportsdata_headers = {"Ocp-Apim-Subscription-Key": sports_data_api}
    response = requests.get("https://api.sportsdata.io/v3/nba/scores/json/Games/2025", headers=sportsdata_headers)
    games = response.json()
    
    today = datetime.now(timezone.utc)
    buffer_time = timedelta(hours=2)
    next_game = None 
    for game in games:
        game_time = datetime.strptime(game.get("Day"), "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        
        if game["HomeTeam"] == team_name or game["AwayTeam"] == team_name:
            if game_time > today - buffer_time:  
                next_game = game
                break

    if not next_game:
        print("Error: No upcoming games found for the team.")
        return None
    
    # GET NEXT GAME DATE 
    next_opponent = next_game["AwayTeam"] if next_game["HomeTeam"] == team_name else next_game["HomeTeam"]
    next_opponent_date = next_game["Day"]
    
    # GET OPPONENT ALLOWED PPG
    team_id = get_team_id(next_opponent)
    if not team_id:
        print(f"Error: Could not find team ID for {next_opponent}")
        return None
    
    response = requests.get(f"https://nba-results-pro.p.rapidapi.com/nba/teams/{team_id}/season/information", headers= {
	"x-rapidapi-key": nba_rapid_api,
	"x-rapidapi-host": "nba-results-pro.p.rapidapi.com"
    })
    allowed_ppg = response.json().get("points_allowed_per_game", 0)
    
    # TRAIN THE ML MODEL
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
        "recent_games": player_stats,
        "recent_points": recent_points,
        "next_opponent": next_opponent,
        "next_opponent_date": next_opponent_date,
        "opponent_allowed_ppg": allowed_ppg,
        "predicted_points": predicted_points
    })

