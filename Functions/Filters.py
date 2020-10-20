import numpy as np


def get_offline_dataframe(df):
    return df[df['is_offline']==1]

import pandas as pd
def get_rows_where_column_less_than_other_column(df,value,column_name,other_column_name):
    return df.loc[df[column_name]-df[other_column_name]<value]

def get_rows_where_column_larger_than_other_column(df,value,column_name,other_column_name):
    return df.loc[df[column_name]-df[other_column_name]>value]


def get_same_df(df):
    return df


def  get_rows_where_column_is_not_equal_to(df,value,column_name):
    return df[df[column_name]!=value]


def get_rows_where_column_between(df,min_value,max_value,column_name):
    new_df = df[df[column_name].between(min_value,max_value)]

    return new_df

def get_rows_where_column_less_than(df,equal_to_value,equal_to_column_name):

    new_df= df[
        (df[equal_to_column_name] < equal_to_value)]
    return new_df

def get_rows_where_column_contains(df,string,column_name):
    new_df = df.loc[
        (df[column_name].str.contains(string))]
    return new_df

def get_rows_where_column_equal_to(df,equal_to_value,equal_to_column_name):

    new_df= df[
        (df[equal_to_column_name] == equal_to_value)]
    return new_df

def get_rows_where_column_larger_than_and_is_offline(df,larger_than_value,larger_than_column_name):

    new_df= df[
        (df[larger_than_column_name] > larger_than_value) &
        (df['is_offline']==1)]
    return new_df

def get_rows_where_column_larger_than(df,larger_than_value,larger_than_column_name):

    new_df= df[
        (df[larger_than_column_name] > larger_than_value)]
    return new_df

def get_rows_where_is_in(df,isin_values,column_name):

    return df.loc[df[column_name].isin(isin_values)]


def get_rows_where_is_in_and_is_offline(df,isin_values,column_name):

    return df.loc[df[column_name].isin(isin_values) &
                  (df['is_offline']==1)]

def get_first_row(df):
    return df.head(1)


def get_single_game_single_player_df(df,game_id,player_id):
    new_df = df[
        (df['game_id'] == game_id) &
        (df['player_id']==player_id)]

    return new_df



def get_rows_based_date_and_player_id_for_2_dataframes(x, data, days_difference):
    """count the player's kills in a time window before the time of current row.
    x: dataframe row
    data: full dataframe
    timewin: a pandas.Timedelta
    """
    return data.loc[(data['start_date_time'] < x['start_date_time']) #select dates preceding current row
            & (data['start_date_time'] >= x['start_date_time']-days_difference) #select dates in the timewin
            & (data['player_id'] == x['player_id'])]#select rows with same player




def get_months_ago_game_rows(df,date_time,months):
    min_date = pd.Timestamp(date_time) - pd.DateOffset(months=months)

    new_df = df[df['start_date_time']>=min_date]
    return new_df


def get_rows_by_map_name(df,map_name):

    if map_name != 'All':
        new_df = df[
            (df['map'] == map_name)]
    else:
        new_df = df

    return new_df

def get_loot_dataframe(df):
    new_df = df.loc[
        (df['organization'] == 'LOOT.BET')]
    return new_df


def get_ecs_dataframe(df):
    new_df = df.loc[
        (df['organization'] == 'ECS')]
    return new_df

def get_2019_dataframe(df):
    new_df = df[df['start_date_time'].between("2019-01-01","2020-01-01")]
    return new_df

def get_ecc_dataframe(df):
    new_df = df.loc[
        (df['tournament_name'] =="European Champions Cup")]
    return new_df

def get_wesg_dataframe(df):
    new_df = df.loc[
        (df['tournament_name'].str.contains("WESG"))]
    return new_df

def get_ecs_dataframe(df):
    new_df = df.loc[
        (df['tournament_name'] =="ECS")]
    return new_df

def get_dataframe_from_start_date_time(df,min_start_date_time):
    return df[df['start_date_time']>=min_start_date_time]


def get_ecs_s8_dataframe(df):
    new_df = df.loc[
        (df['tournament_name'].str.contains("ECS Season 8"))]
    return new_df

def get_ecs_s8_eu_dataframe(df):
    new_df = df.loc[
        (df['tournament_name'].str.contains("ECS Season 8 Europe"))]
    return new_df


def get_ecs_s8_na_dataframe(df):
    new_df = df.loc[
        (df['tournament_name'].str.contains("ECS Season 8 North America"))]
    return new_df

def get_uml_dataframe(df):
    new_df = df.loc[
        (df['tournament_name'].str.contains("United Masters League"))]
    return new_df

def get_uml_s2_dataframe(df):
    new_df = df.loc[
        (df['tournament_name'].str.contains("United Masters League Season 2"))]
    return new_df


def get_loot_s4_dataframe(df):
    new_df = df.loc[
        (df['tournament_name'].str.contains("LOOT.BET Season 4"))]
    return new_df



