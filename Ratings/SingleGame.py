from Functions.Filters import *
from Functions.SingleValue import *
import numpy as np
pd.set_option('display.max_columns', 100)
from TimeWeight.EstimatedValueTimeWeight import  EstimatedValueGenerator
from Functions.RatingFunctions import *
from TimeWeight.timeweightconfigurations import *
from Ratings.SingleGame import SingleGameRatingGenerator

class SingleGameRatingGenerator():


    def __init__(self,team_ids,team_player_ids,start_date_time,AllGames):
        self.all_game_all_player = AllGames.all_game_all_player
        self.all_game_all_team = AllGames.all_game_all_team
        self.all_team = AllGames.all_team
        self.all_player = AllGames.all_player
        self.team_ids = team_ids
        self.team_player_ids = team_player_ids
        self.start_date_time = start_date_time
        self.single_game_team_indexes = {}
        self.single_game_single_team_all_player = {}
        self.player_ratings = {}
        self.default_certain_ratio = {}
        self.normal_certain_ratio = {}
        self.default_player_ratings = {}
        self.weighted_player_ratings = {}
        self.team_ratings = {}
        self.team_regions = {}
        self.player_ratings_dict = {}



    pass

    def calculcate_and_update_ratings(self):

        self.calculcate_single_game_ratings()
        self.update_dataframes()

        return self.all_game_all_player,self.all_game_all_team,self.all_player,self.all_team



    def get_team_regions(self):
        for team_id,player_ids in    self.team_player_ids.items():

            single_team_all_player= get_rows_where_is_in(self.all_player,player_ids,"player_id")
            try: self.team_regions[team_id] = get_most_frequent_column_name(    single_team_all_player,"region")
            except ValueError: self.team_ratings[team_id] = "unknown"


    def calculcate_single_game_ratings(self):
        self.get_team_regions()
        for team_id,player_ids in    self.team_player_ids.items():
            self.player_ratings[team_id] = []
            self.weighted_player_ratings[team_id] = []
            self.default_player_ratings[team_id] = []
            self.default_certain_ratio[team_id] = []
            self.normal_certain_ratio[team_id] = []
            self.team_ratings[team_id] = 0


            for player_id in player_ids:
                self.single_player(player_id,team_id)




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


        for metric in player_time_weight_methods:
            rating_method = player_time_weight_methods[metric]
            column_name = player_time_weight_methods[metric]['column_name']
            column_names_equal_to = player_time_weight_methods[metric]['column_names_equal_to']
            backup_value = self.get_backup_value(metric,player_time_weight_methods,self.all_game_all_player)

            EstimatedValueObject = EstimatedValueGenerator(rating_method,updated_game_single_player, backup_value, self.start_date_time,metric)
            player_rating = EstimatedValueObject.get_estimated_value()

            self.player_ratings[team_id].append(player_rating)

        self.team_ratings[team_id] += player_rating / len(self.team_player_ids[team_id])



    def get_backup_value(self,metric,method,df,region):

        if 'hardcoded_backup_value' in method[metric]:
            backup_value = method[metric]['hardcoded_backup_value']
        elif 'backup_calculation' in method[metric]:
            backup_column_name = method[metric]['backup_column_name']
            function = method[metric]['backup_calculation']
            backup_value = function(self.all_game_all_player, self.all_player, self.game_context_values,   backup_column_name)

        else:
            backup_column_name = method[metric]['backup_column_name']
            backup_value =df.at[self.index,backup_column_name]

        return backup_value




    def player_is_new(self,all_game_rows):
        min_date = self.start_date_time - pd.DateOffset(days=500) ### otherwise player rating will be fucked up becuase it only looks at past 500 days
        game_rows = get_rows_where_column_larger_than(all_game_rows,min_date,"start_date_time")
        updated_games_played = len(game_rows)

        if updated_games_played == 0:
            return True
        else:
            return False

    def calculcate_start_rating(self, team_name):
        team_name = get_single_value_based_on_other_column_value(AllGames.all_team, team_id, "team_id",
                                                                 "team_name")
        if self.team_id in self.team_regions:
            region = self.team_regions[self.team_id]
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


        equal_to_rows = get_rows_where_column_equal_to(        self.updated_game_all_player , region ,"region")
        min_date = self.start_date_time- pd.DateOffset(months=6)
        equal_to_rows_date = get_rows_where_column_larger_than(equal_to_rows,min_date,"start_date_time")
        active_players_region = get_number_of_unique_values(         equal_to_rows_date,"player_id")

        if active_players_region > 25:
            # if region == 'Europe': start_rating =start_rating_region[region] - (active_players_region ** 0.54) * 52
            # if region != 'Europe': start_rating = start_rating_region[region]- (active_players_region ** 0.62) * 60

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



    def get_opponent_adjusted_performance_ratings(self,all_game_all_player):
        performance_multiplier = 18500
        single_game_rows = all_game_all_player[all_game_all_player.index.isin(self.single_game_indexes)]
        net_performance_ratings =         single_game_rows["normalized_player_round_win_percentage"].astype('float64')+0.4
        #single_game_rows =  all_game_all_player.iloc[ self.single_game_indexes]

        return   np.log(( net_performance_ratings) / (1 -(net_performance_ratings)))*performance_multiplier+ \
                 single_game_rows ['opponent_team_rating']

    def update_ratings_to_all_games(self, AllGames):

        self.single_game_indexes = self.single_game_all_player.index.tolist()
        team_number = -1
        for team_id, player_ids in self.team_player_ids.items():
            self.single_game_team_indexes[self.team_id] = self.single_game_single_team_all_player[
                self.team_id].index.tolist()

            team_number += 1
            mask = AllGames.all_player['player_id'].isin(player_ids)
            # for player_id in self.team_player_ids:
            # AllGames.all_player.[AllGames.all_player['player_id']==player_id]
            # AllGames.all_player.loc[mask, 'rating'] = self.player_ratings[team_id]

            opponent_team_id = self.team_ids[-team_number + 1]

            AllGames.all_game_all_player.at[self.single_game_team_indexes[team_id], 'opponent_region'] = \
                self.team_regions[opponent_team_id]
            AllGames.all_game_all_player.at[self.single_game_team_indexes[team_id], 'opponent_team_rating'] = \
            self.team_ratings[opponent_team_id]
            AllGames.all_game_all_player.at[self.single_game_team_indexes[team_id], 'certain_ratio'] = \
                self.normal_certain_ratio[team_id]
            AllGames.all_game_all_player.at[self.single_game_team_indexes[team_id], 'rating'] = self.player_ratings[
                team_id]
            AllGames.all_game_all_player.at[self.single_game_team_indexes[team_id], 'weighted_rating'] = \
            self.weighted_player_ratings[
                team_id]

            AllGames.all_game_all_player.at[self.single_game_team_indexes[team_id], 'default_rating'] = \
            self.default_player_ratings[team_id]

            AllGames.all_game_all_player.at[self.single_game_team_indexes[team_id], 'default_certain_ratio'] = \
                self.default_certain_ratio[team_id]

        AllGames.all_game_all_player.at[self.single_game_indexes, "is_rating_updated"] = 1

        opponent_adjusted_performance_ratings = self.get_opponent_adjusted_performance_ratings(
            AllGames.all_game_all_player)

        AllGames.all_game_all_player.at[
            self.single_game_indexes, "opponent_adjusted_performance_rating"] = opponent_adjusted_performance_ratings
        AllGames.all_game_all_player['net_opponent_adjusted_performance_rating'] = AllGames.all_game_all_player[
                                                                                       'opponent_adjusted_performance_rating'] - \
                                                                                   AllGames.all_game_all_player[
                                                                                       'rating']
        return AllGames


