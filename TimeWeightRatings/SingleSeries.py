from Functions.Lists import *
from Functions.Filters import *
from Functions.SingleValue import *
from TimeWeightRatings.SingleGame import SingleGameRatingGenerator
from Functions.Miscellaneous import *

class SingleSeriesRating():


    def __init__(self,series_id):
        self.series_id = series_id

        self.team_player_ratings = {}

    def main(self,AllGames):

        self.single_series_all_player = get_rows_where_column_equal_to(AllGames.all_game_all_player,self.series_id,"series_id")
        game_numbers = self.single_series_all_player['game_number'].unique().tolist()

        for  game_number in game_numbers:


            self.single_game_all_player = get_rows_where_column_equal_to(AllGames.all_game_all_player, game_number,
                                                                         "game_number")
            self.start_date_time = get_single_value_from_column(self.single_series_all_player, 'start_date_time')
            print("Date", self.start_date_time)
            first_row = self.single_game_all_player.head(1)
            self.game_id = first_row['game_id'].iloc[0]

            team_ids = get_number_of_unique_values(self.single_game_all_player,"team_id")

            if team_ids == 2:

                self.team_player_ids = get_team_player_dictionary(self.single_game_all_player, "team_id", "player_id")
                self.team_ids = get_unique_values_from_column_in_list_format(self.single_game_all_player, "team_id")
                SingleGame = SingleGameRatingGenerator(self.team_ids,self.team_player_ids,self.start_date_time)
                try:
                    SingleGame.main(AllGames)
                    AllGames = SingleGame.update_ratings_to_all_games(AllGames)
                except Exception:
                    print("Erro game_id", self.game_id)


        return AllGames


