import requests
from flask import jsonify
import os
from dotenv import load_dotenv

load_dotenv()

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


        