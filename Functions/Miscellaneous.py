import pandas as pd
import datetime

import numpy as np


def convert_dict_to_df(data_dict):
    new_dict = {}

    for column,value in data_dict.items():
        new_dict[column] = [value]

    return pd.DataFrame.from_dict(new_dict)

def scale_features_and_insert_to_dataframe(scaled_data, unscaled_values):
    scaled_features = {}

    for column in scaled_data.columns[1:]:

        if column not in scaled_features:
            scaled_features[column] = []

        mean = scaled_data.loc[scaled_data['Standardized'] == 'mean', column].iloc[0]
        scaled = scaled_data.loc[scaled_data['Standardized'] == 'scaled', column].iloc[0]
        scaled_features[column].append((unscaled_values[column] - mean) / scaled)
    X_values_df = pd.DataFrame.from_dict(scaled_features)
    return X_values_df


def get_scaled_ratios_to_dict_format(scaled_data):
    scaled_ratios = {}
    for column in scaled_data.columns[1:]:
        mean = scaled_data.loc[scaled_data['Standardized'] == 'mean', column].iloc[0]
        scaled = scaled_data.loc[scaled_data['Standardized'] == 'scaled', column].iloc[0]
        scaled_ratios[column] = {
            'mean': mean,
            'scaled': scaled,
        }

    return scaled_ratios


def get_cumulative_count(df,grouped_by_column_name):
    return df.groupby(grouped_by_column_name).cumcount()-1

def groupby_count(df,grouped_by_column_name):
    return df.groupby(grouped_by_column_name).size().reset_index()

def  get_groupby(df,grouped_by,column_name):

    return df.groupby(grouped_by)[column_name].mean().reset_index()

def subtract_date_integer_to_datetime(date_1,integer):
    new_date_time = date_1 - datetime.timedelta(days=integer)

    return new_date_time

def sort_values_by_descending(df,column_name):

    return df.sort_values(by=column_name,ascending=False)


def sort_values_by_ascending(df,column_name):
    sorted = df.sort_values(by=[column_name], ascending=True)
    return sorted

def sort_2_values_by_ascending(df,column_names):
    sorted = df.sort_values(by=column_names, ascending=[True,True])
    return sorted

def remove_column_names_from_dictionary_with_empty_columns(mydict):
    fake_dict = copy.deepcopy(mydict)
    for column in mydict:
        if len(mydict[column])== 0:
            del   fake_dict [column]

    return fake_dict


def convert_dictionary_to_dataframe(mydict):

    try: return pd.DataFrame.from_dict(mydict)
    except:
        for column in mydict:
            print(column, len(mydict[column]))
        return pd.DataFrame.from_dict(mydict)


def get_value_from_index(df,column_name,index):
    return df.ix[index][column_name]

def get_highest_value(df,column_name):
    if len(df) >=1:
        return int(df[column_name].max())
    else:
        return None

def get_column_name_with_highest_value_from_multiple_columns(df,column_names):
    max_value = 0
    max_column_name = column_names[0]
    for column_name in column_names:
        average_value = df[column_name].dropna().mean()
        if average_value > max_value:
            max_value = average_value
            max_column_name = column_name

    return max_column_name


def get_highest_value_and_return_index(df,column_name):
    return pd.to_numeric(df[column_name]).idxmax()


def get_number_of_unique_values(df,column_name):
    return len(df[column_name].unique().tolist())

def get_standard_deviation_from_column_name(df,column_name):
    series = df[column_name].dropna()
    return series.std()


def rename_merged_dataframe(df):
    for column in df.columns:
        if column[len(column)-2:] == '_y':
            df = df.drop(columns=column)

        elif column[len(column)-2:] == '_x':
            new_column_name = column[:len(column)-2]
            df.rename({column:new_column_name})

    return df

def merge_dataframes_on_different_column_names_on_right(df1,df2,left_on,right_on):
    merged_df = pd.merge(df1,df2,left_on=left_on,right_on=right_on, how='right', suffixes=('_y', ''))
    merged_df =rename_merged_dataframe(merged_df)


    return  merged_df


def merge_dataframes_on_different_column_names(df1,df2,left_on,right_on):
    merged_df = pd.merge(df1,df2,left_on=left_on,right_on=right_on, how='outer', suffixes=('', '_y'))
    merged_df = rename_merged_dataframe(merged_df)
    for column in merged_df.columns:
        print(column)
    return  merged_df



def merge_dataframes(df1,df2,on):

    return pd.merge(df1,df2,on=on)