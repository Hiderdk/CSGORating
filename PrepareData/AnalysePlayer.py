import pandas as pd
from Functions.Filters import *
from Functions.Miscellaneous import *
pd.set_option('display.max_columns', 10)
class PlayerAnalyserGenerator():

    def __init__(self,df,player_ids,function_dict):
        self.df = df
        self.function_dict = function_dict
        self.player_ids = player_ids
        pass

    def main(self):
        self.df = get_rows_where_column_equal_to(self.df, 1, "is_rating_updated")
        for bias_column, bias_inputs in     function_dict .items():
            min_values = bias_inputs['min_values']
            max_values = bias_inputs['max_values']

            for variation_number, min_value in enumerate(min_values):
                max_value = max_values[variation_number]

                filtered_rows_all = get_rows_where_column_between(self.df, min_value, max_value, bias_column)

                filtered_rows =   get_rows_where_is_in(filtered_rows_all,self.player_ids,"player_id")
                sample_size = len(filtered_rows)

                grouped = get_groupby(filtered_rows, ['player_id','player_name'], bias_inputs['column_names'])
                print(grouped)




if __name__ == '__main__':

    all_game_all_player = pd.read_pickle(
        r"C:\Users\Mathias\PycharmProjects\Ratings\Files\all_game_all_player_performance_rating_old")
    all_game_all_player['net_opponent_adjusted_performance_rating'] = all_game_all_player[
                                                                          'opponent_adjusted_performance_rating'] - \
                                                                      all_game_all_player['rating']

    all_game_all_player['rating_difference'] = all_game_all_player['rating'] - all_game_all_player['opponent_team_rating']

    player_ids = [237,1067,735,632]

    function_dict = {
        'start_date_time':{'min_values':["2019-01-01"],'max_values':["2019-07-01"],
                           'column_names':['rating','opponent_team_rating','performance_rating','opponent_adjusted_performance_rating']}
        #'player_predicted_round_win_percentage': {'min_values': [0.05,0.11], 'max_values': [0.09,0.15],
                     #         'column_names': ['normalized_player_round_win_percentage']}
    }

    PlayerAnalyser = PlayerAnalyserGenerator(all_game_all_player,player_ids,function_dict)
    PlayerAnalyser.main()