from SQL import *
from settings import *
from Functions.Lists import *
from Functions.Miscellaneous import *
from Ratings.PerformanceRating import *
from Ratings.SingleSeries import SingleSeriesRating
from Functions.ChangeDataFrame import *
from aws import *
from Ratings.PlayerRoundWins import PlayerRoundWinsGenerator
import time

class AllGamesGenerator():

    def __init__(self):
        pass

    def main(self,newest_games_only,min_date):
        self.newest_games_only = newest_games_only
        self.min_date = min_date
        if self.newest_games_only is True:
            self.load_newest_games_only()
            if len(self.all_game_all_player) >= 1:
                self.prepare_data()
                self.generate_player_round_wins()
                series_ids = get_unique_values_from_column_in_list_format(self.all_game_all_player, "series_id")
                self.all_game_all_player = pd.concat([self.previous_all_game_all_player,self.all_game_all_player],ignore_index=True)
            else:
                print("no new games found")
        else:
            self.load_data_from_sql()
            self.prepare_data()
            self.generate_player_round_wins()
            self.all_player['start_rating'] = None
            self.all_player['default_rating'] = None

            series_ids = get_unique_values_from_column_in_list_format(self.all_game_all_player, "series_id")

        self.all_game_all_player =     self.all_game_all_player.sort_values(by='start_date_time',ascending=True)
        self.calculcate_rating_for_all_series(series_ids)


        self.insert_files()
        self.create_game_team(self.all_game_all_player)


    def insert_files(self):
        insert_df = self.all_game_all_player[np.isfinite(self.all_game_all_player['rating'])]
        insert_df.to_pickle(local_file_path +"\\" + "all_game_all_player_performance_rating")
        self.all_player.to_pickle(local_file_path +"\\" + "all_player")
        self.all_team.to_pickle(local_file_path +"\\" + "all_team")
        print("Updated file")

    def load_data_from_sql(self):
        self.all_game_all_player = get_all_time_game_player_data(self.min_date)
        self.all_team = get_team()
        self.all_player = get_player()


    def load_newest_games_only(self):
        self.previous_all_game_all_player = pd.read_pickle(local_file_path + "\\" + "all_game_all_player_performance_rating")
        #self.previous_all_game_all_player = self.previous_all_game_all_player[self.previous_all_game_all_player['start_date_time']<'2019-03-15']
        self.all_player = pd.read_pickle(local_file_path + "\\" + "all_player")
        self.all_team= pd.read_pickle(local_file_path + "\\" + "all_team")
        most_recent_date =    self.previous_all_game_all_player.sort_values(by='start_date_time',ascending=False).head(1)['start_date_time'].iloc[0]
        series_ids = get_all_series_ids(most_recent_date)['series_id'].unique().tolist()
        unique_series_ids = list(set(   series_ids ) - set(self.previous_all_game_all_player['series_id'].unique().tolist()))
        self.all_game_all_player= get_all_game_all_player_from_series_ids(unique_series_ids)



    def prepare_data(self):


        self.all_game_all_player['rounds_difference'] = self.all_game_all_player['rounds_won'] - \
                                                        self.all_game_all_player['rounds_lost']
        self.all_game_all_player['rounds_win_percentage'] = self.all_game_all_player['rounds_won'] / (
                    self.all_game_all_player['rounds_lost'] + self.all_game_all_player['rounds_won'])
        self.all_game_all_player['is_rating_updated'] = 0
        self.all_game_all_player = add_game_player_simple_ratings(self.all_game_all_player)
        self.all_game_all_player['predicted_adr'] = calculcate_predicted_adr(self.all_game_all_player)
        self.all_game_all_player['net_adr'] = self.all_game_all_player['adr']-self.all_game_all_player['predicted_adr']
        self.all_game_all_player['net_adr'] = self.all_game_all_player['net_adr'].fillna(0)

        self.all_game_all_player['performance_rating'] = add_performance_rating(self.all_game_all_player)
        self.all_game_all_player['opponent_adjusted_performance_rating'] = 0


        self.all_game_all_player= merge_dataframes_on_different_column_names_on_right(self.all_player[['player_id','region','country']],self.all_game_all_player,['player_id'],['player_id'])

        self.all_game_all_player = sort_2_values_by_ascending(self.all_game_all_player,
                                                              ["start_date_time", "game_number"])

        # insert_df_to_s3(bucket_name, self.all_game_all_player, file_name)




    def generate_player_round_wins(self):
        target = "round_win_percentage"
        PlayerRoundWins = PlayerRoundWinsGenerator( self.all_game_all_player,target)
        PlayerRoundWins.main()
        #insert_df_to_s3(bucket_name, PlayerRoundWins.new_df, file_name)
        self.all_game_all_player = PlayerRoundWins.new_df

    def create_game_team(self,all_game_all_player):
        self.all_game_all_team = all_game_all_player.groupby(['team_id','game_id','start_date_time','game_number'])[['rating','opponent_adjusted_performance_rating','certain_ratio']].mean().reset_index()
        self.all_game_all_team = sort_2_values_by_ascending(self.all_game_all_team,['start_date_time','game_number'])
        self.all_game_all_team =  merge_dataframes_on_different_column_names_on_right(self.all_team,self.all_game_all_team,"team_id","team_id")
        self.all_game_all_team.to_pickle(local_file_path + "\\" + "all_game_all_team")

    def calculcate_rating_for_all_series(self,series_ids):

        print(self.all_game_all_player.head(1)['start_date_time'])
        for series_number, series_id in enumerate(series_ids):
            start_date_time = time.time()

            self.single_series(series_id)
            print("Generating Rating for " + str(series_number) + " out of " + str(len(series_ids)) + " series ids",round(time.time()-start_date_time,3))

            if series_number % 50 == 0:

                vg =  self.all_player.sort_values(by='rating', ascending=False)
                print(vg[['player_id', 'rating', 'player_name']].dropna().head(20))
                vt = self.all_team.sort_values(by='rating', ascending=False)
                print(vt[['rating', 'team_name']].dropna().head(20))
                self.insert_files()


    def single_series(self,start_date_time,series_id):

        self.single_series_all_player = get_rows_where_column_equal_to(self.all_game_all_player,series_id,"series_id")
        game_numbers = self.single_series_all_player['game_number'].unique().tolist()

        for  game_number in game_numbers:

            single_game_all_player = get_rows_where_column_equal_to(self.all_game_all_player, game_number,
                                                                         "game_number")
            print("Date", start_date_time)
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

if __name__ == '__main__':
    newest_games_only =False
    min_date = "2015-01-01"
    AllGames = AllGamesGenerator()

    AllGames.main(newest_games_only,min_date)