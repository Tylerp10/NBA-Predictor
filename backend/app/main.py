from flask import jsonify, Flask, request
from flask_cors import CORS
from team_fetcher import teams
from player_fetcher import player_fetcher
from data_fetcher import stats_fetcher
from games_fetcher import games
from odds_fetcher import odds_fetcher
from player_props import player_props_fetcher
from predictionmodel import prediction_model


app = Flask("__name__")
CORS(app)

FRONTEND_DOMAIN = "https://hoopscope.ca"

CORS(app, resources={r"/*": {"origins": FRONTEND_DOMAIN}})

@app.route('/')
def home():
    return jsonify({"message": "API is working!"})

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
        return jsonify({'Error'})
    
    market_id = request.args.get("market_id")
    if not market_id:
        return jsonify({'Error'})
    
    return odds_fetcher(odds_id, market_id)

#PLAYER PROPS DATA----------------------------------------------
@app.route('/playerprops', methods=["GET"])
def player_props():

    odds_id = request.args.get("odds_id")
    if not odds_id:
        return jsonify({"Error"})
    
    player_prop_market = request.args.get("player_prop_market")
    if not player_prop_market:
        return jsonify({"Error"})
    

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


def handler(event, context):
    return app(event, context)
