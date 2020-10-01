import pandas as pd
filepath_dataframes =r"C:\Users\Mathias\PycharmProjects\Ratings\Files"
import math
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
#dft = dft[dft['most_recent_date']>'2020-01-01']
#print(dft[['team_name','time_weight_rating','most_recent_date']].head(35))
df_file_name = "all_game_all_player_rating"
all_game_all_player =  pd.read_pickle(filepath_dataframes + "//" + df_file_name).sort_values(by=['start_date_time','game_number'])



group_sum = all_game_all_player.groupby(['team_id', 'game_id'])['kills'].sum().reset_index()



all_game_all_team = all_game_all_player.groupby(
    ['opponent_region', 'rounds_won', 'rounds_lost', 'team_id', 'team_name', 'team_id_opponent', 'game_id',
     'start_date_time', 'game_number', 'series_id'])[
    ['opponent_adjusted_performance_rating', 'won', 'time_weight_rating',
     'time_weight_rating_certain_ratio']].mean().reset_index()


print(all_game_all_team.sort_values(by=['start_date_time','game_number'])['start_date_time'].iloc[0])
# self.all_game_all_team =  merge_dataframes_on_different_column_names_on_right(self.all_team,self.all_game_all_team,"team_id","team_id")
all_game_all_team = pd.merge(group_sum, all_game_all_team, on=['team_id', 'game_id'])
all_game_all_team['lost'] = -all_game_all_team['won'] + 1
sub_df = all_game_all_team[
    ['time_weight_rating_certain_ratio', 'time_weight_rating', 'game_id', 'team_id_opponent']]. \
    rename(columns={"time_weight_rating": "opponent_time_weight_rating",
                    "time_weight_rating_certain_ratio": "opponent_time_weight_rating_certain_ratio"})

all_game_all_team = pd.merge(sub_df, all_game_all_team, left_on=['game_id', 'team_id_opponent'],
                                  right_on=['game_id', 'team_id'])



def get_logloss(df,target,feature):
    X = df[feature]
    model = LogisticRegression().fit(X ,df[target])
    prob = model.predict_proba(X )

    return log_loss(df[target],prob)

all_game_all_team = all_game_all_team[all_game_all_team['start_date_time']<'2016-07-01']

all_game_all_team = all_game_all_team[all_game_all_team['game_number']==1]
all_game_all_team['rating_difference'] = all_game_all_team['time_weight_rating'] - \
                                                  all_game_all_team['opponent_time_weight_rating']
print(len(all_game_all_team),get_logloss(all_game_all_team,"won",["rating_difference"]))


df_file_name = "process_all_game_all_player_rating"
dft = pd.read_pickle(filepath_dataframes + "//" + df_file_name).sort_values(by=['start_date_time','game_number'],ascending=[False,False])

ov = dft[dft['time_weight_rating']>dft['opponent_time_weight_rating']]
print((ov['adjusted_rounds_win_percentage']-ov["expected_team_performance"]).mean())

ov = dft[dft['expected_player_percentage_contribution']>0.2]
print((ov['player_percentage_contribution']-ov['expected_player_percentage_contribution']).mean())



rows = dft[dft['player_name']=='Davidp'].sort_values(by=['start_date_time','game_number'],ascending=[True,True])

q = 3