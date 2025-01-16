import requests
import os
from dotenv import load_dotenv
from flask import jsonify

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