import numpy as np
import random
from tqdm import tqdm

OT_VALUES = [15,18,21,24,27,30,33,36,39,42,45,48,51,54,57,60,63,66,69,72,75,78]

import pandas as pd

class RoundProbabilityGenerator():

    def __init__(self,simulations=28000,threshold_count=100,start_map_to_round_div=5,start_momentum_factor=0.037 ):
        self.threshold_count = threshold_count
        self.simulations = simulations
        self.start_map_to_round_div = start_map_to_round_div
        self.start_momentum_factor = start_momentum_factor

    def fit(self,df,probability_name="prob"):
        self.probability_name = probability_name
        self.fit_map_to_round_div()
        self.fit_momentum(df)
        start_value = 0
        step_value = (1-start_value)/self.threshold_count

        self.max_probability_to_round_probabilities = {}

        pbar = tqdm([i for i in range(self.threshold_count)])
        for threshold_number in pbar:

            min_win_probability = start_value+threshold_number*step_value
            max_win_probability = start_value+(1+threshold_number)*step_value
            average_map_probability = min_win_probability*0.5+max_win_probability*0.5

            value = np.log((average_map_probability) / (1 - (average_map_probability)))
            round_win_probability = 1 / (1 + 10 ** (-value / self.map_to_round_div))
            _,round_outcomes = self.simulate(round_win_probability)
            _,round_probs = self.get_simulated_average_round_difference(round_outcomes)
            self.max_probability_to_round_probabilities[max_win_probability] = round_probs

    def fit_momentum(self,df,probability_name="prob",max_error=0.07):
        df['round_difference'] = df['rounds_won'] - df['rounds_lost']
        map_probability = 0.6
        min_map_probability = map_probability-0.03
        max_map_probability = map_probability+0.03
        value = np.log((map_probability) / (1 - (map_probability)))
        round_win_probability = 1 / (1 + 10 ** (-value / self.map_to_round_div))
        _, round_outcomes = self.simulate(round_win_probability)
        error = 999
        learned_rate = 0.01
        rows = df[df[probability_name].between(min_map_probability, max_map_probability)]
        average_historical_round_difference = rows['round_difference'].mean()

        self.momentum_factor = self.start_momentum_factor

        while abs(error) > max_error:
            round_win_probability = 1 / (1 + 10 ** (-value / self.map_to_round_div))
            _, round_outcomes = self.simulate(round_win_probability,momentum_factor=self.momentum_factor)
            simulated_average_round_difference,_ = self.get_simulated_average_round_difference(round_outcomes)
            error = simulated_average_round_difference - average_historical_round_difference
            self.momentum_factor-= error * learned_rate



    def fit_map_to_round_div(self,max_error=0.005):

        map_probability = 0.65
        value = np.log((map_probability) / (1 - (map_probability)))
        error = 999
        learned_rate = 10
        self.map_to_round_div = self.start_map_to_round_div

        while abs(error) > max_error:
            round_win_probability = 1 / (1 + 10 ** (-value /   self.map_to_round_div ))
            simulated_map_probability,round_outcomes = self.simulate(round_win_probability)
            error = simulated_map_probability-map_probability
            self.map_to_round_div +=error*learned_rate


    def simulate(self,round_win_probability,momentum_factor=0.037,skill_percentage=0.54):

        round_outcomes = {
        }

        games_won = [0, 0]
        for simulation in range(self.simulations):
            rounds_won = [0, 0]
            game_over = False
            round_results = []

            while game_over == False:

                last_4_rounds = round_results[len(round_results)-4:]

                net = sum(last_4_rounds)-len(last_4_rounds)*(round_win_probability-0.5)*skill_percentage

                mom = net*momentum_factor
                prob = max(min((round_win_probability-0.5)*skill_percentage+0.5+mom,0.99),0.01)


                if prob> random.random():
                    round_results.append(1)
                    rounds_won[0]+=1
                else:
                    round_results.append(-1)
                    rounds_won[1]+=1


                if max(rounds_won) == 16 and min(rounds_won) < 15:
                    game_over = True

                if rounds_won[0] == 18 and rounds_won[1] == 18:
                    h = 3
                if max(rounds_won) >=16 and min(rounds_won) >=15:
                    for tot_number,tot_round in enumerate(OT_VALUES):
                        if min(rounds_won) >= tot_round and min(rounds_won) < OT_VALUES[tot_number+1]:
                            ot_equal_tot = tot_round
                            break

                    if (max(rounds_won)-ot_equal_tot) %4 == 0 and max(rounds_won)-min(rounds_won) >=2:
                        game_over = True


                if game_over:
                    round_difference = rounds_won[0]-rounds_won[1]
                    if round_difference not in round_outcomes:
                        round_outcomes[round_difference] = 0

                    round_outcomes[round_difference]+=1


            if rounds_won[0] > rounds_won[1]:
                games_won[0] +=1
            else:
                games_won[1] +=1

        map_win_probability = games_won[0]/self.simulations
        return map_win_probability,round_outcomes




    def get_simulated_average_round_difference(self, round_outcomes):

        round_probs = {}
        average_round_difference = 0
        for round_difference in round_outcomes:

            probability = round(round_outcomes[round_difference]/self.simulations,4)
            round_probs[round_difference] = probability

            average_round_difference +=probability*round_difference

        return average_round_difference,round_probs




    def predict_proba(self,map_win_probability):


        for max_probability in self.max_probability_to_round_probabilities:
            if map_win_probability < max_probability:
                rp_prob = 0
                for round_difference,prob in self.max_probability_to_round_probabilities[max_probability].items():
                    if round_difference > 0:
                        rp_prob+=prob

                ratio_diff = rp_prob/map_win_probability

                for round_difference, prob in self.max_probability_to_round_probabilities[max_probability].items():
                    if round_difference > 0:
                        pre = self.max_probability_to_round_probabilities[max_probability][round_difference]
                        self.max_probability_to_round_probabilities[max_probability][round_difference]/=ratio_diff

                        #print(round_difference,self.max_probability_to_round_probabilities[max_probability][round_difference])

                probability = self.max_probability_to_round_probabilities[max_probability]
                return  probability

