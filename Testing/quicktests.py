import pandas as pd
filepath_dataframes =r"C:\Users\Mathias\PycharmProjects\Ratings\Files"
import math

df_file_name = "all_team"
dft = pd.read_pickle(filepath_dataframes + "//" + df_file_name).sort_values(by='time_weight_rating',ascending=False)


df_file_name = "process_all_game_all_player_rating"
dft = pd.read_pickle(filepath_dataframes + "//" + df_file_name).sort_values(by=['start_date_time','game_number'],ascending=[True,True])

q = dft.head(4500)
dft[dft['player_id']==1437]
q = dft[dft['opponent_region'].isna()]
q = dft[dft['time_weight_rating'].isna()]

t = dft[dft['player_name']=='iDISBALANCE']
r = t[t['game_id']==64541]['opponent_region'].iloc[0]
if math.isnan(r) is True:
    h = 3
df_file_name = "all_game_all_team_rating"
df = pd.read_pickle(filepath_dataframes + "//" + df_file_name).sort_values(by='start_date_time',ascending=False)

t = df[df['team_name']=='Astralis']
q = 3