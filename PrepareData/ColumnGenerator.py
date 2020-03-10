from Functions.ChangeDataFrame import *
from Functions.Miscellaneous import *
from settings import *



class ColumnGenerator():

    def __init__(self,all_game_all_player):
        self.all_game_all_player = all_game_all_player
        pass

    def main(self):
        self.big_events()
        self.all_game_all_player['cumulative_games_played'] = get_cumulative_count(self.all_game_all_player,'player_id')
        self.all_game_all_player['cumulative_region_games_played'] = get_cumulative_count(self.all_game_all_player,
                                                                                   'region')

        self.all_game_all_player['cumulative_region_games_played'] = get_cumulative_count(self.all_game_all_player,
                                                                                          'region')

        self.all_game_all_player['previous_20_games_average'] = create_rolling_previous_average(    self.all_game_all_player,'player_id','opponent_adjusted_performance_rating',20)


    def big_events(self):
        self.all_game_all_player['big_event'] = 0
        self.all_game_all_player.loc[self.all_game_all_player['prize_pool']>=250000,'big_event'] = 1
        #self.all_game_all_player.loc[(self.all_game_all_player['prize_pool'] < 250000) & (self.all_game_all_player['prize_pool']>=50000) , 'big_event'] = 0
        self.all_game_all_player['cumulative_big_event_games_played'] = get_cumulative_count(self.all_game_all_player,
                                                                                          ['region','player_id'])




        pass

    def apply_columns(self):
        pass


if __name__ == '__main__':
    import pandas as pd
    from TimeWeightRatings.Main import *
    Time = AllGamesGenerator()

    all_team = pd.read_pickle(local_file_path + "\\all_team").sort_values(by='rating',ascending=False)
    file_name = "all_game_all_player_performance_rating"
    all_game_all_player = pd.read_pickle(local_file_path+"\\"+    file_name)
    Time.all_team = all_team
    Time.create_game_team(  all_game_all_player)
    #Time.all_game_all_team
    all_game_all_player ['start_date'] = pd.to_datetime(all_game_all_player ['start_date_time'].dt.date)
    v = all_game_all_player[(all_game_all_player['player_name']=='device') & (all_game_all_player['is_rating_updated']==1)]


    df =  all_game_all_player.groupby('player_id').apply(lambda x: x.set_index('start_date').resample('1D').first())

    df1 = df.groupby(level=0)['opponent_adjusted_performance_rating'].apply(lambda x: x.shift().rolling(min_periods=1, window=20).mean()).\
        reset_index(name='opponent_adjusted_performance_rating_past_20_days')
    all_game_all_player= pd.merge( all_game_all_player, df1, on=['start_date', 'player_id'], how='left')

    df1 = df.groupby(level=0)['opponent_adjusted_performance_rating'].apply(lambda x: x.shift().rolling(min_periods=1, window=80).mean()).\
        reset_index(name='opponent_adjusted_performance_rating_past_80_days')
    all_game_all_player= pd.merge( all_game_all_player, df1, on=['start_date', 'player_id'], how='left')

    dfg = df.groupby(level=0)['opponent_adjusted_performance_rating'].apply(
        lambda x: x.shift().rolling(min_periods=1, window=20).count()).reset_index(name='games_played_past_20_days')
    all_game_all_player= pd.merge( all_game_all_player, dfg, on=['start_date', 'player_id'], how='left')

    dfg = df.groupby(level=0)['opponent_adjusted_performance_rating'].apply(
        lambda x: x.shift().rolling(min_periods=1, window=80).count()).reset_index(name='games_played_past_80_days')
    all_game_all_player= pd.merge( all_game_all_player, dfg, on=['start_date', 'player_id'], how='left')


    df1 = df.groupby(level=0)['opponent_adjusted_performance_rating'].apply(
        lambda x: x.shift().rolling(min_periods=1, window=1).mean()).reset_index(name='Value_Average_Past_1_days')
    all_game_all_player= pd.merge( all_game_all_player, df1, on=['start_date', 'player_id'], how='left')


    all_game_all_player['net_opponent_adjusted_performance_rating'] = all_game_all_player['opponent_adjusted_performance_rating']-all_game_all_player['rating']
    functions_dict = {'First 25 Games':{
        'function_name':create_rolling_previous_average,
        'groupby_column_names':['game_id','player_id'],
        'output_column_name':"net_performance_rating",
        'back_count':25,
    }

    }

    Column = ColumnGenerator(all_game_all_player)
    Column.main()
    Column.all_game_all_player.to_pickle(local_file_path+"\\"+"all_game_all_player_performance_rating_old")
