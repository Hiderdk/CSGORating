import joblib
import pandas as pd
import numpy as np
from typing import Dict
map_win_models = {
    2: pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\won_game_number2"),
    3: pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\won_game_number3")
}
from Predictions.RoundWinProbability import RoundProbabilityGenerator
round_win_probability_model = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\round_difference_ml")

NET_PERFORMANCE_MULTIPLIER = 1.5

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



    def generate_net_performance(self,round_difference,rating_difference):

        if round_difference > 0:
            round_win_percentage = 16/(16+16-round_difference)
        else:
            round_win_percentage = (16+round_difference)/(16+16+round_difference)

        squared_round_win_percentage = round_win_percentage**self.squared_factor
        squared_round_win_percentage_opponent = (1-round_win_percentage)**self.squared_factor


        adjusted_rounds_win_percentage = squared_round_win_percentage/(squared_round_win_percentage+squared_round_win_percentage_opponent)

        expected_team_performance_raw = (1 / (1 + 10 ** (-rating_difference / self.team_rating_prediction_beta)))
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


    def get_round_difference_prob(self,map_win_probability):
        probs = round_win_probability_model.predict_proba([[map_win_probability]])
        round_win_probs = {}
        rp_prob = 0
        sq = 0
        for number,class_ in enumerate(round_win_probability_model.classes_):
            round_win_probs[class_] = probs[0][number]
            if class_ > 0:
                rp_prob += probs[0][number]

            sq += probs[0][number]

        ratio_diff1 = map_win_probability/rp_prob
        ratio_diff2 = (1-map_win_probability)/(1-rp_prob)
        sq = 0
        for round_difference,prob in round_win_probs.copy().items():

            if round_difference > 0:

                round_win_probs[round_difference] *= ratio_diff1
            elif round_difference < 0:
                round_win_probs[round_difference] *=  ratio_diff2

            sq +=round_win_probs[round_difference]

        return round_win_probs

    def generate_series_probability(self):

        if self.format == "bo3":
            self.generate_bo3()
            self.calculcate_bo3_probability()

        elif self.format == "bo1":
            self.calculcate_bo1_probability()

        else:
            self.round_win_probsmap1 = self.get_round_difference_prob(self.win_probability)
            self.series_result_probability = {}
            self.series_win_probability = [0,0]

        return self.series_win_probability


    def get_implied_rating_difference(self,map_win_probability,lr_model,max_error = 0.003,learning_rate=2000):
        error = 9999
        rating_difference = -9999

        while abs(error) > max_error:
            estimated_map_win_probability = lr_model.predict_proba([[rating_difference,rating_difference]])[0][1]

            error = abs(map_win_probability-estimated_map_win_probability)

            rating_difference +=error*learning_rate

        return rating_difference


    def generate_bo_3_from_map1(self, used_round_difference1, raw_map_win_probability1, raw_map_win_probability2, raw_map_win_probability3,lr_model):
        self.probs = {}


        self.map_score_probabilities = {
            0: {},
            1: {},
            2: {}
        }

        self.map_win_probabilities = {
            0: {0: {0: {'prob': 0}, 1: {'prob': 0}, 'prob': 0}, 1: {0: {'prob': 0}, 1: {'prob': 0}, 'prob': 0},
                'prob': 0},
            1: {0: {0: {'prob': 0}, 1: {'prob': 0}, 'prob': 0}, 1: {0: {'prob': 0}, 1: {'prob': 0}, 'prob': 0},
                'prob': 0},
            'prob': 0,
        }


        self.round_win_probsmap1 = self.get_round_difference_prob(self.win_probability)

        for round_difference1, prob1 in self.round_win_probsmap1.copy().items():

            if used_round_difference1 != round_difference1:
                prob1 = 0
            else:
                prob1 = 1

            implied_rating_difference = self.get_implied_rating_difference(raw_map_win_probability1,lr_model)
            net_performance = self.generate_net_performance(used_round_difference1,implied_rating_difference)
            net_performance = net_performance * NET_PERFORMANCE_MULTIPLIER
            feature_dict = {
                'win_probability': [raw_map_win_probability2],
                'series_net_opponent_adjusted_performance_rating': [net_performance],
                # 'series_round_difference': [0],
            }
            # feature_dict['series_round_difference'] = class_1
            feature_df = pd.DataFrame.from_dict(feature_dict)
            map_win_probability2 = map_win_models[2].predict_proba(feature_df)[0][1]
            game1_result = 0
            if round_difference1 > 0:
                game1_result = 1

            self.map_win_probabilities[game1_result]['prob'] += prob1

            round_win_probs_map2 = self.get_round_difference_prob(map_win_probability2)

            for round_difference2, prob2 in round_win_probs_map2.copy().items():
                # feature_dict['series_round_difference'] = class_2
                if round_difference2 not in self.map_score_probabilities[1]:
                    self.map_score_probabilities[1][round_difference2] = 0
                self.map_score_probabilities[1][round_difference2] += prob1 * prob2

                sum_round_difference =  min(16,used_round_difference1+round_difference2)
                sum_round_difference = max(-16, sum_round_difference)
                net_performance = self.generate_net_performance(sum_round_difference,implied_rating_difference)
                feature_dict = {
                    'win_probability': [raw_map_win_probability3],
                    'series_net_opponent_adjusted_performance_rating': [net_performance],
                    # 'series_round_difference': [0],
                }
                # feature_dict['series_round_difference'] =+ class_2

                game1_result = 0
                game2_result = 0
                if round_difference1 > 0:
                    game1_result = 1
                if round_difference2 > 0:
                    game2_result = 1

                if round_difference2 > 0:
                    game2_result = 1
                self.map_win_probabilities[game1_result][game2_result]['prob'] += prob2

                feature_df = pd.DataFrame.from_dict(feature_dict)
                map_win_probability3 = map_win_models[3].predict_proba(feature_df)[0][1]
                round_win_probs_map3 = self.get_round_difference_prob(map_win_probability3)

                for round_difference3, prob3 in round_win_probs_map3.copy().items():
                    if round_difference3 not in self.map_score_probabilities[2]:
                        self.map_score_probabilities[2][round_difference3] = 0

                    self.map_score_probabilities[2][round_difference3] += prob1 * prob2 * prob3
                    if game1_result == 1 and game2_result == 1 or game1_result == 0 and game2_result == 0:
                        pass
                    else:
                        game3_result = 0
                        if round_difference3 > 0:
                            game3_result = 1

                        if 'prob' not in self.map_win_probabilities[game1_result][game2_result][game3_result]:
                            self.map_win_probabilities[game1_result][game2_result][game3_result]['prob'] = 0

                        self.map_win_probabilities[game1_result][game2_result][game3_result]['prob'] += prob3

        self.calculcate_bo3_probability()


    def calculcate_bo3_probability(self):

        p1 = self.map_win_probabilities[1]['prob'] / (
                    self.map_win_probabilities[0]['prob'] + self.map_win_probabilities[1]['prob'])


        win1p2 = self.map_win_probabilities[1][1]['prob']/(self.map_win_probabilities[1][1]['prob']+self.map_win_probabilities[1][0]['prob'])


        win1loss2p3 = self.map_win_probabilities[1][0][1]['prob']/(self.map_win_probabilities[1][0][1]['prob']+self.map_win_probabilities[1][0][0]['prob'])


        loss1p2 = self.map_win_probabilities[0][1]['prob'] / (
                        self.map_win_probabilities[0][1]['prob'] + self.map_win_probabilities[0][0]['prob'])


        loss1win2p3 = self.map_win_probabilities[0][1][1]['prob'] / (
                        self.map_win_probabilities[0][1][1]['prob'] + self.map_win_probabilities[0][1][0]['prob'])


        self.series_result_probability = {}


        self.series_result_probability['0-2'] = (1-loss1p2)*(1-p1)
        self.series_result_probability['2-0'] =  p1*win1p2
        self.series_result_probability['2-1'] = win1loss2p3*p1*(1-win1p2)+loss1win2p3*(1-p1)*loss1p2
        self.series_result_probability['1-2'] = (1-win1loss2p3)*p1*(1-win1p2)+(1-loss1win2p3)*(1-p1)*loss1p2

        so =  self.series_result_probability['0-2'] + self.series_result_probability['2-0']+    self.series_result_probability['2-1']+   self.series_result_probability['1-2']
        self.series_win_probability = self.series_result_probability['2-1']+ self.series_result_probability['2-0']

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
            0:{0:{0:{'prob':0},1:{'prob':0},'prob':0},1:{0:{'prob':0},1:{'prob':0},'prob':0},'prob':0},
            1:{0:{0:{'prob':0},1:{'prob':0},'prob':0},1:{0:{'prob':0},1:{'prob':0},'prob':0},'prob':0},
            'prob':0,
        }
        self.round_win_probsmap1 = self.get_round_difference_prob(self.win_probability)


        self.sumprob2 = 0
        self.prob1win = 0
        self.prob2win10 = 0
        self.prob2win = 0
        self.prob2winm10 = 0
        for round_difference1,prob1 in self.round_win_probsmap1.copy().items():

            if round_difference1 > 0:
                self.prob1win +=prob1

            if round_difference1 not in self.map_score_probabilities[0]:
                self.map_score_probabilities[0][round_difference1] = 0
            self.map_score_probabilities[0][round_difference1] += prob1
            net_performance = self.generate_net_performance(round_difference1,self.rating_difference)
            net_performance = net_performance*NET_PERFORMANCE_MULTIPLIER
            feature_dict['series_net_opponent_adjusted_performance_rating'] =net_performance
            #feature_dict['series_round_difference'] = class_1
            feature_df = pd.DataFrame.from_dict(feature_dict)
            map_win_probability2 = map_win_models[2].predict_proba(feature_df)[0][1]

            round_win_probs_map2 = self.get_round_difference_prob(map_win_probability2)
            game1_result = 0
            if round_difference1 > 0:
                game1_result = 1

            self.map_win_probabilities[game1_result]['prob'] += prob1

            for round_difference2, prob2 in round_win_probs_map2.copy().items():

                if round_difference1 > 0:
                    self.sumprob2 +=prob1

                if round_difference1 >0 and round_difference2 > 0:
                    self.prob2win10 += prob2

                if round_difference1 >0 and round_difference2 <0:
                    self.prob2winm10 += prob2


                if round_difference2 not in self.map_score_probabilities[1]:
                    self.map_score_probabilities[1][round_difference2] = 0
                self.map_score_probabilities[1][round_difference2] +=prob1*prob2

                sum_round_difference = min(16,round_difference1 + round_difference2)
                sum_round_difference = max(-16, sum_round_difference)

                net_performance = self.generate_net_performance(sum_round_difference,self.rating_difference)
                feature_dict['series_net_opponent_adjusted_performance_rating'] =+ net_performance
                #feature_dict['series_round_difference'] =+ class_2



                game2_result = 0

                if round_difference2 > 0:
                    game2_result = 1
                self.map_win_probabilities[game1_result][game2_result]['prob'] += prob2
                    #self.map_win_probabilities[game1_result][game2_result]['combined_prob'] += combined_prob


                feature_df = pd.DataFrame.from_dict(feature_dict)
                map_win_probability3 = map_win_models[3].predict_proba(feature_df)[0][1]
                round_win_probs_map3 = self.get_round_difference_prob(map_win_probability3)

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

                        if 'prob' not in    self.map_win_probabilities[game1_result][game2_result][game3_result]:
                            self.map_win_probabilities[game1_result][game2_result][game3_result]['prob'] = 0

                        self.map_win_probabilities[game1_result][game2_result][game3_result]['prob'] +=prob3




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


    def calculcate_bo1_probability(self):
        self.round_win_probsmap1 = self.get_round_difference_prob(self.win_probability)
        self.series_result_probability = {}
        self.series_win_probability = self.win_probability

if __name__ == '__main__':
    import time
    format = "bo3"

    st = time.time()
    series_win_probability = SeriesWinProbability(win_probability=0.6,rating_difference=460,format=format)

    series_win_probability.generate_series_probability()
   # probs = series_win_probability.get_probs(feature_dict,2)
    series_win_probability.generate_series_probability()
    print(time.time()-st)