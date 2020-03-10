def update_dataframe_based_on_index(df, index, column_name,  value ):

    df.at[index,column_name] = value

    return df


def update_value_based_on_other_column_value(df,column_value,column_name,output_column_name,output_column_value):
    df.loc[
        (df[column_name] == column_value)
        , output_column_name] = output_column_value

    return df


def update_dataframe_based_on_game_id_and_player_id(df ,game_id ,player_id ,column_name ,value):
    df.loc[
        (df['player_id'] == player_id) &
        (df['game_id'] == game_id)
        , column_name] = value

    return df


def update_dataframe_based_on_series_id_and_player_id(df,series_id,player_id,column_name,value):
    if player_id != None and series_id != None:
        df.loc[
            (df['player_id'] == player_id) &
            (df['series_id'] == series_id)
            , column_name] = value

    return df


def update_dataframe_based_on_series_id_and_team_id(df,series_id,team_id,column_name,value):
    if team_id != None and series_id != None:
        df.loc[
            (df['team_id'] == team_id) &
            (df['series_id'] == series_id)
            , column_name] = value

    return df


def update_dataframe_based_on_game_id_and_team_id(df,game_id,team_id,column_name,value):
    if team_id != None and game_id != None:
        df.loc[
            (df['team_id'] == team_id) &
            (df['game_id'] == game_id)
            , column_name] = value

    return df


def save_df_as_pickle(df,filepath,filename):
    full_file_name = filepath + '//'+filename
    df.to_pickle( full_file_name)