import requests
from flask import jsonify
import os
from dotenv import load_dotenv

load_dotenv()

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