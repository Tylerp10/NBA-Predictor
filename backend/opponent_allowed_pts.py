import requests

headers = {
	"x-rapidapi-key": "b7ff177dc6msh0354e8083416a13p185307jsndfdc4d061346",
	"x-rapidapi-host": "nba-results-pro.p.rapidapi.com"
}

def get_team_id(team_name):

	url = "https://nba-results-pro.p.rapidapi.com/nba/teams"

	response = requests.get(url, headers=headers)
	data = response.json()

	teams = data.get('teams')
	team_dict = {team.get('team_abbreviation'): team.get('team_id') for team in teams}

	return team_dict.get(team_name)


def get_opponent_ppg(team_id):
	
	url = f"https://nba-results-pro.p.rapidapi.com/nba/teams/{team_id}/season/information"


	response = requests.get(url, headers=headers)
	data =response.json()

	allowed_ppg = data['points_allowed_per_game']

	return allowed_ppg
