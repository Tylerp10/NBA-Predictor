from flask import jsonify
import requests
import os
from dotenv import load_dotenv
import time
load_dotenv()
# HANDLE TIMEOUT ERRORS
def make_request_with_retries(func, retries=3, delay=2, *args, **kwargs):
    for _ in range(retries):
        try:
            return func(*args, **kwargs, timeout=60) 
        except requests.exceptions.ReadTimeout:
            print("Request timed out. Retrying...")
            time.sleep(delay)
    raise Exception("Failed after multiple retries")

nba_teams = ["76ers", "Bucks", "Bulls", "Cavaliers", "Clippers", "Celtics", "Grizzlies", "Hawks", "Heat", "Hornets", "Jazz", "Kings", "Knicks", "Lakers", "Magic", "Mavericks", "Nets", "Nuggets", "Pacers", "Pelicans", "Pistons", "Raptors", "Rockets", "Suns", "Spurs", "Thunder", "Timberwolves", "Trail Blazers", "Warriors", "Wizards"]

api_key = os.getenv("SPORTS_RADAR_KEY")

url = f'https://api.sportradar.com/nba/trial/v8/en/league/teams.json?api_key={api_key}'

response = requests.get(url)

if response.status_code == 200:
    teams_data = response.json()
    teams = {
        team["name"]: team["id"]
        for team in teams_data.get("teams", [])
        if team["name"] in nba_teams
    }
else:
    print("error")


def player_fetcher(team_id):
    api_key = os.getenv("SPORTS_RADAR_KEY")
    roster_url = f"https://api.sportradar.com/nba/trial/v8/en/teams/{team_id}/profile.json?api_key={api_key}"

    roster = requests.get(roster_url)

    if roster.status_code == 200:
        roster_data = roster.json()
        players = {
            player["full_name"]:player["id"]
            for player in roster_data.get("players", [])
        }
        return jsonify(players)
    else:
        return jsonify({"error": "Failed to fetch roster, {roster.status_code}"})


def stats_fetcher(player_id):
    api_key = os.getenv("SPORTS_RADAR_KEY")
    url = f'https://api.sportradar.com/nba/trial/v8/en/players/{player_id}/profile.json?api_key={api_key}'

    stats = requests.get(url)

    if stats.status_code == 200:

        stats_data = stats.json()
        seasons = stats_data.get("seasons", [])

        if seasons:
            current_season = seasons[0]
            team = current_season.get("teams", [])

            if team:
                current_team = team[0]
                stats = current_team.get("average")

                filtered_stats = {
                "points": stats.get("points"),
                "assists": stats.get("assists"),
                "rebounds": stats.get("rebounds"),
                "blocks": stats.get("blocks"), 
                "steals": stats.get("steals"),
                "field_goals_made": stats.get("field_goals_made"),
                "field_goals_att": stats.get("field_goals_att"),
                "three_points_made": stats.get("three_points_made"),
                "three_points_att": stats.get("three_points_att"),
                }

                return jsonify(filtered_stats)
    else:
        return jsonify({"error": "Failed to fetch stats, {stats.status_code}"})



api = os.getenv("ODDS_KEY")

events_url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/events?apiKey={api}"

response = requests.get(events_url)

if response.status_code == 200:
    games_data = response.json()
    games = {}

    for game in games_data:
        game_id = game["id"]
        matchup = game["home_team"] + " vs " + game["away_team"]
        games[matchup] = game_id        
else:
    print(response.status_code)


def odds_fetcher(odds_id, market_id):
    api = os.getenv("ODDS_KEY")

    odds_url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/events/{odds_id}/odds?apiKey={api}&regions=us&markets={market_id}&oddsFormat=american"

    odds_response = requests.get(odds_url)

    if odds_response.status_code == 200:
        odds_data = odds_response.json()
        game_odds = {}
        # print(odds_data)

        for bookermaker in odds_data.get("bookmakers", []):
            bookermaker_name = bookermaker["title"]

            market = next((m for m in bookermaker.get("markets", []) if m["key"] == market_id), None)

            if market:

                outcomes = market.get("outcomes", [])
                market_name = market.get("key")
                if market_id == "spreads":
                    team_lines = {
                        outcome["name"]: {
                            "Market": market_name,
                            "Price": outcome["price"],
                            "Value": outcome["point"]
                        }
                        for outcome in outcomes
                    }
                elif market_id == "h2h":
                    team_lines = {
                        outcome["name"]: {
                            "Market": market_name,
                            "Price": outcome["price"],
                        }
                        for outcome in outcomes
                    }
                elif market_id == "totals":
                    team_lines = {
                        outcome["name"]: {
                            "Market": market_name,
                            "Line": outcome["name"],
                            "Price": outcome["price"],
                            "Value": outcome["point"]
                        }
                        for outcome in outcomes
                    }

                game_odds[bookermaker_name] = team_lines
            
        return jsonify(game_odds)

    else:
        return jsonify(odds_response.status_code)


def player_props_fetcher(game_id, player_prop_market):
    api = os.getenv("ODDS_KEY")


    odds_url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/events/{game_id}/odds?apiKey={api}&regions=us&markets={player_prop_market}&oddsFormat=american"

    response = requests.get(odds_url)

    if response.status_code == 200:
        data = response.json()
        player_props = {}
        
        for bookmaker in data.get("bookmakers", []):
            bookmaker_name = bookmaker.get("title")
            player_props[bookmaker_name] = {}
        
            for market in bookmaker.get("markets", []):  
                market_key = market.get("key")
                outcomes = market.get("outcomes", [])
                
                player_outcomes = [
                    {"player": outcome.get("description"),
                     "Line": outcome.get("name"),
                     "Value": outcome.get("point"),
                     "odds": outcome.get("price"), }
                    for outcome in outcomes
                ]
                if player_outcomes:
                    player_props[bookmaker_name][market_key] = player_outcomes


        return jsonify(player_props)

    else:
        return jsonify("Error Fetching Player Props")


