from flask import jsonify, Flask, request
from flask_cors import CORS
from model import teams, player_fetcher, stats_fetcher, games, odds_fetcher, player_props_fetcher, prediction_model, run_prediction, get_opponent_defense_stats, get_next_game, get_recent_performance, get_player_info, get_info


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


@app.route('/info', methods=['GET'])
def info():
    player_id = request.args.get('player_id')
    info = get_info(player_id)
    return jsonify(info)

@app.route('/player_info', methods=['GET'])
def player_info():
    player_name = request.args.get('player_name')
    if not player_name:
        return jsonify({"error": "player_name is required"}), 400

    player_info = get_player_info(player_name)
    if not player_info:
        return jsonify({"error": "Player not found"}), 404

    return jsonify(player_info)


@app.route('/player_performance', methods=['GET'])
def player_performance():
    player_id = request.args.get('player_id')
    if not player_id:
        return jsonify({"error": "player_id is required"}), 400

    performance_data = get_recent_performance(player_id)
    if not performance_data:
        return jsonify({"error": "Could not retrieve player performance data"}), 500

    return jsonify(performance_data)


@app.route('/next_game', methods=['GET'])
def next_game():
    player_id = request.args.get('player_id')
    team_id = request.args.get('team_id')
    if not player_id or not team_id:
        return jsonify({"error": "player_id and team_id are required"}), 400

    next_game = get_next_game(player_id, team_id)
    if not next_game:
        return jsonify({"error": "No upcoming games found"}), 404

    return jsonify(next_game)


@app.route('/opponent_defense', methods=['GET'])
def opponent_defense():
    opponent_id = request.args.get('opponent_id')
    if not opponent_id:
        return jsonify({"error": "opponent_id is required"}), 400

    opponent_defense = get_opponent_defense_stats(opponent_id)
    if opponent_defense is None:
        return jsonify({"error": "Could not retrieve opponent defensive stats"}), 500

    return jsonify({"opponent_allowed_points": opponent_defense})


@app.route('/predict', methods=['GET'])
def predict():
    player_name = request.args.get('player_name')
    if not player_name:
        return jsonify({"error": "player_name is required"}), 400

    prediction = prediction_model(player_name)
    return jsonify(prediction)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)