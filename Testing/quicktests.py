import pandas as pd
filepath_dataframes =r"C:\Users\Mathias\PycharmProjects\Ratings\Files"
import math
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
#dft = dft[dft['most_recent_date']>'2020-01-01']
#print(dft[['team_name','time_weight_rating','most_recent_date']].head(35))
df = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\_newall_game_all_team_rating")
df['rating_difference'] = df['time_weight_rating']-df['opponent_time_weight_rating']
df['rating_difference'] = df['time_weight_rating']-df['opponent_time_weight_rating']
from SQL import get_series_team
min_date = "2019-10-01"
series_team = get_series_team(min_date)

game1df = df[df['game_number']==1]

series_team = pd.merge(series_team,game1df[['rating_difference','series_id','team_id']],on=['series_id','team_id'])
series_team = series_team[series_team['format']=='bo3']

rows = series_team[series_team['rating_difference'].between(180,700)]
print(len(rows))
print(rows.rating_difference.mean())
for won in range(3):
    for lost in range(3):

        pr = rows[(rows['games_won']==won)&(rows['games_lost']==lost)]
        print(won,lost,len(pr)/len(rows))

