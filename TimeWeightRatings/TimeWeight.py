import pandas as pd
import numpy as np
from Functions.Filters import *
from Functions.Miscellaneous import *

class TimeWeightGenerator():

    def __init__(self,current_date_time,df,time_weight_parameter,min_days_ago):
        self.time_weight_parameter = time_weight_parameter
        self.min_days_ago = min_days_ago
        self.current_date_time = pd.to_datetime(current_date_time)
        self.df = df



    def main(self):
        self.min_date_time =subtract_date_integer_to_datetime(self.current_date_time,self.min_days_ago)
        self.new_df =  get_rows_where_column_between(self.df,        self.min_date_time,self.current_date_time, "start_date_time")
        if len(self.new_df) >=1:
            self.days_ago = self.get_days_ago()
            self.game_weights =self.calculate_each_game_weights()

        else:
            self.days_ago = []
            self.game_weights = []
            self.date_to_max_day_ratio = []

    def get_days_ago(self):
        return (pd.to_datetime(self.current_date_time)- self.new_df['start_date_time']).dt.days


    def calculate_each_game_weights(self):
        ## FUNCTION THAT WEIGHTS RECENT PERFORMANCES HIGHER

        self.date_to_max_day_ratio = (      self.min_days_ago -    self.days_ago) /       self.min_days_ago
        pre_weights =  self.date_to_max_day_ratio** self.time_weight_parameter
        return pre_weights.values / np.sum(pre_weights.values)

    def calculate_weighted_rating(self,metric_name):
        return float((   self.new_df [metric_name] *         self.game_weights).sum())


if __name__ == '__main__':
    from settings import local_file_path
    current_date_time = pd.to_datetime("2019-11-11")
    df = pd.read_pickle(local_file_path+'//all_game_all_player_performance_rating')
    single_player_df = df[df['player_name']=='device']
    TW = TimeWeightGenerator(current_date_time,    single_player_df,20,400)
    print(TW.estimated_rating)
