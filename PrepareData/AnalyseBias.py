
from Functions.Filters import *
from Functions.Miscellaneous import *
from settings import *
pd.set_option('display.max_columns', 10)
class AnalyzeBiasGenerator():

    def __init__(self,df,bias_dict,initial_filter):
        self.df = df
        self.bias_dict = bias_dict
        self.initial_filter = initial_filter

    def main(self):
        self.df = self.df[self.df['is_rating_updated']==1]
        self.get_initial_filters()
        self.get_filter_column_names()
        #filter_column_names = self.bias_dict['filter_column_names']
        groupby_column_names = self.bias_dict['groupby_column_names']
        output_column_names = self.bias_dict['output_column_names']


        filters_0 = self.bias_dict['filter_column_names'][self.filter_column_names[0]]
        filters_1 = self.bias_dict['filter_column_names'][self.filter_column_names[1]]

        for variation_number in range(filters_0 ['iterations']):
            filtered_rows1 = self.get_rows_for_function(  filters_0,self.initial_filtered_df,variation_number,self.filter_column_names[0])

            for variation_number1 in  range(filters_1['iterations']):

                filtered_rows= self.get_rows_for_function(     filters_1 ,filtered_rows1,variation_number1,self.filter_column_names[1])


                sample_size = len(filtered_rows)
                print("Sample", sample_size)
                                #columns = bias_inputs['column_names']
                                #columns.append(bias_column)
                grouped =get_groupby(filtered_rows,  groupby_column_names ,     output_column_names)
                grouped['count'] = groupby_count(filtered_rows, groupby_column_names)[0]
                print(grouped)

    def get_initial_filters(self):
        self.df = get_rows_where_column_equal_to(self.df, 1, "is_rating_updated")
        column_name = self.initial_filter['column_name']
        min= self.initial_filter['min']
        max = self.initial_filter['max']
        function = self.initial_filter['function']
        self.initial_filtered_df = function(self.df,min,max,column_name)

    def get_filter_column_names(self):
        self.filter_column_names = []
        for column in self.bias_dict['filter_column_names']:
            self.filter_column_names.append(column)


    def get_rows_for_function(self,filters,df,variation_number,filter_column_name):

        if len(filters['min'])>=1:
            min_value = filters['min'][variation_number]
            max_value = filters['max'][variation_number]
            filtered_rows = get_rows_where_column_between(df, min_value, max_value,filter_column_name)

        elif len(filters['other_column_names'])>=1:
            function = filters['function']
            other_column_name = filters['other_column_names'][variation_number]

            filtered_rows =function(df,filters['difference'][variation_number], filter_column_name, other_column_name)

        return filtered_rows


if __name__ == '__main__':
    file_name = "all_game_all_player_performance_rating_old"
    all_game_all_player = pd.read_pickle(local_file_path + "\\" + file_name)


    all_game_all_player['net_opponent_adjusted_performance_rating'] = all_game_all_player['opponent_adjusted_performance_rating']-all_game_all_player['rating']
    all_game_all_player['rating_difference'] = all_game_all_player['rating']-all_game_all_player['opponent_team_rating']

    initial_filter = {
        #'column_name':'games_played_past_80_days',
        'column_name':'start_date_time',
        'min':'2019-01-01',
        'max':'2030-01-01',
        'function':get_rows_where_column_between,
    }

    bias_dict = {
            'filter_column_names':{
              'rating':{'function':get_rows_where_column_between,'min':[2600],'max':[6000],'equal_to':[],'iterations':1},
               # 'cumulative_region_games_played': {'function': get_rows_where_column_between, 'min': [1000], 'max': [200000],
               #                             'equal_to': [], 'iterations': 1},
                'weighted_rating':{'function':get_rows_where_column_less_than_other_column,'equal_to':[],'difference':[-65],'iterations':1,'other_column_names':['rating'],'min':[],'max':[]},

            },

            'output_column_names':['net_opponent_adjusted_performance_rating'],
            'groupby_column_names':['region']}


    AnalyzeBias = AnalyzeBiasGenerator(all_game_all_player,bias_dict,initial_filter)
    AnalyzeBias.main()