import trueskill
from trueskill_generator.game_team import  create_game_team_trueskill
from trueskill_generator.game_player import  create_game_player_trueskill
import pandas as pd
from sklearn.metrics import log_loss
from sklearn.linear_model import LogisticRegression
import pickle
from SQL import *
import numpy as np
from trueskill import Rating

def create_all_game_all_team():
    filepath_dataframes =r"C:\Users\Mathias\PycharmProjects\Ratings\Files"
    df_file_name = "_newall_game_all_player_rating"
    all_game_all_player =  pd.read_pickle(filepath_dataframes + "//" + df_file_name).sort_values(by=['start_date_time','game_number'])
    all_game_all_player = all_game_all_player[all_game_all_player['start_date_time'].between('2015-07-01','2028-02-01')]


    group_sum = all_game_all_player.groupby(['team_id', 'game_id'])['kills'].sum().reset_index()



    all_game_all_team = all_game_all_player.groupby(
        ['opponent_region', 'rounds_won', 'rounds_lost', 'team_id', 'team_name', 'team_id_opponent', 'game_id',
         'start_date_time', 'game_number', 'series_id'])[
        ['opponent_adjusted_performance_rating', 'won', 'time_weight_rating',
         'time_weight_rating_certain_ratio']].mean().reset_index()

    # self.all_game_all_team =  merge_dataframes_on_different_column_names_on_right(self.all_team,self.all_game_all_team,"team_id","team_id")
    all_game_all_team = pd.merge(group_sum, all_game_all_team, on=['team_id', 'game_id'])
    all_game_all_team['lost'] = -all_game_all_team['won'] + 1
    sub_df = all_game_all_team[
        ['time_weight_rating_certain_ratio', 'time_weight_rating', 'game_id', 'team_id_opponent']]. \
        rename(columns={"time_weight_rating": "opponent_time_weight_rating",
                        "time_weight_rating_certain_ratio": "opponent_time_weight_rating_certain_ratio"})

    all_game_all_team = pd.merge(sub_df, all_game_all_team, left_on=['game_id', 'team_id_opponent'],
                                      right_on=['game_id', 'team_id'])


sigma = 3
beta = 5
tau = 0.025
start_rating_quantile = 18

start_rating_regions = {'Europe': 28, 'Africa': 23, 'Asia': 23,
                        'North America': 26, 'South America': 24,
                        'Middle East': 23, 'Oceania': 23, 'Brazil': 24, None: 23, 'unknown': 23}

def run_trueskill(newest_games_only=False,min_date="2015-07-01"):
    if newest_games_only:
        all_game_ids = get_all_game_ids(min_date)['game_id'].unique().tolist()
        updated_game_team = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\trueskill_game_team")
        updated_game_ids = updated_game_team['game_id'].unique().tolist()
        #new_game_ids = np.setdiff1d(all_game_ids,updated_game_ids)
        new_game_ids =[item for item in all_game_ids if item not in updated_game_ids]


        with open(r'C:\Users\Mathias\PycharmProjects\Ratings/Files/player_ratings', 'rb') as f:
            player_ratings = pickle.load(f)
        with open(r'C:\Users\Mathias\PycharmProjects\Ratings/Files/region_players_rating', 'rb') as f:
            region_players_rating = pickle.load(f)
        with open(r'C:\Users\Mathias\PycharmProjects\Ratings/Files/region_players', 'rb') as f:
            region_players = pickle.load(f)


    else:
        player_ratings = {}
        region_players_rating = {}
        region_players = {}
        new_game_ids = get_all_game_ids(min_date)['game_id'].unique().tolist()

    new_game_player= get_all_game_all_player_from_game_ids(new_game_ids)
    trueskill.setup(draw_probability=0)




    if len(new_game_player) > 0:
        env = trueskill.setup(sigma=sigma, beta=beta, tau=tau)
        new_game_team,player_ratings,region_players,region_players_rating = create_game_player_trueskill(new_game_player, env, start_rating_quantile,
                                                                                                         start_rating_regions=start_rating_regions,
                                                                                                         player_ratings=player_ratings,
                                                                                                         region_players_rating=region_players_rating,
                                                                                                         region_players=region_players)
        print(len(player_ratings))
        if newest_games_only:
            game_team = updated_game_team.append(new_game_team)
        else:
            game_team = new_game_team.copy()

        game_team.to_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\trueskill_game_team")
        with open(r'C:\Users\Mathias\PycharmProjects\Ratings/Files/player_ratings', 'wb') as f:
            pickle.dump(player_ratings, f, pickle.HIGHEST_PROTOCOL)

        with open(r'C:\Users\Mathias\PycharmProjects\Ratings/Files/region_players', 'wb') as f:
            pickle.dump(region_players, f, pickle.HIGHEST_PROTOCOL)

        with open(r'C:\Users\Mathias\PycharmProjects\Ratings/Files/region_players_rating', 'wb') as f:
            pickle.dump(region_players_rating, f, pickle.HIGHEST_PROTOCOL)

    else:
        print("Ts no new games found")



if __name__ == '__main__':

    run_trueskill(newest_games_only=False)