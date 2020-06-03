from Functions.AverageValues import *
import pickle
from sklearn import preprocessing
pd.options.mode.chained_assignment = None  # default='warn
import numpy as np
np.set_printoptions(suppress=True)
import time

class PlayerRoundWinsGenerator():

    def __init__(self,df,target):
        self.df = df
        self.feature_column_names =   ['performance_rating']

        all_columns = self.feature_column_names.copy()
        all_columns.append(target)
        all_columns.append('id')

        self.new_df = self.df.dropna(subset=     self.feature_column_names)
        #self.new_df = self.df.loc[self.v[all_columns]]



    def load_multi_model(self):
        self.full_filepath = r"C:\Users\Mathias\PycharmProjects\StatisticalModels\lr_round_wins_performance_rating"
        self.model = pickle.load(open(self.full_filepath, 'rb'))

    def load_linear_model(self):
        self.full_filepath = r"C:\Users\Mathias\PycharmProjects\StatisticalModels\linear_performance_rating"
        self.model = pickle.load(open(self.full_filepath, 'rb'))

    def main(self):
        #self.load_model()
        self.load_linear_model()
        self.standardize(self.new_df[self.feature_column_names])
        #self.predict_round_win_percentage_linear_regression()
        self.predict_round_win_percentage_own_method()
        #self.calculcate_predicted_rounds_won()
        self.normalize_round_wins()

    def standardize(self,X_values):
        scaler = preprocessing.StandardScaler()
        return  scaler.fit_transform(X_values)

    #### USE PROBABILITIES INSTEAD

    def calculcate_predicted_rounds_won(self):
        h = self.model.classes_
        X =   self.new_df [self.feature_column_names]

        X_standardized =  self. standardize(X)
        probabilities = self.model.predict_proba(    X_standardized )
        class_names = self.model.classes_
        self.new_df['player_predicted_net_rounds_won'] =  np.dot(probabilities,    class_names )
        self.new_df.loc[self.new_df['player_predicted_net_rounds_won'] >= 0, 'player_predicted_round_win_percentage'] = (16 / (
                    16 + 16 - self.new_df['player_predicted_net_rounds_won']))/5

        self.new_df.loc[ self.new_df['player_predicted_net_rounds_won'] < 0,
                         'player_predicted_round_win_percentage'] =  ((  self.new_df[ 'player_predicted_net_rounds_won'] + 16) / (
                (self.new_df['player_predicted_net_rounds_won'] + 16) + 16))/5


    def predict_round_win_percentage_linear_regression(self):
        X = self.new_df[self.feature_column_names]
        X_standardized = self.standardize(X)
        self.new_df['player_predicted_round_win_percentage'] = self.model.predict(     X_standardized )/5
        h = self.new_df.head(200)
        self.new_df.loc[self.new_df['player_predicted_round_win_percentage']<0,'player_predicted_round_win_percentage'] = 0

    def predict_round_win_percentage_own_method(self):
        X = self.new_df[self.feature_column_names]
        self.new_df['player_predicted_round_win_percentage'] =1/(1+10**(-X/155))/5

    def normalize_round_wins(self):

       # min = self.new_df['predicted_net_rounds_won'].min()
        #max = self.new_df['predicted_net_rounds_won'].max()
        #self.new_df['raw_normalized'] = (self.new_df['predicted_net_rounds_won']-min)/(max-min)
        #grouped_sum = self.new_df.groupby(['game_id','team_id'])['raw_normalized'].sum().reset_index()
        st = time.time()
        print("start")
        self.new_df['summed_player_round_win_percentage']=self.new_df.groupby(['game_id','team_id'])['player_predicted_round_win_percentage'].transform('sum')
        print("Done", time.time()-st)
        percentage_of_team = self.new_df['player_predicted_round_win_percentage']/self.new_df['summed_player_round_win_percentage']
        net_difference = self.new_df['rounds_win_percentage']-self.new_df['summed_player_round_win_percentage']
        self.new_df['normalized_player_round_win_percentage'] = self.new_df['player_predicted_round_win_percentage']+net_difference*percentage_of_team


if __name__ == '__main__':
    df = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\all_game_all_player_performance_rating")
    target = "round_win_percentage"
    PlayerRoundWins= PlayerRoundWinsGenerator(df,target)
    PlayerRoundWins.load_linear_model()
    #PlayerRoundWins.calculcate_predicted_rounds_won()
    #PlayerRoundWins.predict_round_win_percentage_linear_regression()
    PlayerRoundWins.predict_round_win_percentage_own_method()
    PlayerRoundWins.normalize_round_wins()