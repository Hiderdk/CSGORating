



fast_kill_kpr= {
    'filter_column_name':'time_weighted_opponent_adjusted_kpr',
    'filter_compared_to_column_name':'fast_time_weighted_opponent_adjusted_kpr',
    'filter_equal_to_names': {},
    'filter_min_equal_to_values': {},
    'filter_max_equal_to_values': {},
    'filter_not_equal_to_names': {},
    'min_difference':0.003,
    'max_difference':5000,
    'df_file_name':'process_all_game_all_player_rating',
    'error_column_name1':'kill_percentage',
    'error_column_name2': 'expected_kill_percentage',
}



fast_rating= {
    'filter_column_name':'time_weight_rating',
    'filter_compared_to_column_name':'fast_time_weight_rating',
    'filter_equal_to_names': {},
    'filter_min_equal_to_values': {'time_weight_rating_certain_ratio':0.5},
    'filter_max_equal_to_values': {'time_weight_rating_certain_ratio': 1},
    'filter_not_equal_to_names': {},
    'min_difference':40,
    'max_difference':5000,
    'df_file_name':'process_all_game_all_player_rating',
    'error_column_name1':'opponent_adjusted_performance_rating',
    'error_column_name2': 'time_weight_rating',
}


