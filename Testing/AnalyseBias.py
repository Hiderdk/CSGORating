from Testing.configurations import *

from Functions.Filters import *
import pandas as pd

filepath_dataframes =r"C:\Users\Mathias\PycharmProjects\Ratings\Files"
tests = [fast_kill_kpr,fast_rating]

for number,configuration in enumerate(tests):

    filter_column_name = configuration['filter_column_name']
    filter_compared_to_column_name = configuration['filter_compared_to_column_name']
    min_difference = configuration['min_difference']
    max_difference = configuration['max_difference']
    filter_equal_to_names = configuration['filter_equal_to_names']
    filter_not_equal_to_names = configuration['filter_not_equal_to_names']
    filter_min_equal_to_values = configuration['filter_min_equal_to_values']
    filter_max_equal_to_values = configuration['filter_max_equal_to_values']

    df_file_name = configuration['df_file_name']
    df = pd.read_pickle(filepath_dataframes+"//"+df_file_name)

    #df['tournament_count'] = get_cumulative_count(df,['tournament_name'])

    for filter_min_equal_to_value in filter_min_equal_to_values:
        column_name = filter_min_equal_to_value
        value = filter_min_equal_to_values[column_name]
        df = df[df[column_name] > value]

    for filter_max_equal_to_value in filter_max_equal_to_values:
        column_name = filter_max_equal_to_value
        value = filter_max_equal_to_values[column_name]
        df = df[df[column_name] < value]

    for filter_not_equal_to_name in filter_not_equal_to_names:
        column_name = filter_not_equal_to_name
        value = filter_not_equal_to_names[column_name]
        df = df[df[    column_name]!=value]

    if 'error_column_name1' in configuration:
        error_column_name1 = configuration['error_column_name1']
        error_column_name2 = configuration['error_column_name2']
        df['net_error'] = df[error_column_name1] - df[error_column_name2]
    else:
        df['net_error'] = df[configuration['error_column_name']]

    df['net'] = df[filter_column_name]-df[filter_compared_to_column_name]

    filtered_df = get_rows_where_column_between(df,min_difference,max_difference,'net')
    average_error = filtered_df['net_error'].mean()
    print( len(filtered_df),average_error)

    reverse_filtered_df = get_rows_where_column_between(df,-max_difference,-min_difference,'net')
    average_error =     reverse_filtered_df['net_error'].mean()
    print( "reverse",len(    reverse_filtered_df ),average_error)

