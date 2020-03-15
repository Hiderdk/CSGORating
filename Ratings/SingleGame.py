from Functions.Filters import *
from Functions.SingleValue import *
import numpy as np
pd.set_option('display.max_columns', 100)
from TimeWeight.EstimatedValueTimeWeight import  EstimatedValueGenerator
from Functions.RatingFunctions import *
from TimeWeight.timeweightconfigurations import *


class SingleGameRatingGenerator():


    def __init__(self,team_ids,team_player_ids,start_date_time,AllGames,update_dataframe=False,single_game_all_player=None):
        self.update_dataframe = update_dataframe
        self.single_game_all_player = single_game_all_player
        self.all_game_all_player = AllGames.all_game_all_player
        self.all_team = AllGames.all_team
        self.all_player = AllGames.all_player
        self.team_ids = team_ids
        self.team_player_ids = team_player_ids
        self.start_date_time = start_date_time
        self.single_game_single_team_all_player = {}
        self.player_ratings = {}
        self.team_ratings = {}
        self.team_regions = {}
        self.player_ratings_dict = {}
        self.single_game_stored_player_values = {}


    def get_team_regions(self):
        for team_id,player_ids in    self.team_player_ids.items():


            try: self.team_regions[team_id] = get_most_frequent_column_name( self.single_game_single_team_all_player[team_id] ,"region")
            except ValueError: self.team_ratings[team_id] = "unknown"


    def calculcate_ratings(self):
        self.get_team_regions()
        for team_id,player_ids in    self.team_player_ids.items():
            self.single_game_single_team_all_player[team_id] = get_rows_where_is_in(self.all_player, player_ids, "player_id")
            self.player_ratings[team_id] = []
            self.team_ratings[team_id] = 0


            for player_id in player_ids:
                self.single_game_stored_player_values[player_id] = {}
                self.single_player(player_id,team_id)

        if self.update_dataframe is True:
            single_game_indexes = self.single_game_all_player.index.tolist()
            opponent_adjusted_kpr = self.calculcate_opponent_adjusted_kpr(self.single_game_all_player)
            opponent_adjusted_performance_ratings = self.calculcate_opponent_adjusted_performance_ratings(
                    self.single_game_all_player)



        return self.all_game_all_player,self.all_player,self.all_team


    def single_player(self,player_id,team_id):
        player_region = get_single_value_based_on_other_column_value(self.all_player, player_id,
                                                                          "player_id",
                                                                          "region")
        all_game_single_player = get_rows_where_column_equal_to(self.all_game_all_player,
                                                                     player_id,
                                                                     "player_id")
        updated_game_single_player = \
            get_rows_where_column_equal_to(all_game_single_player, 1, "is_rating_updated")

        if self.player_is_new(updated_game_single_player) is True:

            start_rating = self.calculcate_start_rating(team_id)
            player_index = self.all_player[self.all_player['player_id'] == player_id].index.tolist()[0]
            self.all_player.at[player_index,'start_time_weight_rating'] = start_rating

        for time_weight_name in player_time_weight_methods:
            rating_method = player_time_weight_methods[time_weight_name]
            column_name = player_time_weight_methods[time_weight_name]['column_name']
            #column_names_equal_to = player_time_weight_methods[time_weight_name]['column_names_equal_to']
            backup_value = self.get_backup_value(player_id,time_weight_name,player_time_weight_methods)

            EstimatedValueObject = EstimatedValueGenerator(rating_method,updated_game_single_player, backup_value, self.start_date_time,column_name)
            time_estimated_value = EstimatedValueObject.get_estimated_value()
            self.single_game_stored_player_values[player_id][time_weight_name] = time_estimated_value
            self.single_game_stored_player_values[player_id][time_weight_name + 'certain_ratio'] = EstimatedValueObject.stored_values['certain_ratio']
            self.single_game_stored_player_values[player_id][time_weight_name + 'weighted_rating'] = \
            EstimatedValueObject.stored_values['weighted_rating']

            self.player_ratings[team_id].append(time_estimated_value)
            self.team_ratings[team_id] += time_estimated_value / len(self.team_player_ids[team_id])

            if self.update_dataframe is True:
                player_index = self.single_game_all_player[self.single_game_all_player['player_id']==player_id].index.tolist()[0]
                self.update_single_game_single_player(time_weight_name,EstimatedValueObject.stored_values,player_index)



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
        team_name = get_single_value_based_on_other_column_value(self.all_team, team_id, "team_id",
                                                                 "team_name")
        if team_id in self.team_regions:
            region = self.team_regions[team_id]
        else:
            region = "unknown"
        start_rating_region = {'Europe': 1200, 'Africa': -900, 'Asia': 0,
                               'North America': 950, 'South America': 0,
                               'Middle East': 100, 'Oceania': -200, 'Brazil': 500,
                               'unknown': 0}

        if region not in start_rating_region:
            print(region, "not in region")
            region = 400
        else:
            start_rating = start_rating_region[region]

        updated_all_game_all_player = self.all_game_all_player[self.all_game_all_player['is_rating_updated']==1]
        equal_to_rows = get_rows_where_column_equal_to( updated_all_game_all_player , region ,"region")
        min_date = self.start_date_time- pd.DateOffset(months=6)
        equal_to_rows_date = get_rows_where_column_larger_than(equal_to_rows,min_date,"start_date_time")
        active_players_region = get_number_of_unique_values(         equal_to_rows_date,"player_id")

        if active_players_region > 25:

            if region == 'Europe': start_rating = start_rating_region[region] - (
                        active_players_region ** 0.52) * 37
            if region != 'Europe': start_rating = start_rating_region[region] - (
                        active_players_region ** 0.57) * 48
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
            if ratio == 'ratio':
                column_name = time_weight_name
            else:
                column_name = time_weight_name + '_' + ratio
            self.all_game_all_player.at[index,column_name] = value


    def update_player_opponent_data(self):

        team_number = -1
        for team_id, player_ids in self.team_player_ids.items():
            team_number+=1
            single_game_team_indexes = self.single_game_single_team_all_player[
               team_id].index.tolist()
            opponent_team_id = self.team_ids[-team_number + 1]
            self.all_game_all_player.at[single_game_team_indexes,'opponent_region'] =   self.team_regions[opponent_team_id]
            self.all_game_all_player.at[self.single_game_single_team_all_player[team_id] , 'opponent_time_weight_rating'] = \
                self.team_ratings[opponent_team_id]

            opponent_adjusted_performance_ratings = self.calculcate_opponent_adjusted_performance_ratings()

            self.all_game_all_player.at[
                self.single_game_indexes, "opponent_adjusted_performance_rating"] = opponent_adjusted_performance_ratings
            self.all_game_all_player['net_opponent_adjusted_performance_rating'] = self.all_game_all_player[
                                                                                       'opponent_adjusted_performance_rating'] - \
                                                                                   self.all_game_all_player[
                                                                                       'rating']



    def calculcate_opponent_adjusted_kpr(self):
        standard_rating = 1500
        factor = 0.00001
        return self.single_game_all_player['kpr'] + (self.single_game_all_player['rating'] - standard_rating) * factor

    def calculcate_opponent_adjusted_performance_ratings(self):
        performance_multiplier = 18500

        net_performance_ratings = self.single_game_all_player["normalized_player_round_win_percentage"].astype(
            'float64') + 0.4
        # single_game_rows =  all_game_all_player.iloc[ self.single_game_indexes]

        return np.log((net_performance_ratings) / (1 - (net_performance_ratings))) * performance_multiplier + \
               self.single_game_all_player['opponent_team_rating']