from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog, commonplayerinfo, playernextngames, teamdashboardbygeneralsplits
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


def get_player_info(player_name):

    print("Fetching player info for:", player_name)
    all_players = players.get_active_players()
    player = next((p for p in all_players if p['full_name'] == player_name), None)
    
    if not player:
        return None
    
    player_id = int(player['id'])
    player_info = make_request_with_retries(commonplayerinfo.CommonPlayerInfo, 3, 2, player_id=player_id)
    player_data = player_info.get_data_frames()[0]

    return {
        "player_id": player_id,
        "team_id": int(player_data.loc[0, 'TEAM_ID']),
        "team_name": str(player_data.loc[0, 'TEAM_NAME']),
        "team_abbr": str(player_data.loc[0, 'TEAM_ABBREVIATION'])
    }

def get_recent_performance(player_id):

    print("Fetching player performance for:", player_id)
    player_logs = make_request_with_retries(playergamelog.PlayerGameLog, 3, 2, player_id=player_id, season='2024-25')
    player_logs_df = player_logs.get_data_frames()[0]

    player_logs_df = player_logs_df.head(5)
    points = player_logs_df['PTS'].tolist()
    points_list = [int(value) for value in points]

    return {
        "recent_performances": player_logs_df[['GAME_DATE', 'MATCHUP', 'WL', 'AST', 'REB', 'PTS']].to_dict(orient='records'),
        "points_list": points_list
    }
            
def get_next_game(player_id, team_id):
    """Fetch player's next game details."""
    print("Fetching next game for player:", player_id)
    next_games = make_request_with_retries(playernextngames.PlayerNextNGames, 3, 2, player_id=player_id, number_of_games=1)
    next_games_df = next_games.get_data_frames()[0]

    if next_games_df.empty:
        return None

    game = next_games_df.iloc[0]
    if game["HOME_TEAM_ID"] == team_id:
        opponent_id = int(game["VISITOR_TEAM_ID"])
        opponent_name = str(game["VISITOR_TEAM_NAME"])
        player_team = str(game["HOME_TEAM_NAME"])
    else:
        opponent_id = int(game["HOME_TEAM_ID"])
        opponent_name = str(game["HOME_TEAM_NAME"])
        player_team = str(game["VISITOR_TEAM_NAME"])

    return {
        "opponent_id": opponent_id,
        "opponent_name": opponent_name,
        "game_date": str(game['GAME_DATE']),
        "player_team": player_team
    }

    # GET OPPONENT DEFENSIVE STATS 
def get_opponent_defense_stats(opponent_id, season='2024-25'):

    print("Fetching opponent defense stats for:", opponent_id)
    team_stats = make_request_with_retries(
        teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits, 3, 2,
        season=season, team_id=opponent_id, measure_type_detailed_defense='Opponent'
    )
    team_stats_df = team_stats.get_data_frames()[0]

    team_total_oppg = team_stats_df['OPP_PTS']
    team_gp = team_stats_df['GP']
    team_oppg = team_total_oppg / team_gp
    return team_oppg.iloc[0]


    # PREDICTION MODEL 
def run_prediction(points_list, opponent_allowed_points):
    """Train Linear Regression model and predict."""
    print("Running prediction model...")
    
    # Sample training data
    X = [
        [25, 28, 22, 24, 30, 112],
        [15, 18, 12, 20, 22, 105],
        [35, 40, 38, 45, 37, 115],
        [10, 12, 8, 11, 9, 95],
        [20, 25, 22, 18, 26, 108],
        [30, 28, 25, 32, 31, 110],
        [18, 20, 22, 21, 19, 107],
        [40, 38, 42, 37, 35, 120],
        [12, 10, 8, 14, 11, 98],
        [22, 24, 25, 23, 27, 109],
        [25, 28, 22, 24, 30, 118],  
        [15, 18, 12, 20, 22, 115],  
        [35, 40, 38, 45, 37, 125],
        [10, 12, 8, 11, 9, 100],
        [20, 25, 22, 18, 26, 114]
    ]
    y = [27, 19, 43, 10, 24, 29, 21, 41, 12, 26, 29, 21, 45, 11, 25]

    # Train model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)

    prediction_input = points_list + [int(opponent_allowed_points)]
    predicted_points = model.predict([prediction_input]).tolist()

    return predicted_points

def prediction_model(player_name):

    print("Starting prediction_model for player:", player_name)

    player_info = get_player_info(player_name)
    if not player_info:
        return {"error": "Player not found"}

    performance_data = get_recent_performance(player_info["player_id"])
    if not performance_data:
        return {"error": "Could not retrieve player performance data"}

    next_game = get_next_game(player_info["player_id"], player_info["team_id"])
    if not next_game:
        return {"error": "No upcoming games found"}

    opponent_allowed_points = get_opponent_defense_stats(next_game["opponent_id"])
    if opponent_allowed_points is None:
        return {"error": "Could not retrieve opponent defensive stats"}

    predicted_points = run_prediction(performance_data["points_list"], opponent_allowed_points)

    return {
        "player_name": player_name,
        "player_team": next_game["player_team"],
        "recent_performance": performance_data["recent_performances"],
        "next_opponent": next_game["opponent_name"],
        "game_date": next_game["game_date"],
        "opponent_allowed_points": opponent_allowed_points,
        "predicted_points": predicted_points
    }