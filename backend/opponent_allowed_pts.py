import requests
from teamid import team_id

def get_opponent_ppg(team_id):
	url = f"https://nba-results-pro.p.rapidapi.com/nba/teams/{team_id}/season/information"

	headers = {
		"x-rapidapi-key": "b7ff177dc6msh0354e8083416a13p185307jsndfdc4d061346",
		"x-rapidapi-host": "nba-results-pro.p.rapidapi.com"
	}

	response = requests.get(url, headers=headers)
	data =response.json()

	allowed_ppg = data['points_allowed_per_game']
	print(allowed_ppg)

get_opponent_ppg(team_id)