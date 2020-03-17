



fast_kill_kpr= {
    'filter_column_name':'time_weighted_default_opponent_adjusted_kpr',
    'filter_compared_to_column_name':'time_weighted_opponent_adjusted_kpr',
    'filter_equal_to_names': {},
    'filter_min_equal_to_values': {},
    'filter_max_equal_to_values': {},
    'filter_not_equal_to_names': {},
    'min_difference':0.01,
    'max_difference':5000,
    'df_file_name':'all_game_all_player_rating',
    'error_column_name1':'kpr',
    'error_column_name2': 'time_weighted_opponent_adjusted_kpr',
}



fast_rating= {
    'filter_column_name':'time_weight_rating',
    'filter_compared_to_column_name':'fast_time_weight_rating',
    'filter_equal_to_names': {},
    'filter_min_equal_to_values': {'time_weight_rating_certain_ratio':0.5},
    'filter_max_equal_to_values': {'time_weight_rating_certain_ratio': 1},
    'filter_not_equal_to_names': {},
    'min_difference':100,
    'max_difference':5000,
    'df_file_name':'all_game_all_player_rating',
    'error_column_name1':'opponent_adjusted_performance_rating',
    'error_column_name2': 'time_weight_rating',
}



fast_league_time_weighted_kills_testing= {
    'filter_column_name':'league_time_weighted_kills',
    'filter_compared_to_column_name':'fast_league_time_weighted_kills',
    'filter_equal_to_names': {},
    'filter_min_equal_to_values': {'tournament_count':5},
    'filter_max_equal_to_values': {'tournament_count':80},
    'filter_not_equal_to_names': {},
    'min_difference':0.0004,
    'max_difference':5,
    'df_file_name':'game_team',
    'error_column_name1':'total_kills',
    'error_column_name2': 'league_time_weighted_kills',
}

league_time_weighted_kills_testing= {
    'filter_column_name': 'time_weighted_total_kills',
    'filter_compared_to_column_name': 'league_time_weighted_kills',
    'filter_equal_to_names': {},
    'filter_min_equal_to_values': {'time_weighted_kills_certain_ratio': 0.65},
    'filter_max_equal_to_values': {'time_weighted_kills_certain_ratio': 1},
    'filter_not_equal_to_names': {},
    'min_difference': 0.04,
    'max_difference': 5,
    'df_file_name': 'game_team',
    'error_column_name1': 'total_kills',
    'error_column_name2': 'time_weighted_total_kills',


}


