import numpy as np
import datetime

from Functions.Filters import *

def get_rows_where_column_between(df,min_value,max_value,column_name):
    new_df = df[df[column_name].between(min_value,max_value)]

    return new_df

class TimeWeightGenerator():

    def __init__(self,current_date_time,df,time_weight_parameter,min_days_ago,rating_methods):
        self.time_weight_parameter = time_weight_parameter
        self.rating_methods = rating_methods
        self.min_days_ago = min_days_ago
        self.current_date_time = pd.to_datetime(current_date_time)
        self.df = df


    def main(self):
        self.min_date_time =  self.current_date_time - datetime.timedelta(days=self.min_days_ago)

        self.new_df =  get_rows_where_column_larger_than(self.df,   self.min_date_time, "start_date_time")
        if len(self.new_df) >=1:
            if 'weight_multiplier' in self.rating_methods:
                weight_column = self.rating_methods['weight_multiplier']
                self.weight_multiplier =      self.new_df [weight_column]
            else:
                self.weight_multiplier = None


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
        if  isinstance(self.weight_multiplier, pd.Series):
            pre_weights =  self.date_to_max_day_ratio*self.weight_multiplier** self.time_weight_parameter
        else:
            pre_weights = self.date_to_max_day_ratio ** self.time_weight_parameter

        return pre_weights.values / np.sum(pre_weights.values)

    def calculate_weighted_rating(self,metric_name):
        if len(self.new_df) == 0:
            return 0
        else:
            return float(( self.new_df [metric_name] * self.game_weights).sum())

