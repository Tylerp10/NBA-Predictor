import requests
import os
from dotenv import load_dotenv

load_dotenv()

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