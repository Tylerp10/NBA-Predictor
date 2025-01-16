import requests
import os
from dotenv import load_dotenv
from flask import jsonify

load_dotenv()

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





