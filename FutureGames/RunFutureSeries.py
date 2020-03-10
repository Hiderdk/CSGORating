from settings import *
from SQL import *
from Functions.Filters import *
from Functions.SingleValue import *
from Functions.Lists import *
from TimeWeightRatings.SingleGame import SingleGameRatingGenerator
from TimeWeightRatings.Main import AllGamesGenerator


class SeriesPredictionGenerator():

    def __init__(self):
        pass

    def load_data(self):
        self. AllGames = AllGamesGenerator()
        self.   AllGames.all_game_all_player = pd.read_pickle(local_file_path+"//all_game_all_player_performance_rating_old").sort_values(by='start_date_time',ascending=False)
        self.AllGames.all_player = pd.read_pickle(local_file_path + "//all_player")
        self.AllGames.all_team = pd.read_pickle(local_file_path + "//all_team")
        min_date =self.AllGames.all_game_all_player.head(1)['start_date_time'].iloc[0]
        pre_series_player = get_all_from_series_player(min_date)
        historical_series_ids =  self.AllGames.all_game_all_player ['series_id'].unique().tolist()
        self.future_series_player = pre_series_player[~pre_series_player.series_id.isin(        historical_series_ids)]
        pass

    def main(self):

        series_ids = self.future_series_player['series_id'].unique().tolist()
        for self.series_id in series_ids:
            self.player_ratings = {}
            self.single_series_all_player = get_rows_where_column_equal_to(self.future_series_player,self.series_id,"series_id")
            self.start_date_time =    self.single_series_all_player .head(1)['start_date_time'].iloc[0]
            self.team_ids = get_unique_values_from_column_in_list_format(self.single_series_all_player,"team_id")
            self.get_team_player_ids()
            self.SingleGameRating = SingleGameRatingGenerator(self.team_ids,self.team_player_ids,self.start_date_time)
            self.SingleGameRating.main(self.AllGames)

            self.predict_single_game()




    def get_team_player_ids(self):
        self.team_player_ids = {self.team_ids[0]:[],self.team_ids[1]:[]}
        for self.team_id in self.team_ids:
            self.single_series_single_team_all_player = get_rows_where_column_equal_to(self.single_series_all_player,
                                                                                       self.team_id, "team_id")

            player_ids = get_unique_values_from_column_in_list_format(self.single_series_single_team_all_player,
                                                                      "player_id")
            for self.player_id in player_ids:
                self.team_player_ids[self.team_id].append(self.player_id)

    def predict_single_game(self):
        rating_difference = self.SingleGameRating.team_ratings[self.team_ids[0]]- self.SingleGameRating.team_ratings[self.team_ids[1]]
        pass




if __name__ == '__main__':
    SeriesPrediction = SeriesPredictionGenerator()
    SeriesPrediction.load_data()
    SeriesPrediction.main()