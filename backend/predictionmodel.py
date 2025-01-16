from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog, commonplayerinfo, playernextngames, teamdashboardbygeneralsplits
from errorhandler import make_request_with_retries
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

def prediction_model(player_name):
    # LOOP THROUGH ALL ACTIVE PLAYERS TO FIND SELECTED PLAYER
    season = '2024-25'
    all_players = players.get_active_players()
    # player_name = "Julius Randlde"
    player = next((p for p in all_players if p['full_name'] == player_name), None)

    # GRAB PLAYER ID AND NAME 
    if player:
        # print(f"Player found: {player['full_name']}, {player['id']}")
        player_id = player['id']

    # GET PLAYER INFO 
        player_info = make_request_with_retries(commonplayerinfo.CommonPlayerInfo, 3 ,2, player_id=player_id)
        player_data = player_info.get_data_frames()[0]

        team_id = player_data.loc[0, 'TEAM_ID']
        team_name = player_data.loc[0, 'TEAM_NAME']
        team_abbr = player_data.loc[0, 'TEAM_ABBREVIATION']
        # print(f"Player's Team: {team_name}, {team_abbr}, ID: {team_id}")

    # GET PLAYER RECENT PERFORMANCES
        player_logs = make_request_with_retries(playergamelog.PlayerGameLog, 3, 2, player_id=player_id, season=season)
        player_logs_df = player_logs.get_data_frames()[0]

        player_logs_df = player_logs_df.head(5)
        recent_performances = player_logs_df[['GAME_DATE', 'MATCHUP', 'WL', 'AST', 'REB', 'PTS']].head().to_dict(orient='records')
            
        points = player_logs_df['PTS'].tolist()
        points_list = [int(value) for value in points]
            

    else:
        print("Player not found")

    # FETCH PLAYERS NEXT GAME 
    next_games = make_request_with_retries(playernextngames.PlayerNextNGames, 3, 2, player_id=player_id, number_of_games=1)
    next_games_df = next_games.get_data_frames()[0]

    # FIGURE OUT OPPONENT TEAM NAME 
    game = next_games_df.iloc[0]
    if game["HOME_TEAM_ID"] == team_id:
        opponent_id = game["VISITOR_TEAM_ID"]
        opponent_name = game["VISITOR_TEAM_NAME"]
        player_team = game["HOME_TEAM_NAME"]
    else:
        opponent_id = game["HOME_TEAM_ID"]
        opponent_name = game["HOME_TEAM_NAME"]
        player_team = game["VISITOR_TEAM_NAME"]

    game_date = game['GAME_DATE']

    # print(f"Opponent ID is {opponent_id}, {opponent_name}, {game['GAME_DATE']}")

    # GET OPPONENT DEFENSIVE STATS 
    team_stats = make_request_with_retries(teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits, 3, 2,
        season=season,
        team_id=opponent_id, 
        measure_type_detailed_defense='Opponent'
    )

    team_stats_df = team_stats.get_data_frames()[0]

    # CALCULATE AMOUNT OF POINTS OPPONENT ALLOWS PER GAME  
    team_total_oppg = team_stats_df['OPP_PTS']
    team_gp = team_stats_df['GP']
    team_oppg = team_total_oppg/team_gp
    opponent_allowed_points = team_oppg.iloc[0]

    # print(f'{opponent_name} allows {opponent_allowed_points} per game')


    # PREDICTION MODEL 

    points_list.append(int(opponent_allowed_points))

    # SAMPLE DATA - POINTS FROM PLAYERS PAST 5 GAMES + NEXT OPPONENT ALLOWED PPG
    X = [
        [25, 28, 22, 24, 30, 112],
        [15, 18, 12, 20, 22, 105],
        [35, 40, 38, 45, 37, 115],
        [10, 12, 8, 11, 9, 95],
        [20, 25, 22, 18, 26, 108],
        [30, 28, 25, 32, 31, 110],
        [18, 20, 22, 21, 19, 107],
        [40, 38, 42, 37, 35, 120],
        [12, 10, 8, 14, 11, 98],
        [22, 24, 25, 23, 27, 109],
        [25, 28, 22, 24, 30, 118],  
        [15, 18, 12, 20, 22, 115],  
        [35, 40, 38, 45, 37, 125],
        [10, 12, 8, 11, 9, 100],
        [20, 25, 22, 18, 26, 114]
    ]
    # ACTUAL SCORES
    y = [
        27, 19, 43, 10, 24, 29, 21, 41, 12, 26, 29, 21, 45, 11, 25
    ]

    # Splitting data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Model initialization and training
    model = LinearRegression()
    model.fit(X_train, y_train)

    prediction = points_list
    predicted_points = model.predict([prediction]).tolist()
    # print(f'Predicted points: {predicted_points}')

    return  {
        "player_name": player_name,
        "player_team": player_team,
        "recent_performance": recent_performances,
        "next_opponent": opponent_name,
        "game_date": game_date,
        "opponent_allowed_points": opponent_allowed_points,
        "predicted_points": predicted_points
    }


