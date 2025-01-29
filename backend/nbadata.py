from flask import jsonify
import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

# GET TEAMS------------------------------------------------
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

# GET PLAYERS------------------------------------------------
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

# GET PLAYER AVERAGES------------------------------------------------
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


# GET ODDS------------------------------------------------
api = os.getenv("ODDS_KEY")

events_url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/events?apiKey={api}&_={int(time.time())}"
headers = {
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}
response = requests.get(events_url, headers=headers)

if response.status_code == 200:
    games_data = response.json()
    games = {}

    for game in games_data:
        game_id = game["id"]
        matchup = game["home_team"] + " vs " + game["away_team"]
        games[matchup] = game_id        
else:
    print(response.status_code)


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

# GET PLAYER PROP ODDS------------------------------------------------
def player_props_fetcher(game_id, player_prop_market):
    api = os.getenv("ODDS_KEY")


    odds_url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/events/{game_id}/odds?apiKey={api}&regions=us&markets={player_prop_market}&oddsFormat=american"

    response = requests.get(odds_url)

    if response.status_code == 200:
        data = response.json()
        player_props = {}
        
        for bookmaker in data.get("bookmakers", []):
            bookmaker_name = bookmaker.get("title")
            player_props[bookmaker_name] = {}
        
            for market in bookmaker.get("markets", []):  
                market_key = market.get("key")
                outcomes = market.get("outcomes", [])
                
                player_outcomes = [
                    {"player": outcome.get("description"),
                     "Line": outcome.get("name"),
                     "Value": outcome.get("point"),
                     "odds": outcome.get("price"), }
                    for outcome in outcomes
                ]
                if player_outcomes:
                    player_props[bookmaker_name][market_key] = player_outcomes


        return jsonify(player_props)

    else:
        return jsonify("Error Fetching Player Props")
