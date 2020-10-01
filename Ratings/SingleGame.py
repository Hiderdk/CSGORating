from Functions.Filters import *
from Functions.SingleValue import *
import numpy as np
pd.set_option('display.max_columns', 100)
from TimeWeight.EstimatedValueTimeWeight import  EstimatedValueGenerator
from Functions.RatingFunctions import *
import math
from TimeWeight.timeweightconfigurations import player_time_weight_methods





class SingleGameRatingGenerator():


    def __init__(self,
                 team_ids,
                 team_player_ids,
                 start_date_time,
                 all_game_all_player,
                 all_player,
                 player_time_weight_methods,
                 update_dataframe=False,
                 single_game_all_player=None,
                 start_rating_quantile=0.22,
                 team_rating_prediction_beta=1500,
                 expected_player_percentage_contribution_beta=18500,
                 performance_multiplier=18500,
                 squared_performance_factor=1,
                 start_rating_regions = {'Europe': 1800, 'Africa': -900, 'Asia': 0,
                               'North America': 940, 'South America': 0,
                               'Middle East': 100, 'Oceania': -200, 'Brazil': 500,
                               None: 0},
                 map_names=[]
                 ):

        self.start_rating_regions = start_rating_regions
        self.start_rating_quantile = start_rating_quantile
        self.update_dataframe = update_dataframe
        self.player_time_weight_methods = player_time_weight_methods
        self.single_game_all_player = single_game_all_player
        self.all_game_all_player =all_game_all_player
        self.all_player =all_player
        self.team_ids = team_ids
        self.team_player_ids = team_player_ids
        self.start_date_time = start_date_time
        self.single_game_single_team_all_player = {}
        self.player_ratings = {}
        self.team_ratings = {}
        self.team_regions = {}
        self.player_ratings_dict = {}
        self.single_game_stored_player_values = {}
        self.player_id_to_player_index = {}
        self.map_names = map_names
        self.team_rating_prediction_beta = team_rating_prediction_beta
        self.expected_player_percentage_contribution_beta = expected_player_percentage_contribution_beta
        self.performance_multiplier = performance_multiplier
        self.squared_performance_factor = squared_performance_factor


    def get_team_regions(self):

        for team_id,player_ids in    self.team_player_ids.items():
            single_team_all_player = get_rows_where_is_in(self.all_player, player_ids,
                                                                                    "player_id")

            try: self.team_regions[team_id] = get_most_frequent_column_name( single_team_all_player ,"region")
            except ValueError: self.team_regions[team_id] = "unknown"
            if self.team_regions[team_id]==None:
                self.team_regions[team_id] = 'unknown'
            try:
                if math.isnan(self.team_regions[team_id]) is True:
                    self.team_regions[team_id] = 'unknown'
            except TypeError: pass

    def calculcate_ratings(self):

        self.get_team_regions()

        for team_id,player_ids in    self.team_player_ids.items():

            self.player_ratings[team_id] = []
            self.team_ratings[team_id] = 0


            for player_id in self.team_player_ids[team_id]:
                self.single_game_stored_player_values[player_id] = {}
                self.single_player(player_id,team_id)

        if self.update_dataframe is True:
            self.update_player_opponent_data()
            player_id0 = self.team_player_ids[self.team_ids[0]][0]
            if 'time_weighted_opponent_adjusted_kpr' in self.single_game_stored_player_values[player_id0]:
                self.update_expected_kill_percentage()

        return self.all_game_all_player,self.all_player


    def single_player(self,player_id,team_id):

        all_game_single_player = get_rows_where_column_equal_to(self.all_game_all_player,
                                                                     player_id,
                                                                     "player_id")
        updated_game_single_player = \
            get_rows_where_column_equal_to(all_game_single_player, 1, "is_rating_updated")

        if self.player_is_new(updated_game_single_player) is True:

            start_rating = self.calculcate_start_rating(team_id)
            player_index = self.all_player[self.all_player['player_id'] == player_id].index.tolist()[0]

            self.all_player.at[player_index,'start_time_weight_rating'] = start_rating


        for time_weight_name in self.player_time_weight_methods:

            rating_method = self.player_time_weight_methods[time_weight_name]
            column_name = self.player_time_weight_methods[time_weight_name]['column_name']
            column_names_equal_to = self.player_time_weight_methods[time_weight_name]['column_names_equal_to']

            for column_name_equal_to,equal_to_values in column_names_equal_to.items():
                if column_name_equal_to == "map" and self.map_names != []:
                    equal_to_values = self.map_names
                for equal_to_value in equal_to_values:

                    filtered_rows = self.get_filtered_rows(column_name_equal_to,equal_to_value,updated_game_single_player) ### CURRENTLY DOES NOT HANDLE MULTPLE DIFFERNT FILTERS
                    backup_value = self.get_backup_value(player_id,time_weight_name,self.player_time_weight_methods)

                    EstimatedValueObject = EstimatedValueGenerator(rating_method,filtered_rows, backup_value, self.start_date_time,column_name)
                    time_estimated_value = EstimatedValueObject.get_estimated_value()
                    if column_name_equal_to == "player_id":
                        output_column_name = time_weight_name
                    else:
                        output_column_name = time_weight_name + '_' + equal_to_value
                    self.single_game_stored_player_values[player_id][output_column_name] = time_estimated_value
                    self.single_game_stored_player_values[player_id][output_column_name + '_certain_ratio'] = EstimatedValueObject.stored_values['certain_ratio']
                    self.single_game_stored_player_values[player_id][output_column_name + '_weighted_rating'] = \
                    EstimatedValueObject.stored_values['weighted_rating']


                    if time_weight_name == "time_weight_rating":
                        self.player_ratings[team_id].append(time_estimated_value)
                        self.team_ratings[team_id] += time_estimated_value / len(self.team_player_ids[team_id])

                    if self.update_dataframe is True:
                        player_index = self.single_game_all_player[self.single_game_all_player['player_id']==player_id].index.tolist()[0]
                        self.player_id_to_player_index[player_id] = player_index
                        self.update_single_game_single_player(time_weight_name, EstimatedValueObject.stored_values,
                                                              player_index)
        if self.update_dataframe is True:

            self.update_all_player(player_id)

    def get_filtered_rows(self,column_name_equal_to,equal_to_value,filtered_rows):
        if column_name_equal_to == "player_id":
            updated_filtered_rows = filtered_rows
        else:
            updated_filtered_rows = filtered_rows[
                filtered_rows[column_name_equal_to].str.lower() == equal_to_value]

        return updated_filtered_rows

    def get_backup_value(self,id,metric,method):

        if 'hardcoded_backup_value' in method[metric]:
            backup_value = method[metric]['hardcoded_backup_value']

        else:
            backup_column_name = method[metric]['backup_column_name']
            if 'backup_source' in method[metric]:
                if method[metric]['backup_source'] == "all_player":
                    backup_value =self.all_player[self.all_player['player_id']==id][backup_column_name].iloc[0]
            else:
                backup_value =  self.single_game_stored_player_values[id][ backup_column_name ]

        return backup_value


    def player_is_new(self,all_game_rows):
        min_date = self.start_date_time - pd.DateOffset(days=500) ### otherwise player rating will be fucked up becuase it only looks at past 500 days
        game_rows = get_rows_where_column_larger_than(all_game_rows,min_date,"start_date_time")
        updated_games_played = len(game_rows)

        if updated_games_played == 0:
            return True
        else:
            return False

    def calculcate_start_rating(self, team_id):
        team_name = self.single_game_all_player[self.single_game_all_player['team_id']==team_id]['team_name'].iloc[0]
        if team_id in self.team_regions:
            region = self.team_regions[team_id]
        else:
            region = "unknown"


        if region not in self.start_rating_regions:
            print(region, "not in region")
            region = None


        region_level_rows = self.all_player[
            ( self.all_player['region'] == region)
            & ( self.all_player['time_weight_rating'] !="")
            & (self.all_player['time_weight_rating_certain_ratio'] >0.06)
            ]

        min_new_player_start_date_time = pd.to_datetime("2016-01-01")

        if len(region_level_rows) >= 30 and self.start_date_time > min_new_player_start_date_time:
            start_rating = region_level_rows['time_weight_rating'].quantile(self.start_rating_quantile)
        else:
            start_rating = self.start_rating_regions[region]


        if  self.get_it_player_is_female_or_staff(team_name) is True:
            start_rating -= 2500

        return start_rating

    def get_it_player_is_female_or_staff(self,team_name):

        if '_fe' in  team_name or 'Ladies' in team_name or ' fe' == team_name[len(team_name) - 3:] \
                or '_Staff' in team_name or ' RED' == team_name[len(team_name) - 3:]:
            return True
        else:
            return False

    def update_single_game_single_player(self,time_weight_name,stored_values,index):
        self.all_game_all_player.at[index,'is_rating_updated'] = 1
        for ratio,value in stored_values.items():
            if ratio == 'rating':
                column_name = time_weight_name
            else:
                column_name = time_weight_name + '_' + ratio
            self.all_game_all_player.at[index,column_name] = value

    def update_expected_kill_percentage(self):
        for team_id in self.team_player_ids:
            sum_team_kpr = 0
            sum_team_map_kpr = 0
            for player_id in self.team_player_ids[team_id]:
                sum_team_kpr += self.single_game_stored_player_values[player_id]['time_weighted_opponent_adjusted_kpr']
                sum_team_map_kpr += self.single_game_stored_player_values[player_id]['map_time_weighted_opponent_adjusted_kpr']
            for player_id in self.team_player_ids[team_id]:
                expected_kill_percentage = self.single_game_stored_player_values[player_id]['time_weighted_opponent_adjusted_kpr']/sum_team_kpr
                expected_kill_map_percentage = self.single_game_stored_player_values[player_id][
                                               'map_time_weighted_opponent_adjusted_kpr'] / sum_team_map_kpr
                index =          self.player_id_to_player_index[player_id]
                self.all_game_all_player.at[index,'expected_kill_percentage'] = expected_kill_percentage
                self.all_game_all_player.at[index, 'expected_kill_map_percentage'] = expected_kill_map_percentage

    def update_all_player(self,player_id):

        self.all_player.loc[self.all_player['player_id']==player_id,'time_weight_rating_certain_ratio'] = \
            self.single_game_stored_player_values[player_id]['time_weight_rating_certain_ratio']
        self.all_player.loc[self.all_player['player_id'] == player_id, 'time_weight_rating'] = \
        self.single_game_stored_player_values[player_id]['time_weight_rating']
        if 'time_weighted_opponent_adjusted_kpr' in self.single_game_stored_player_values[player_id]:
            self.all_player.loc[self.all_player['player_id'] == player_id, 'time_weighted_opponent_adjusted_kpr'] = \
                self.single_game_stored_player_values[player_id]['time_weighted_opponent_adjusted_kpr']




    def update_player_opponent_data(self):
        game_id = self.single_game_all_player['game_id'].iloc[0]
        single_game_all_player = self.all_game_all_player[self.all_game_all_player['game_id'] == game_id]
        single_game_indexes = single_game_all_player.index.tolist()
        team_number = -1

        single_game_team_indexes = {}
        for team_id, player_ids in self.team_player_ids.items():
            single_game_single_team_all_player = single_game_all_player[single_game_all_player['team_id']==team_id]
            team_number+=1
            single_game_team_indexes[team_id] = single_game_single_team_all_player.index.tolist()
            opponent_team_id = self.team_ids[-team_number + 1]
            self.all_game_all_player.at[single_game_team_indexes[team_id],'opponent_region'] =   self.team_regions[opponent_team_id]

            self.all_game_all_player.at[single_game_team_indexes[team_id], 'opponent_time_weight_rating'] = \
                self.team_ratings[opponent_team_id]

        expected_team_performances = self.calculcate_expected_team_performances()

        sum_squared_rounds_win_percentage = single_game_all_player['squared_rounds_win_percentage'].sum()/(len(single_game_all_player)/2)

        single_game_all_player['adjusted_rounds_win_percentage'] = single_game_all_player['squared_rounds_win_percentage']/sum_squared_rounds_win_percentage
        adjusted_rounds_win_percentage_list = single_game_all_player['adjusted_rounds_win_percentage'].tolist()
        self.all_game_all_player.at[
            single_game_indexes, 'adjusted_rounds_win_percentage'] = adjusted_rounds_win_percentage_list

        #percentage_of_team = single_game_all_player['player_predicted_round_win_percentage'] / single_game_all_player[
       #     'summed_player_round_win_percentage']
        #net_difference = single_game_all_player['adjusted_rounds_win_percentage'] -single_game_all_player['summed_player_round_win_percentage']
        #single_game_all_player['normalized_player_round_win_percentage'] = single_game_all_player[
        #                                                            'player_predicted_round_win_percentage'] + net_difference * percentage_of_team



        game_id = self.single_game_all_player['game_id'].iloc[0]
        updated_single_game_all_player = self.all_game_all_player[self.all_game_all_player['game_id']==game_id]
        opponent_adjusted_performance_ratings,expected_player_performances,expected_player_percentage_contributions\
            = self.calculcate_opponent_adjusted_performance_ratings(updated_single_game_all_player,expected_team_performances)
        opponent_adjusted_kpr = self.calculcate_opponent_adjusted_kpr(updated_single_game_all_player)
        self.all_game_all_player.at[
            single_game_indexes, "opponent_adjusted_kpr"] = opponent_adjusted_kpr
        self.all_game_all_player.at[
                single_game_indexes, "opponent_adjusted_performance_rating"] = opponent_adjusted_performance_ratings
        self.all_game_all_player.at[
                single_game_indexes, "expected_player_performances"] = expected_player_performances
        self.all_game_all_player.at[
            single_game_indexes, "expected_player_percentage_contribution"] = expected_player_percentage_contributions

        for team_id,indexes in single_game_team_indexes.items():
            self.all_game_all_player.at[
                indexes, "expected_team_performance"] = expected_team_performances[team_id]



       # self.all_game_all_player['net_opponent_adjusted_performance_rating'] = \
         #   self.all_game_all_player[ 'opponent_adjusted_performance_rating'] - self.all_game_all_player['time_weight_rating']





    def calculcate_opponent_adjusted_kpr(self,single_game_all_player):
        standard_rating = 3000
        factor = 0.000052
        return single_game_all_player['kpr'] + (single_game_all_player['opponent_time_weight_rating'] - standard_rating) * factor


    def calculcate_expected_team_performances(self):
        expected_team_performances = {}
        expected_team_performances_list = []
        teams = [t for t in self.team_ratings]
        for number,team in enumerate(teams):

            opponent_team = teams[-number+1]

            team_rating = self.team_ratings[team]
            opponent_rating = self.team_ratings[opponent_team]
            rating_difference = team_rating - opponent_rating
            #expected_team_performance_raw = (1 / (1 + 10 ** (-rating_difference / self.team_rating_prediction_beta)))**self.squared_performance_factor
            expected_team_performance_raw = (1 / (1 + 10 ** (-rating_difference / self.team_rating_prediction_beta)))
            expected_team_performances_list.append(expected_team_performance_raw)

        for number, team in enumerate(teams):
            expected_team_performances[team] = expected_team_performances_list[number]/sum(expected_team_performances_list)

        return expected_team_performances

    def calculcate_opponent_adjusted_performance_ratings(self, single_game_all_player,expected_team_performances):
      #  expected_player_percentage_contribution_beta = self.rating_model_parameters[
       #     'expected_player_percentage_contribution_beta']

        expected_player_percentage_contributions = []
        expected_player_performances = []
        opponent_adjusted_performance_ratings= []
        for index, row in single_game_all_player.iterrows():

            team_id = row['team_id']
            player_id = row['player_id']
            player_percentage_contribution = row['player_percentage_contribution']

            player_rating = self.single_game_stored_player_values[player_id]['time_weight_rating']
            rating_difference_from_team = (player_rating - self.team_ratings[team_id])
            expected_player_percentage_contribution = 1 / (1 + 10 ** (
                    -rating_difference_from_team / self.expected_player_percentage_contribution_beta)) / 2.5
            expected_player_percentage_contributions.append(expected_player_percentage_contribution)

            expected_player_performance = expected_player_percentage_contribution * expected_team_performances[team_id]
            expected_player_performances.append(expected_player_performance)
            player_performance = player_percentage_contribution * row['adjusted_rounds_win_percentage']
            net = player_performance - expected_player_performance

            # unlogged_expected_player_performances.append(np.log((expected_player_performance+0.4) / (1 - (expected_player_performance+0.4))))
            #  unlogged_player_performances.append(np.log(
            #    (player_performance+0.4) / (1 - (player_performance+0.4))))

          #  self.all_game_all_player.at[
            #    index, 'player_percentage_contribution'] = player_percentage_contribution

          #  self.all_game_all_player.at[
              #  index, 'expected_player_percentage_contribution'] = expected_player_percentage_contribution


            opponent_adjusted_performance_rating = net * self.performance_multiplier + player_rating
            opponent_adjusted_performance_ratings.append(opponent_adjusted_performance_rating)
        return opponent_adjusted_performance_ratings,expected_player_performances,expected_player_percentage_contributions

    def calculcate_opponent_adjusted_performance_ratings_old_method(self, single_game_all_player):


            net_performance_ratings = single_game_all_player["normalized_player_round_win_percentage"].astype(
                'float64') + 0.4
            # single_game_rows =  all_game_all_player.iloc[ self.single_game_indexes]

            return np.log((net_performance_ratings) / (1 - (net_performance_ratings))) * performance_multiplier + \
                   single_game_all_player['opponent_time_weight_rating']




