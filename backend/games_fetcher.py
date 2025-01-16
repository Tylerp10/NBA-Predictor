import requests
import os
from dotenv import load_dotenv

load_dotenv()

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