from flask import jsonify, Flask, request
from flask_cors import CORS
import time
import requests
import os
from nbadata import teams, player_fetcher, stats_fetcher, odds_fetcher, player_props_fetcher
from prediction_model import get_player_prediction, search_players

app = Flask("__name__")


FRONTEND_DOMAIN = "https://hoopscope.ca"

CORS(app, resources={r"/*": {"origins": FRONTEND_DOMAIN}})

# # TEAMS DATA-------------------------------------------
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
    api = os.getenv("ODDS_KEY")

    events_url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/events?apiKey={api}&_={int(time.time())}"
    headers = {
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }
    response = requests.get(events_url, headers=headers)

    if response.status_code == 200:
        games_data = response.json()
        games = {}

        for game in games_data:
            game_id = game["id"]
            matchup = game["home_team"] + " vs " + game["away_team"]
            games[matchup] = game_id      

            resp = jsonify(games)
            resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            resp.headers["Pragma"] = "no-cache"
            resp.headers["Expires"] = "0"

        return resp, 200
    else:
        return jsonify({"error": "Failed to fetch games", "status_code": response.status_code}), 500  


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


@app.route('/search', methods=['GET'])
def get_players():
    last_name = request.args.get('last_name')
    if not last_name:
        return jsonify({"Error": 'Odds ID required'})
    
    return search_players(last_name)


@app.route('/predict', methods=['GET'])
def prediction():
    player_id = request.args.get('player_id')
    if not player_id:
        return jsonify({"Error": 'Player ID required'})

    return get_player_prediction(player_id)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)