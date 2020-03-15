import pandas as pd
import datetime

def create_average_over_under_df(all_game_all_player,team_player_ids,player_id_to_player_name,name='3M Stats',months_back=3):
    stats_dict = {
        name:[]
    }
    stats_dict['3M Stats'].append('Games Played')
    for kill_value in range(12, 21):
        stats_dict['3M Stats'].append("Over " + str ( kill_value+0.5))

    min_date = datetime.datetime.now()- datetime.timedelta(months_back*365/12)

    filtered_game_all_player = all_game_all_player[all_game_all_player['start_date_time']>min_date]
    for team in team_player_ids:
        for player_id in team_player_ids[team]:
            player_name = player_id_to_player_name[player_id]
            filtered_game_single_player = filtered_game_all_player[filtered_game_all_player['player_id']==player_id]
            stats_dict[player_name] = []
            games_played = len(filtered_game_single_player)
            stats_dict[player_name].append(games_played)

            for kill_value in range(12,21):
                over_rows = filtered_game_single_player[filtered_game_single_player['kills']>kill_value]
                frequency = len(over_rows)/len(filtered_game_single_player)
                str_frequency = str(round(frequency*100,0)) + "%"
                stats_dict[player_name].append(str_frequency)

    return pd.DataFrame.from_dict(stats_dict)


def get_mean_from_pandas_series(series):
    if len(series) >= 1:
        return series.mean()
    else:
        return 0

def get_average_value_from_column_name(df,column_name):

    series = df[column_name].dropna()

    return get_mean_from_pandas_series(series)