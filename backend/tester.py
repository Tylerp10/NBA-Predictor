import requests

def import_name(name):
    url = "https://api-nba-v1.p.rapidapi.com/players"

    querystring = {"search": name}

    headers = {
        "x-rapidapi-key": "b7ff177dc6msh0354e8083416a13p185307jsndfdc4d061346",
        "x-rapidapi-host": "api-nba-v1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    return response.json()

import_name('james')


url = "https://api-nba-v1.p.rapidapi.com/players/statistics"

querystring = {"id":"265","season":"2024"}

headers = {
	"x-rapidapi-key": "b7ff177dc6msh0354e8083416a13p185307jsndfdc4d061346",
	"x-rapidapi-host": "api-nba-v1.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

data = response.json()

# Extract last 5 games
games = data.get("response", [], )[-5:]


# Process data
player_stats = []
for game in games:
    stats = {
        "points": game.get("points", 0),
        "rebounds": game.get("totReb", 0),
        "assists": game.get("assists", 0),
        "game_id": game['game']['id']
    }
    player_stats.append(stats)

print(player_stats)