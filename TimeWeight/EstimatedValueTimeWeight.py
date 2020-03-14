from TimeWeight.TimeWeight import TimeWeightGenerator


class EstimatedValueGenerator():

    def __init__(self, rating_method, game_single_player, backup_value, start_date_time, metric):
        self.metric = metric
        self.rating_method = rating_method
        self.updated_game_single_player = game_single_player
        self.backup_value = backup_value
        self.start_date_time = start_date_time
        self.stored_values = {
            'rating':None,
            'certain_ratio':None,
            'weighted_rating':None,
        }


    def get_estimated_value(self):

        time_weight_parameter = self.rating_method['parameter']
        max_days_ago = self.rating_method['max_days_ago']

        games_played_weight = self.rating_method['games_played_weight']
        self.stored_values['weighted_rating'] , date_to_max_day_ratio = self.get_game_weights(time_weight_parameter, max_days_ago)
        self.stored_values['certain_ratio'] = self.calculate_certain_ratio(date_to_max_day_ratio, games_played_weight)

        self.stored_values['rating'] = self.calculate_estimated_rating(self.stored_values['certain_ratio'] , self.stored_values['weighted_rating'], self.backup_value)
        return   self.stored_values['rating']

    def get_game_weights(self, time_weight_parameter, max_days_ago):
        TimeWeight = TimeWeightGenerator(self.start_date_time, self.updated_game_single_player, time_weight_parameter,
                                         max_days_ago, self.rating_method)
        TimeWeight.main()
        weighted_rating = TimeWeight.calculate_weighted_rating(self.metric)
        return weighted_rating, TimeWeight.date_to_max_day_ratio

    def calculate_estimated_rating(self, certain_ratio, weighted_rating, backup_rating):
        return certain_ratio * weighted_rating + (1 - certain_ratio) * backup_rating

    def calculate_certain_ratio(self, days_ago, games_played_weight):
        recency_div_factor = self.rating_method['games_played_div_factor'] / 2
        games_played = len(days_ago)
        if games_played == 0:
            return 0

        games_played_ratio = (1 / (1 + 10 ** (-games_played / self.games_played_div_factor)) - 0.5) * 2
        sum_date_ratio = sum(days_ago)
        recency_cv = (1 / (1 + 10 ** (- sum_date_ratio / recency_div_factor)) - 0.5) * 2

        certain_ratio = games_played_weight * games_played_ratio + (1 - games_played_weight) * recency_cv
        #### CREATE FUNCTION THAT has a ratio between 0 and 1. The more games played and the more recent they are the closer to 1 it is.
        return certain_ratio






