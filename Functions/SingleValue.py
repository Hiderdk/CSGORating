import pandas as pd


def get_single_value_based_on_other_column_value(df,equal_to_value,equal_to_column_name,column_output):

    series = df[
        (df[equal_to_column_name] == equal_to_value)][column_output]
    if len(series) == 1:
        return series.iloc[0]
    else:
        return None

def get_single_value_based_on_other_column_value_where_rows_larger_than_1(df,equal_to_value,equal_to_column_name,column_output):
    series = df[
        (df[equal_to_column_name] == equal_to_value)][column_output]

    return series.iloc[0]



def get_single_value_from_column(df,column_name):
    return df[column_name].iloc[0]


def get_future_start_date_time_for_x_hours(date_time,hours):
    return pd.Timestamp(date_time) + pd.DateOffset(hours=hours)


def get_past_start_date_time_for_x_hours(date_time,hours):
    return pd.Timestamp(date_time) - pd.DateOffset(hours=hours)

def get_past_start_date_time_for_x_months(date_time,months):
    return pd.Timestamp(date_time) - pd.DateOffset(months=months)

def get_future_start_date_time_for_x_months(date_time,months):
    return pd.Timestamp(date_time) + pd.DateOffset(months=months)

