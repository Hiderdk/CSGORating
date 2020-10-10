import joblib
import pandas as pd
import numpy as np
from typing import Dict
round_win_models = {
    1: pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\round_difference_game_number1"),
    2: pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\round_difference_game_number2"),
    3: pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\round_difference_game_number2")
}
round_win_model = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\round_difference")

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
            'series_round_difference': [0],
        }


        self.map_score_probabilities = {
            0:{},
            1:{},
            2:{}
        }

        self.probs[0] = self.get_probs(feature_dict,1)
        self.map_win_probabilities = {
            0:{0:{0:0,1:0,'prob':0},1:{0:0,1:0,'prob':0}},
            1:{0:{0:0,1:0,'prob':0},1:{0:0,1:0,'prob':0}},
        }
        for number1,class_1 in enumerate(round_win_model.classes_):
            print(class_1)
            if class_1 not in self.map_score_probabilities[0]:
                self.map_score_probabilities[0][class_1] = 0
            self.map_score_probabilities[0][class_1] += self.probs[0][number1]
            net_performance = self.generate_net_performance(class_1)
            feature_dict['series_net_opponent_adjusted_performance_rating'] =net_performance
            feature_dict['series_round_difference'] = class_1
            self.probs[1] = self.get_probs(feature_dict,2)


            for number2, class_2 in enumerate(round_win_model.classes_):
                #feature_dict['series_round_difference'] = class_2
                if class_2 not in self.map_score_probabilities[1]:
                    self.map_score_probabilities[1][class_2] = 0
                self.map_score_probabilities[1][class_2] +=self.probs[1][number2]*self.probs[0][number1]

                net_performance = self.generate_net_performance(class_2)
                feature_dict['series_net_opponent_adjusted_performance_rating'] =+ net_performance
                feature_dict['series_round_difference'] =+ class_2

                self.probs[2] = self.get_probs(feature_dict,3)
                game1_result = 0
                game2_result = 0
                if class_1 > 0:
                    game1_result = 1
                if class_2 > 0:
                    game2_result = 1

                if game1_result == 1 and game2_result == 1 or game1_result == 0 and game2_result == 0:
                    self.map_win_probabilities[game1_result][game2_result]['prob'] += self.probs[1][number2] * \
                                                                                      self.probs[0][number1]



                for number3, class_3 in enumerate(round_win_model.classes_):
                    if class_3 not in self.map_score_probabilities[2]:
                        self.map_score_probabilities[2][class_3] = 0

                    self.map_score_probabilities[2][class_3] += self.probs[2][number3]*self.probs[1][number2]*self.probs[0][number1]

                    if game1_result == 1 and game2_result == 1 or game1_result == 0 and game2_result == 0:
                        pass
                    else:
                        game3_result = 0
                        if class_3 > 0:
                            game3_result=1

                        self.map_win_probabilities[game1_result][game2_result][game3_result] += self.probs[2][number3]*self.probs[1][number2]*self.probs[0][number1]

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
        probs = round_win_models[game_number].predict_proba(feature_df)[0]
        return probs


    def get_bo1_probability(self):
        pass

if __name__ == '__main__':
    import time
    format = "bo3"
    feature_dict = {
        'prob':0.6,
        'series_round_difference':[0]
    }
    st = time.time()
    series_win_probability = SeriesWinProbability(win_probability=0.61,rating_difference=410,format=format)

    series_win_probability.generate_series_probability()
    print(time.time()-st)