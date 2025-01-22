import requests

url = "https://nba-results-pro.p.rapidapi.com/nba/teams"

headers = {
     "x-rapidapi-key": "b7ff177dc6msh0354e8083416a13p185307jsndfdc4d061346",
    "x-rapidapi-host": "nba-results-pro.p.rapidapi.com"
}

response = requests.get(url, headers=headers)

data = response.json()

teams = data.get('teams')

team_dict = {team.get('team_abbreviation'): team.get('team_id') for team in teams}


def get_team_id(team_name):
    return team_dict.get(team_name)

team_name = "LAC"
team_id = get_team_id(team_name)
print(team_id)