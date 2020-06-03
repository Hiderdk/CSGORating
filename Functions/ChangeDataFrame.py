import numpy as np
from Functions.Lists import *
from Functions.Filters import *
from Functions.Updates import *
import time

def create_rolling_previous_average(df,groupby_columns,output_column_name,rolling_count):

    return df.groupby(groupby_columns)[output_column_name].transform(
        lambda x: x.rolling(rolling_count+1, 1).mean()) - df[output_column_name]


def count_previous_sum_based_on_1_where_conditions(df,previous_day_count,condition_1,output_column_name):

    def count(x, data, timewin):

        return data.loc[(data['start_date_time'] < x['start_date_time'])
                & (data['start_date_time'] >= x['start_date_time']-timewin)
                & (data[condition_1] == x[condition_1])][output_column_name].sum()


    return df.apply(lambda r: count(r, df, pd.Timedelta(previous_day_count, 'D')), axis=1)

def count_previous_sum_based_on_2_where_conditions(df,previous_day_count,condition_1,condition_2,output_column_name):

    def count(x, data, timewin):

        return data.loc[(data['start_date_time'] < x['start_date_time']) #select dates preceding current row
                & (data['start_date_time'] >= x['start_date_time']-timewin)
                & (data[condition_1] == x[condition_1])
                & (data[condition_2] == x[condition_2])][output_column_name].sum() #select rows with same player

    return df.apply(lambda r: count(r, df, pd.Timedelta(previous_day_count, 'D')), axis=1)



class ColumnsFromRowGenerator():

    def __init__(self,df,column_name):
        self.df = df
        self.column_name = column_name
        self.df['player_number'] = None


    def main(self):

        game_ids = self.df['game_id'].unique().tolist()
        for self.game_id in game_ids:

            st = time.time()

            self.single_game_all_player =get_rows_where_column_equal_to(self.df,self.game_id,"game_id")
            #self.df = get_rows_where_column_is_not_equal_to(self.df,self.game_id,"game_id")

            team_ids = get_unique_values_from_column_in_list_format(self.single_game_all_player,"team_id")
            for self.team_id in team_ids:
                self.single_game_single_team_all_player = get_rows_where_column_equal_to(self.single_game_all_player,self.team_id,"team_id")
                self.update_value_for_other_players_loop_method()
                #self.generate_player_number()
                #self.single_game_single_team_all_player = self.add_extra_columns_from_rows()
                #self.append_df()

           # print(len(self.df))


        return self.df

    def update_value_for_other_players_loop_method(self):
        player_ids = get_unique_values_from_column_in_list_format(self.single_game_single_team_all_player,"player_id")
        for index1,row1 in self.single_game_single_team_all_player.iterrows():
            player_id = row1['player_id']
        #for player_id in player_ids:
            player_number = 0
            for index,row in self.single_game_single_team_all_player.iterrows():
                value = row[self.column_name]
                row_player_id = row['player_id']

                if player_id != row_player_id:
                    player_number+=1

                    #self.df = update_dataframe_based_on_game_id_and_player_id(self.df ,self.game_id ,player_id ,self.column_name+'_'+str(player_number) ,value)
                    self.df = update_dataframe_based_on_index(self.df, index1, self.column_name+'_'+str(player_number) ,  value )



    def generate_player_number(self):
        player_number = 0
        for index,row in self.single_game_single_team_all_player.iterrows():
            player_number+=1
            self.single_game_single_team_all_player.at[index, "player_number"] = player_number



    def append_df(self):
        self.df = self.df.append(self.single_game_single_team_all_player,ignore_index=True)


    def add_extra_columns_from_rows(self):
        repeats = np.tile( self.single_game_single_team_all_player  [self.column_name].values, (len( self.single_game_single_team_all_player  ), 1))

        # remove elements from the diagonal
        m = repeats.shape[0]
        data = repeats[~np.eye(len( self.single_game_single_team_all_player  ), dtype=bool)].reshape(m, -1)

        # create new DataFrame
        df2 = pd.DataFrame(data=data[:, :], columns=self.column_name+'_' +  self.single_game_single_team_all_player ["player_number"].astype(str)[1:])

        # concat old and new data
        result = pd.concat([ self.single_game_single_team_all_player  , df2], axis=1)

        return result
