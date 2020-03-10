from Functions.Filters import  *

def get_unique_values_from_column_in_list_format(df,column_name):
    return df[column_name].unique().tolist()


def get_team_player_dictionary(df,column_name1,column_name2):
    dict= {}

    teams= df[column_name1].unique().tolist()

    for team in teams:
        single_team = get_rows_where_column_equal_to(df,team,column_name1)
        dict[team] = get_unique_values_from_column_in_list_format(   single_team,column_name2)

    return dict