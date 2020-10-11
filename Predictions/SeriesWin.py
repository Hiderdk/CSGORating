import joblib
import pandas as pd
import numpy as np
from typing import Dict
map_win_models = {
    2: pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\won_game_number2"),
    3: pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\won_game_number3")
}
from Predictions.RoundWinProbability import RoundProbabilityGenerator
round_win_probability = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\round_difference_probability")

class SeriesWinProbability():


    def __init__(self,
                 win_probability,
                 format,
                 rating_difference,
                 team_rating_prediction_beta = 4300,
                 performance_multiplier = 42000,
                 squared_factor = 1.25

                 ):

        self.performance_multiplier = performance_multiplier
        self.squared_factor = squared_factor
        self.rating_difference = rating_difference
        self.team_rating_prediction_beta = team_rating_prediction_beta
        self.win_probability = win_probability
        self.format = format



    def generate_net_performance(self,round_difference):

        if round_difference > 0:
            round_win_percentage = 16/(16+round_difference)
        else:
            round_win_percentage = (16+round_difference)/(16+16+round_difference)

        squared_round_win_percentage = round_win_percentage**self.squared_factor
        squared_round_win_percentage_opponent = (1-round_win_percentage)**self.squared_factor


        adjusted_rounds_win_percentage = squared_round_win_percentage/(squared_round_win_percentage+squared_round_win_percentage_opponent)

        expected_team_performance_raw = (1 / (1 + 10 ** (-self.rating_difference / self.team_rating_prediction_beta)))
        opponent_adjusted_performance_ratings =[]
        for player in range(5):

            player_percentage_contribution = 0.2

            expected_player_percentage_contribution = 0.2


            expected_player_performance = expected_player_percentage_contribution * expected_team_performance_raw

            player_performance = player_percentage_contribution * adjusted_rounds_win_percentage
            net = player_performance - expected_player_performance
            opponent_adjusted_performance_ratings.append(net*self.performance_multiplier)

        performance =sum(opponent_adjusted_performance_ratings)/len(opponent_adjusted_performance_ratings)
        return performance


    def generate_series_probability(self):

        if self.format == "bo3":
            self.generate_bo3()
            self.calculcate_bo3_probability()
        elif self.format == "bo1":
            self.get_bo1_probability()


    def generate_bo3(self):

        self.probs = {}

        feature_dict = {
            'win_probability':[self.win_probability],
            'series_net_opponent_adjusted_performance_rating':[0],
           # 'series_round_difference': [0],
        }


        self.map_score_probabilities = {
            0:{},
            1:{},
            2:{}
        }

        self.map_win_probabilities = {
            0:{0:{0:0,1:0,'prob':0},1:{0:0,1:0,'prob':0}},
            1:{0:{0:0,1:0,'prob':0},1:{0:0,1:0,'prob':0}},
        }
        round_win_probsmap1 = round_win_probability.predict_proba(self.win_probability)
        self.to2_prob = 0
        self.to1_prob = 0


        for round_difference1,prob1 in round_win_probsmap1.copy().items():
            if round_difference1 > 0:
                self.to1_prob += prob1

            if round_difference1 not in self.map_score_probabilities[0]:
                self.map_score_probabilities[0][round_difference1] = 0
            self.map_score_probabilities[0][round_difference1] += prob1
            net_performance = self.generate_net_performance(round_difference1)
            net_performance = net_performance*2
            feature_dict['series_net_opponent_adjusted_performance_rating'] =net_performance
            #feature_dict['series_round_difference'] = class_1
            feature_df = pd.DataFrame.from_dict(feature_dict)
            map_win_probability2 = map_win_models[2].predict_proba(feature_df)[0][1]
            if round_difference1 > 0:
                self.to2_prob += prob1*map_win_probability2
            round_win_probs_map2 = round_win_probability.predict_proba(map_win_probability2)

            for round_difference2, prob2 in round_win_probs_map2.copy().items():
                #feature_dict['series_round_difference'] = class_2
                if round_difference2 not in self.map_score_probabilities[1]:
                    self.map_score_probabilities[1][round_difference2] = 0
                self.map_score_probabilities[1][round_difference2] +=prob1*prob2

                net_performance = self.generate_net_performance(round_difference2)
                feature_dict['series_net_opponent_adjusted_performance_rating'] =+ net_performance
                #feature_dict['series_round_difference'] =+ class_2


                game1_result = 0
                game2_result = 0
                if round_difference1 > 0:
                    game1_result = 1
                if round_difference2 > 0:
                    game2_result = 1

                if game1_result == 1 and game2_result == 1 or game1_result == 0 and game2_result == 0:
                    combined_prob = prob2 * prob1

                    self.map_win_probabilities[game1_result][game2_result]['prob'] += combined_prob
                feature_df = pd.DataFrame.from_dict(feature_dict)
                map_win_probability3 = map_win_models[3].predict_proba(feature_df)[0][1]
                round_win_probs_map3 = round_win_probability.predict_proba(map_win_probability3)

                for round_difference3, prob3 in round_win_probs_map3.copy().items():
                    if round_difference3 not in self.map_score_probabilities[2]:
                        self.map_score_probabilities[2][round_difference3] = 0

                    self.map_score_probabilities[2][round_difference3] += prob1*prob2*prob3
                    if game1_result == 1 and game2_result == 1 or game1_result == 0 and game2_result == 0:
                        pass
                    else:
                        game3_result = 0
                        if round_difference3 > 0:
                            game3_result=1

                        self.map_win_probabilities[game1_result][game2_result][game3_result] += prob1*prob2*prob3

    def calculcate_bo3_probability(self):

        self.series_result_probability = {}
        self.series_result_probability['0-2'] = self.map_win_probabilities[0][0]['prob']
        self.series_result_probability['2-0'] = self.map_win_probabilities[1][1]['prob']
        self.series_result_probability['2-1'] = self.map_win_probabilities[1][0][1]+self.map_win_probabilities[0][1][1]
        self.series_result_probability['1-2'] = self.map_win_probabilities[1][0][0] + self.map_win_probabilities[0][1][
            0]

        so =  self.series_result_probability['0-2'] + self.series_result_probability['2-0']+    self.series_result_probability['2-1']+   self.series_result_probability['1-2']
        print(self.series_result_probability)


    def get_probs(self,feature_dict:Dict,game_number: int)->np.ndarray:
        if game_number == 1:
            feature_dict = {'win_probability':feature_dict['win_probability']}
        feature_df = pd.DataFrame.from_dict(feature_dict)
        probs = map_win_models[game_number].predict_proba(feature_df)[0]
        return probs

    def sum_probs_to_map_win_probability(sel,game_number,probs:np.ndarray):
        prob = 0
        for number,class_ in enumerate(map_win_models[game_number].classes_):
            if class_ > 0:
                prob+=probs[number]

        return prob


    def get_bo1_probability(self):
        pass

if __name__ == '__main__':
    import time
    format = "bo3"

    st = time.time()
    series_win_probability = SeriesWinProbability(win_probability=0.64,rating_difference=700,format=format)

    series_win_probability.generate_series_probability()
   # probs = series_win_probability.get_probs(feature_dict,2)
    series_win_probability.generate_series_probability()
    print(time.time()-st)