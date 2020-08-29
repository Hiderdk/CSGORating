from SQL import *
from settings import *

from Ratings.PerformanceRating import *
from Ratings.SingleGame import SingleGameRatingGenerator
from Functions.ChangeDataFrame import *
from aws import *
from Ratings.PlayerRoundWins import PlayerRoundWinsGenerator
from TimeWeight.timeweightconfigurations import player_time_weight_methods
import time

class RatingGenerator():

    def __init__(self,
                 newest_games_only=False,
                 min_date="2015-07-01",
                 max_date="2030-01-01",
                 insert_final_file=True,
                 parameter_configuration=player_time_weight_methods,
                 start_rating_quantile=0.1,
                 verbose=True
                 ):

        self.verbose = verbose
        self.newest_games_only = newest_games_only
        self.parameter_configuration=parameter_configuration
        self.max_date = max_date
        self.insert_final_file = insert_final_file
        self.min_date = min_date
        self.start_rating_quantile = start_rating_quantile
        self.all_team_dict = {
            'team_id': [],
            'team_name': [],
            'most_recent_date': [],
            'time_weight_rating': [],
            'time_weight_rating_certain_ratio': [],
            'player1_name': [],
            'player1_rating': [],
            'player2_name': [],
            'player2_rating': [],
            'player3_name': [],
            'player3_rating': [],
            'player4_name': [],
            'player4_rating': [],
            'player5_name': [],
            'player5_rating': [],
        }



    def main(self):

        if self.newest_games_only is True:

            self.load_dataframes()
            self.get_newest_all_game_all_player()

            if len(self.new_all_game_all_player) >= 1:
                self.new_all_game_all_player= self.add_columns_to_all_game_all_player(self.new_all_game_all_player)

                self.all_game_all_player = pd.concat([self.previous_all_game_all_player, self.new_all_game_all_player],
                                                     ignore_index=True)

                self.add_new_players_to_all_player()


                self.convert_all_team_df_to_dict()
                self.generate_player_round_wins()
            else:
                if self.verbose == True:
                    print("no new games found")



            series_ids = get_unique_values_from_column_in_list_format(  self.new_all_game_all_player , "series_id")

        else:
            self.load_data_from_sql()
            self.all_game_all_player = self.add_columns_to_all_game_all_player(self.all_game_all_player)
            self.all_player['time_weight_rating'] = ""
            self.all_player['time_weight_rating_certain_ratio'] = 0
            self.all_player['start_time_weight_rating'] = None
            self.generate_player_round_wins()

            series_ids = get_unique_values_from_column_in_list_format(self.all_game_all_player, "series_id")
        try:
            self.all_game_all_player =     self.all_game_all_player.sort_values(by=['start_date_time','game_number'],ascending=True)

        except AttributeError: ## No NEW GAMES
            pass


        self.calculcate_rating_for_all_series(series_ids)

        if self.insert_final_file == True:
            try:
                self.create_game_team(self.all_game_all_player)
                self.insert_files()
                self.print_out_ratings()
            except AttributeError: ## No NEW GAMES
                pass

        else:
            self.insert_files("process_")


    def convert_all_team_df_to_dict(self):
        for index,row in self.all_team.iterrows():
            for column in self.all_team.columns:
                value = row[column]
                self.all_team_dict[column].append(value)


    def insert_files(self,extra_name=""):
        self.all_team = pd.DataFrame.from_dict(self.all_team_dict)
        insert_df = self.all_game_all_player[np.isfinite(self.all_game_all_player['time_weight_rating'])]

        insert_df.to_pickle(local_file_path +"\\" + extra_name + "all_game_all_player_rating")
        self.all_player.to_pickle(local_file_path +"\\" + extra_name + "all_player")
        self.all_team.to_pickle(local_file_path +"\\" + extra_name + "all_team")
        all_game_all_team = self.create_game_team(self.all_game_all_player)
        all_game_all_team.to_pickle(local_file_path +"\\" + extra_name + "all_game_all_team_rating")
        if self.verbose == True:
            print("Updated file")

    def load_data_from_sql(self):
        self.all_game_all_player = get_all_time_game_player_data(self.min_date,self.max_date)
        self.all_player = get_player()


    def add_new_players_to_all_player(self):
        all_player_sql = get_player()
        all_player_sql['time_weight_rating'] = ""
        all_player_sql['time_weight_rating_certain_ratio'] = 0
        all_player_sql['start_time_weight_rating'] = None
        player_ids_sql = all_player_sql['player_id'].unique().tolist()
        player_ids_existing = self.all_player['player_id'].unique().tolist()
        unique_player_ids = list(set(player_ids_sql) - set(player_ids_existing))
        new_player_rows = all_player_sql.loc[all_player_sql['player_id'].isin(unique_player_ids)]

        for index,row in new_player_rows.iterrows():
            self.all_player = self.all_player.append(row)


    def get_newest_all_game_all_player(self):
        most_recent_date = \
        self.previous_all_game_all_player.sort_values(by=['start_date_time','game_number'], ascending=False).head(1)['start_date_time'].iloc[0]
        series_ids = get_all_series_ids(most_recent_date)['series_id'].unique().tolist()
        unique_series_ids = list(set(series_ids) - set(self.previous_all_game_all_player['series_id'].unique().tolist()))
        self.new_all_game_all_player = get_all_game_all_player_from_series_ids(unique_series_ids)


    def load_dataframes(self):
        self.previous_all_game_all_player = pd.read_pickle(local_file_path + "\\" + "all_game_all_player_rating")
        self.all_player = pd.read_pickle(local_file_path + "\\" + "all_player")
        self.all_team= pd.read_pickle(local_file_path + "\\" + "all_team")

  


    def add_columns_to_all_game_all_player(self, all_game_all_player):


        all_game_all_player['rounds_difference'] = all_game_all_player['rounds_won'] - \
                                                        all_game_all_player['rounds_lost']
        all_game_all_player['rounds_win_percentage'] = all_game_all_player['rounds_won'] / (
                    all_game_all_player['rounds_lost'] + all_game_all_player['rounds_won'])
        all_game_all_player['is_rating_updated'] = 0
        all_game_all_player = add_game_player_simple_ratings(all_game_all_player)
        all_game_all_player['predicted_adr'] = calculcate_predicted_adr(all_game_all_player)
        #all_game_all_player['rating'] = calculcate_predicted_adr(all_game_all_player)
       # all_game_all_player['opponent_adjusted_kpr'] = calculcate_predicted_adr(all_game_all_player)
        all_game_all_player['net_adr'] = all_game_all_player['adr']-all_game_all_player['predicted_adr']
        all_game_all_player['net_adr'] = all_game_all_player['net_adr'].fillna(0)
        all_game_all_player['performance_rating'] = add_performance_rating(all_game_all_player)
        all_game_all_player['opponent_adjusted_performance_rating'] = 0


        all_game_all_player= merge_dataframes_on_different_column_names_on_right(self.all_player[['player_id','region','country']],all_game_all_player,['player_id'],['player_id'])

        all_game_all_player = sort_2_values_by_ascending(all_game_all_player,
                                                              ["start_date_time", "game_number"])
        
        return all_game_all_player

        # insert_df_to_s3(bucket_name, self.all_game_all_player, file_name)


    def generate_player_round_wins(self):
        target = "round_win_percentage"
        PlayerRoundWins = PlayerRoundWinsGenerator( self.all_game_all_player,target)
        PlayerRoundWins.main()
        #insert_df_to_s3(bucket_name, PlayerRoundWins.new_df, file_name)
        self.all_game_all_player = PlayerRoundWins.new_df

    def create_game_team(self,all_game_all_player):
        group_sum = all_game_all_player.groupby(['team_id','game_id'])['kills'].sum().reset_index()
        self.all_game_all_team = all_game_all_player.groupby(
            ['opponent_region','rounds_won','rounds_lost','team_id','team_name','team_id_opponent','game_id','start_date_time','game_number','series_id','format'])[['opponent_adjusted_performance_rating','won','time_weight_rating','time_weight_rating_certain_ratio']].mean().reset_index()
        self.all_game_all_team = sort_2_values_by_ascending(self.all_game_all_team,['start_date_time','game_number'])
        #self.all_game_all_team =  merge_dataframes_on_different_column_names_on_right(self.all_team,self.all_game_all_team,"team_id","team_id")
        self.all_game_all_team  = pd.merge(group_sum,self.all_game_all_team,on=['team_id','game_id'])
        self.all_game_all_team['lost'] = -self.all_game_all_team['won']+1
        sub_df = self.all_game_all_team[['time_weight_rating_certain_ratio','time_weight_rating','game_id','team_id_opponent']].\
            rename(columns={"time_weight_rating":"opponent_time_weight_rating","time_weight_rating_certain_ratio":"opponent_time_weight_rating_certain_ratio"})

        self.all_game_all_team = pd.merge(sub_df,self.all_game_all_team,left_on=['game_id','team_id_opponent'],right_on=['game_id','team_id'])
        self.all_series_all_team = self.all_game_all_team.groupby(['team_id','series_id','format'])[['opponent_adjusted_performance_rating']].mean().reset_index()
        game1all = self.all_game_all_team[self.all_game_all_team['game_number']==1][['time_weight_rating',
                                                                                      "opponent_time_weight_rating",
                                                                                      "opponent_time_weight_rating_certain_ratio",
                                                                                      'time_weight_rating_certain_ratio','series_id','team_id','won','lost']]
        sup_grouped = game1all.groupby(['series_id','team_id'])[['time_weight_rating',
                                                                                      "opponent_time_weight_rating",
                                                                                      "opponent_time_weight_rating_certain_ratio",
                                                                                      'time_weight_rating_certain_ratio']].mean().reset_index()
        self.all_series_all_team = pd.merge(sup_grouped, self.all_series_all_team, on=['series_id', 'team_id'])

        sup_sum= game1all.groupby(['series_id','team_id'])[['won','lost']].sum().reset_index()
        self.all_series_all_team = pd.merge(sup_sum, self.all_series_all_team, on=['series_id', 'team_id'])


        return self.all_game_all_team


    def calculcate_rating_for_all_series(self,series_ids):


        for series_number, series_id in enumerate(series_ids):


            st = time.time()
            single_series_all_player = get_rows_where_column_equal_to(self.all_game_all_player, series_id,
                                                                           "series_id")
            start_date_time = single_series_all_player['start_date_time'].iloc[0]
            self.single_series(start_date_time,single_series_all_player)
            if self.verbose == True:
                print("Generating Rating for " + str(series_number) + " out of " + str(len(series_ids)) + " series ids",round(time.time()-st,3))
            post_series_single_series_all_player = get_rows_where_column_equal_to(self.all_game_all_player, series_id,
                                                                      "series_id")
            self.insert_to_all_team(post_series_single_series_all_player)

            if series_number % 400 == 0:
                if self.verbose == True:
                    self.print_out_ratings()

                self.insert_files("process_")


    def print_out_ratings(self):
        vg = self.all_player[self.all_player['time_weight_rating'] != ''].sort_values(by='time_weight_rating',
                                                                                      ascending=False)
        print(vg[['time_weight_rating', 'time_weight_rating_certain_ratio', 'player_name']].dropna().head(20))
        self.all_team = pd.DataFrame.from_dict(self.all_team_dict)
        vt = self.all_team.sort_values(by='time_weight_rating', ascending=False)
        print(vt[['time_weight_rating', 'team_name']].dropna().head(40))

    def insert_to_all_team(self, single_series_all_player):
        team_ids = single_series_all_player['team_id'].unique().tolist()
        start_date_time = single_series_all_player['start_date_time'].iloc[0]
        for team_id in team_ids:
            team_name = single_series_all_player[single_series_all_player['team_id']==team_id]['team_name'].iloc[0]
            if team_id not in self.all_team_dict['team_id']:
                for column in self.all_team_dict:
                    if column == 'team_id':
                        self.all_team_dict['team_id'].append(team_id)
                    elif column == "team_name":
                        self.all_team_dict['team_name'].append(team_name)
                    else:
                        self.all_team_dict[column].append(None)
            player_ids = single_series_all_player[single_series_all_player['team_id'] == team_id][
                        'player_id'].unique().tolist()
            self.update_all_team_dict(team_id,player_ids,start_date_time)


    def update_all_team_dict(self,team_id,player_ids,start_date_time):
        index = self.all_team_dict['team_id'].index(team_id)

        player_number = 0
        team_time_weight_ratings = []
        team_time_weight_certain_ratios = []
        for player_id in player_ids:
            player_number += 1
            if player_number == 6:
                break

            player_row = self.all_player[self.all_player['player_id'] == player_id]
            time_weight_rating = player_row['time_weight_rating'].iloc[0]
            time_weight_rating_certain_ratio = player_row['time_weight_rating_certain_ratio'].iloc[0]
            player_name = player_row['player_name'].iloc[0]
            self.all_team_dict['player' + str(player_number) + '_name'][index] = player_name
            self.all_team_dict['player' + str(player_number) + '_rating'][index] = time_weight_rating
            team_time_weight_certain_ratios.append(time_weight_rating_certain_ratio)
            team_time_weight_ratings.append(time_weight_rating)

        try:
            self.all_team_dict['time_weight_rating'][index] = sum(team_time_weight_ratings) / len(
                team_time_weight_ratings)
            self.all_team_dict['time_weight_rating_certain_ratio'][index] = sum(
                team_time_weight_certain_ratios) / len(
                team_time_weight_certain_ratios)
        except:
            self.all_team_dict['time_weight_rating'][index] = None
            self.all_team_dict['time_weight_rating_certain_ratio'][index] = None

        self.all_team_dict['most_recent_date'][index] = start_date_time


    def single_series(self,start_date_time,single_series_all_player):

        game_numbers = single_series_all_player['game_number'].unique().tolist()

        for  game_number in game_numbers:



            single_game_all_player = get_rows_where_column_equal_to(single_series_all_player, game_number,
                                                                      "game_number")
            if self.verbose == True:
                print("Date", start_date_time)
            first_row = single_game_all_player.head(1)
            self.game_id = first_row['game_id'].iloc[0]
            if len(single_game_all_player) != 10:
                continue

            team_ids = single_game_all_player['team_id'].unique().tolist()
            map = single_game_all_player['map'].iloc[0]
            if len(team_ids) == 2:


                team_player_ids = get_team_player_dictionary(single_game_all_player, "team_id", "player_id")
                SingleGame = SingleGameRatingGenerator(team_ids,team_player_ids,start_date_time,self.all_game_all_player,self.all_player,self.parameter_configuration,
                                                       update_dataframe=True,single_game_all_player=single_game_all_player,map_names=[map],start_rating_quantile=self.start_rating_quantile)

                self.all_game_all_player,self.all_player = SingleGame.calculcate_ratings()






if __name__ == '__main__':

    newest_games_only =False
    min_date = "2015-07-01"
    AllGames = RatingGenerator(newest_games_only=False,min_date="2015-07-01")

    AllGames.main()