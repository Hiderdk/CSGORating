from SQL import *

import pickle
import pandas as pd
import math

all_game_all_team_rating = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\all_game_all_team_rating")

net_round_wins_regular = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\total_kills_csgo_regular")

net_round_wins_ot = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\total_kills_csgo_ot")
def generate_kills_probability_model():
    game_team_original = get_game_team("2019-03-01")
    game_team_original = pd.merge(game_team_original,all_game_all_team_rating[['game_id','team_id','time_weight_rating','opponent_time_weight_rating']],on=['game_id','team_id'])
    game_team_original['net_rounds'] = game_team_original['rounds_won']-game_team_original['rounds_lost']
    game_team_original['total_rounds'] = game_team_original['rounds_won']+game_team_original['rounds_lost']
    game_team_original['rating_difference'] = game_team_original['time_weight_rating']-game_team_original['opponent_time_weight_rating']
   # game_team_original = game_team_original[abs(game_team_original['rating_difference'])<600]
    probabilities = net_round_wins_regular.predict_proba([[0]])[0]
    probabilities_classes = net_round_wins_regular.classes_.tolist()
    probabilities_ot = net_round_wins_ot.predict_proba([[0]])[0]
    probabilities_ot_classes = net_round_wins_ot.classes_.tolist()



    for ot in range(2):
        if ot == 0:
            filtered_rows = game_team_original[game_team_original['total_rounds']<31]
            game_team = filtered_rows[filtered_rows['rounds_won'] != filtered_rows['rounds_lost']]
        else:
            filtered_rows = game_team_original[game_team_original['total_rounds'] > 31]
            game_team = filtered_rows[filtered_rows['rounds_won'] != filtered_rows['rounds_lost']]
            game_team = game_team[abs(game_team['net_rounds'])<4.5]



        net_rounds = game_team['net_rounds'].unique().tolist()
        so = 0
        kills = game_team['kills'].unique().tolist()
        for kill in kills:
            game_team_kills = game_team[game_team['kills'] == kill]
            mean_all = len(game_team_kills) / len(game_team)

            so += kill * mean_all

        net_rounds_probability_dict = {
        }
        so = 0
        win = 0
        for net_round in net_rounds:
            if net_round == 2:
                h = 3
            if ot == 0:
                index = probabilities_classes.index(net_round)
                round_prob = probabilities[index]
            else:
                index = probabilities_ot_classes.index(net_round)
                round_prob = probabilities_ot[index]

            net_rounds_probability_dict[net_round] = {}
            game_team_rank =  game_team[game_team['net_rounds']==net_round]

            #game_team_rank = game_team

            kills = game_team_rank['kills'].unique().tolist()
            for kill in kills:
                if math.isnan(kill) is True:
                    continue
                game_team_rank_kills = game_team_rank[game_team_rank['kills']==kill]

                mean = len(game_team_rank_kills)/len(game_team_rank)
                net_rounds_probability_dict[net_round][kill] = mean

                if net_round > 0:
                    win +=kill*mean*round_prob


                so+=mean*kill*round_prob
                if math.isnan(so) is True:
                    h = 3

                    #print(kill,net_rounds,mean,round_prob)
        print(so)
        q = 3

        file_name = "ot_" + str(ot)+ "_net_rounds_to_kills"
        with open(r'C:\Users\Mathias\PycharmProjects\Ratings\Files\models/'+ file_name , 'wb') as fp:
            pickle.dump(net_rounds_probability_dict, fp, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    generate_kills_probability_model()