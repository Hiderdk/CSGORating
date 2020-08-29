import pandas as pd
filepath_dataframes =r"C:\Users\Mathias\PycharmProjects\Ratings\Files"
import math

#dft = dft[dft['most_recent_date']>'2020-01-01']
#print(dft[['team_name','time_weight_rating','most_recent_date']].head(35))


df_file_name = "all_game_all_player_rating"
dft = pd.read_pickle(filepath_dataframes + "//" + df_file_name).sort_values(by=['start_date_time','game_number'],ascending=[False,False])
q = dft[dft['player_name'].str.lower()=='hades'].sort_values(by='start_date_time',ascending=False).head(10)
v = dft.head(50)
v = dft[dft['player_name']=='hades'].head(10)

df_file_name = "all_game_all_team_rating"
df = pd.read_pickle(filepath_dataframes + "//" + df_file_name).sort_values(by='start_date_time',ascending=False)


v = df[df['team_name']=='Wisła Kraków']



v = df.head(1)
dft['rounds_difference'] = dft['rounds_won']-dft['rounds_lost']
h = dft[(dft['start_date_time']>'2020-04-22')&(dft['team_name']=='BIG')]

print(h[['opponent_adjusted_performance_rating','rounds_difference','opponent_time_weight_rating','won']].mean())



df['rating_difference'] = df['time_weight_rating']-df['opponent_time_weight_rating']

rows = df[df['rating_difference'].between(500,960)]

rows['round_difference'] = rows['rounds_won']-rows['rounds_lost']

q = rows[(rows['round_difference'] > 3.5)]
print(len(q)/len(rows))

q = df[(df['team_name']=='c0ntact')&(df['start_date_time']>'2020-01-15')]
q['rounds_difference'] = df['rounds_won']-df['rounds_lost']
print(q[['opponent_adjusted_performance_rating','rounds_difference','opponent_time_weight_rating']].mean(),len(q))


q = df[(df['team_name']=='Movistar Riders')&(df['start_date_time']>'2020-01-15')]
q['rounds_difference'] = df['rounds_won']-df['rounds_lost']
print(q[['opponent_adjusted_performance_rating','rounds_difference','opponent_time_weight_rating']].mean(),len(q))



