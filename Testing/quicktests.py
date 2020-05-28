import pandas as pd
filepath_dataframes =r"C:\Users\Mathias\PycharmProjects\Ratings\Files"
import math

#df_file_name = "all_team"
#dft = pd.read_pickle(filepath_dataframes + "//" + df_file_name).sort_values(by=['time_weight_rating'],ascending=[False])
#dft = dft[dft['most_recent_date']>'2020-01-01']
#print(dft[['team_name','time_weight_rating','most_recent_date']].head(35))


df_file_name = "all_game_all_player_rating"
dft = pd.read_pickle(filepath_dataframes + "//" + df_file_name).sort_values(by=['start_date_time','game_number'],ascending=[True,True])
q = dft[dft['player_name'].str.lower()=='acor'].sort_values(by='start_date_time',ascending=False).head(10)

dft[dft['player_name']=='ottoNd']

df_file_name = "all_game_all_team_rating"
df = pd.read_pickle(filepath_dataframes + "//" + df_file_name).sort_values(by='start_date_time',ascending=False)


q = df[(df['team_name']=='c0ntact')&(df['start_date_time']>'2020-01-15')]
q['rounds_difference'] = df['rounds_won']-df['rounds_lost']
print(q[['opponent_adjusted_performance_rating','rounds_difference','opponent_time_weight_rating']].mean(),len(q))


q = df[(df['team_name']=='Movistar Riders')&(df['start_date_time']>'2020-01-15')]
q['rounds_difference'] = df['rounds_won']-df['rounds_lost']
print(q[['opponent_adjusted_performance_rating','rounds_difference','opponent_time_weight_rating']].mean(),len(q))



