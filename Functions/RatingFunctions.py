import pandas as pd

def calculate_estimated_rating(certain_ratio,weighted_rating,backup_rating):
    return certain_ratio * weighted_rating + (1 - certain_ratio) * backup_rating


def calculate_certain_ratio(days_ago,games_played_weight):
    games_played = len(days_ago)
    if games_played == 0:
        return 0
    games_played_ratio = (1/(1+10**(-games_played/124))-0.5)*2
    sum_date_ratio= sum( days_ago )
    recency_cv =  (1/(1+10**(- sum_date_ratio /69))-0.5)*2

    certain_ratio = games_played_weight*games_played_ratio+(1-games_played_weight)*    recency_cv
        #### CREATE FUNCTION THAT has a ratio between 0 and 1. The more games played and the more recent they are the closer to 1 it is.
    return certain_ratio


def get_most_frequent_column_name( df,column_name):
    from Functions.Miscellaneous import  groupby_count
    new_df = groupby_count(df,column_name)
    return     new_df .loc[ new_df [0].idxmax(), column_name]

if __name__ == '__main__':
    dict = {
        'region':['denmark','troll','denmark','troll','troll',"usa"],

    }
    df = pd.DataFrame.from_dict(dict)
    v = get_most_frequent_column_name(df,"region")
    print(v)


