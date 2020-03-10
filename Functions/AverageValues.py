def get_mean_from_pandas_series(series):
    if len(series) >= 1:
        return series.mean()
    else:
        return 0

def get_average_value_from_column_name(df,column_name):

    series = df[column_name].dropna()

    return get_mean_from_pandas_series(series)