import requests
from datetime import datetime, UTC
from teamid import team_name

def get_next_opp(team_name):
    API_KEY = "e66cbb3731f14beda2b155087756ad48"

    URL = "https://api.sportsdata.io/v3/nba/scores/json/Games/2025"

    headers = {
        "Ocp-Apim-Subscription-Key": API_KEY
    }

    response = requests.get(URL, headers=headers)

    if response.status_code == 200:
        games = response.json()
        today = datetime.now(UTC)

        for game in games:
            game_date_str = game.get("Day")  
            if not game_date_str:
                continue 
            
            game_date = datetime.strptime(game_date_str, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=UTC)

            if game_date > today:
                if game["HomeTeam"] == team_name:
                    opponent = game["AwayTeam"]
                    return {
                        "opponent": opponent,
                        "date": game_date
                    }
                elif game["AwayTeam"] == team_name:
                    opponent = game["HomeTeam"]
                    return {
                        "opponent": opponent,
                        "date": game_date
                    }

