from Functions.Lists import *
from Functions.Filters import *
from TimeWeightRatings.TimeWeight import *
from Functions.RatingFunctions import *
from Functions.SingleValue import *



class PlayerRatingGenerator():

    def __init__(self,game_single_player,start_rating,start_date_time):

        self.updated_game_single_player= game_single_player
        self.rating_methods = {
            'default_rating': {'parameter': 1.5, 'max_days_ago': 500, 'backup': "start_rating", "games_played_weight": 0.6},
            'normal_rating': {'parameter': 1.5, 'max_days_ago': 130, "backup": "default_rating", "games_played_weight": 0.06}
        }

        self.start_rating = start_rating
        self.start_date_time = start_date_time
        pass

    def main(self):

        self.ratings = {}
        self.ratings['start_rating'] = self.start_rating
        if self.ratings['start_rating']== None:
            print("player has no start rating")
            self.ratings['start_rating'] = -100

        self.rating = 0
        for rating_method in self.rating_methods:
            time_weight_parameter= self.rating_methods[rating_method]['parameter']
            max_days_ago= self.rating_methods[rating_method]['max_days_ago']
            backup_column_name = self.rating_methods[rating_method]['backup']
            games_played_weight = self.rating_methods[rating_method]['games_played_weight']
            self.rating_methods[rating_method]['weighted_rating'],date_to_max_day_ratio= self.get_game_weights(time_weight_parameter,   max_days_ago)

            self.rating_methods[rating_method]['certain_ratio'] = calculate_certain_ratio(date_to_max_day_ratio,games_played_weight)
            #backup_rating= get_single_value_based_on_other_column_value(self.AllGames.all_player,self.player_id,"player_id",backup_column_name)
            backup_rating = self.ratings[backup_column_name]
            self.ratings[rating_method ] =  calculate_estimated_rating(   self.rating_methods[rating_method]['certain_ratio'] ,  self.rating_methods[rating_method]['weighted_rating'],backup_rating)


    def get_game_weights(self, time_weight_parameter,   max_days_ago):

        TimeWeight = TimeWeightGenerator(self.start_date_time,  self.updated_game_single_player , time_weight_parameter, max_days_ago)
        TimeWeight.main()
        weighted_rating =  TimeWeight.calculate_weighted_rating("opponent_adjusted_performance_rating")
        return weighted_rating,TimeWeight.date_to_max_day_ratio


