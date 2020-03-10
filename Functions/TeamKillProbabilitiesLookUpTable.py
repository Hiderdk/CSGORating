from SQL import *

import pickle
import pandas as pd

def generate_kills_probability_model():
    game_team_original = get_game_team("2019-01-01")
    game_team_original['net_rounds'] = game_team_original['rounds_won']-game_team_original['rounds_lost']
    for ot in range(2):
        if ot == 0:
            game_team = game_team_original[(game_team_original['rounds_won']+game_team_original['rounds_lost']<=30) & game_team_original['rounds_won']!=15]
        else:
            game_team = game_team_original[
                (game_team_original['rounds_won'] + game_team_original['rounds_lost'] >30) & game_team_original[
                    'rounds_won'] != game_team_original[
                    'rounds_lost']]
        net_rounds = game_team['net_rounds'].unique().tolist()
        net_rounds_probability_dict = {
        }
        so = 0
        for net_rounds in net_rounds:
            net_rounds_probability_dict[net_rounds] = {}
            game_team_rank =  game_team[game_team['net_rounds']==net_rounds]
            kills = game_team_rank['kills'].unique().tolist()
            for kill in kills:
                game_team_rank_kills = game_team_rank[game_team_rank['kills']==kill]
                mean = len(game_team_rank_kills)/len(game_team_rank)
                net_rounds_probability_dict[net_rounds][kill] = mean
                so +=kill*mean

        print(so)
        file_name = "ot_" + str(ot)+ "_net_rounds_to_kills"
        with open(r'C:\Users\Mathias\PycharmProjects\Ratings\Files\models/'+ file_name , 'wb') as fp:
            pickle.dump(net_rounds_probability_dict, fp, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    generate_kills_probability_model()