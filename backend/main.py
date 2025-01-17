from flask import jsonify, Flask, request
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

import time

# HANDLE TIMEOUT ERRORS
def make_request_with_retries(func, retries=3, delay=2, *args, **kwargs):
    for _ in range(retries):
        try:
            return func(*args, **kwargs, timeout=10) 
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


load_dotenv()

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

def prediction_model(player_name):
    # LOOP THROUGH ALL ACTIVE PLAYERS TO FIND SELECTED PLAYER
    season = '2024-25'
    all_players = players.get_active_players()
    # player_name = "Julius Randlde"
    player = next((p for p in all_players if p['full_name'] == player_name), None)

    # GRAB PLAYER ID AND NAME 
    if player:
        # print(f"Player found: {player['full_name']}, {player['id']}")
        player_id = player['id']

    # GET PLAYER INFO 
        player_info = make_request_with_retries(commonplayerinfo.CommonPlayerInfo, 3 ,2, player_id=player_id)
        player_data = player_info.get_data_frames()[0]

        team_id = player_data.loc[0, 'TEAM_ID']
        team_name = player_data.loc[0, 'TEAM_NAME']
        team_abbr = player_data.loc[0, 'TEAM_ABBREVIATION']
        # print(f"Player's Team: {team_name}, {team_abbr}, ID: {team_id}")

    # GET PLAYER RECENT PERFORMANCES
        player_logs = make_request_with_retries(playergamelog.PlayerGameLog, 3, 2, player_id=player_id, season=season)
        player_logs_df = player_logs.get_data_frames()[0]

        player_logs_df = player_logs_df.head(5)
        recent_performances = player_logs_df[['GAME_DATE', 'MATCHUP', 'WL', 'AST', 'REB', 'PTS']].head().to_dict(orient='records')
            
        points = player_logs_df['PTS'].tolist()
        points_list = [int(value) for value in points]
            

    else:
        print("Player not found")

    # FETCH PLAYERS NEXT GAME 
    next_games = make_request_with_retries(playernextngames.PlayerNextNGames, 3, 2, player_id=player_id, number_of_games=1)
    next_games_df = next_games.get_data_frames()[0]

    # FIGURE OUT OPPONENT TEAM NAME 
    game = next_games_df.iloc[0]
    if game["HOME_TEAM_ID"] == team_id:
        opponent_id = game["VISITOR_TEAM_ID"]
        opponent_name = game["VISITOR_TEAM_NAME"]
        player_team = game["HOME_TEAM_NAME"]
    else:
        opponent_id = game["HOME_TEAM_ID"]
        opponent_name = game["HOME_TEAM_NAME"]
        player_team = game["VISITOR_TEAM_NAME"]

    game_date = game['GAME_DATE']

    # print(f"Opponent ID is {opponent_id}, {opponent_name}, {game['GAME_DATE']}")

    # GET OPPONENT DEFENSIVE STATS 
    team_stats = make_request_with_retries(teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits, 3, 2,
        season=season,
        team_id=opponent_id, 
        measure_type_detailed_defense='Opponent'
    )

    team_stats_df = team_stats.get_data_frames()[0]

    # CALCULATE AMOUNT OF POINTS OPPONENT ALLOWS PER GAME  
    team_total_oppg = team_stats_df['OPP_PTS']
    team_gp = team_stats_df['GP']
    team_oppg = team_total_oppg/team_gp
    opponent_allowed_points = team_oppg.iloc[0]

    # print(f'{opponent_name} allows {opponent_allowed_points} per game')


    # PREDICTION MODEL 

    points_list.append(int(opponent_allowed_points))

    # SAMPLE DATA - POINTS FROM PLAYERS PAST 5 GAMES + NEXT OPPONENT ALLOWED PPG
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
    # ACTUAL SCORES
    y = [
        27, 19, 43, 10, 24, 29, 21, 41, 12, 26, 29, 21, 45, 11, 25
    ]

    # Splitting data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Model initialization and training
    model = LinearRegression()
    model.fit(X_train, y_train)

    prediction = points_list
    predicted_points = model.predict([prediction]).tolist()
    # print(f'Predicted points: {predicted_points}')

    return  {
        "player_name": player_name,
        "player_team": player_team,
        "recent_performance": recent_performances,
        "next_opponent": opponent_name,
        "game_date": game_date,
        "opponent_allowed_points": opponent_allowed_points,
        "predicted_points": predicted_points
    }




app = Flask("__name__")
CORS(app)

FRONTEND_DOMAIN = "https://hoopscope.ca"

CORS(app, resources={r"/*": {"origins": FRONTEND_DOMAIN}})

# TEAMS DATA-------------------------------------------
@app.route('/teams', methods=['GET'])
def team_selector():
    return jsonify(teams)

# TEAM ROSTER DATA-------------------------------------------
@app.route('/rosters', methods=["GET"])
def roster_fetcher():

    team_id = request.args.get("team_id")
    if not team_id:
        return jsonify({"error": "Team ID is required"}), 400
    
    return player_fetcher(team_id)
    
# PLAYER AVERAGES DATA-------------------------------------------
@app.route('/averages', methods=["GET"])
def player_averages():

    player_id = request.args.get("player_id")
    if not player_id:
        return jsonify({"error": "Player ID required"}), 400
    
    return stats_fetcher(player_id)

#GAMES DATA----------------------------------------------
@app.route('/games', methods=["GET"])
def games_fetcher():
    return jsonify(games)

#ODDS DATA----------------------------------------------
@app.route('/odds', methods=['GET'])
def game_odds():

    odds_id = request.args.get("odds_id")
    if not odds_id:
        return jsonify({'Error': 'Odds ID required'})
    
    market_id = request.args.get("market_id")
    if not market_id:
        return jsonify({'Error': 'Market ID required'})
    
    return odds_fetcher(odds_id, market_id)

#PLAYER PROPS DATA----------------------------------------------
@app.route('/playerprops', methods=["GET"])
def player_props():

    odds_id = request.args.get("odds_id")
    if not odds_id:
        return jsonify({"Error": 'Odds ID required'})
    
    player_prop_market = request.args.get("player_prop_market")
    if not player_prop_market:
        return jsonify({"Error": 'Market ID required'})
    

    return player_props_fetcher(odds_id, player_prop_market)


# PREDICTION MODEL API ----------------------------------------------
@app.route('/predict', methods=['GET'])
def predict_player_points():
    player_name = request.args.get("player_name")
    if not player_name:
        return jsonify({"error": "Player name is required"}), 400

    try:
        prediction_result = prediction_model(player_name)
        prediction_result['predicted_points'] = [round(p, 2) for p in prediction_result['predicted_points']] 
        return jsonify(prediction_result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)