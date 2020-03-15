from Functions.Miscellaneous import *

player_time_weight_methods = {

    'time_weight_default_rating': {

        'column_name': 'opponent_adjusted_performance_rating',
        'column_names_equal_to': ['player_id'],
        'parameter': 0.3,
        'max_days_ago': 500,
        'backup_column_name': 'start_time_weight_rating',
        'backup_source':"all_player",
        "games_played_weight": 1,
        'games_played_div_factor': 50,
    },

    'time_weight_rating': {

        'column_name': 'opponent_adjusted_performance_rating',
        'column_names_equal_to': ['player_id'],
        'parameter': 1,
        'max_days_ago': 100,
        'backup_column_name': 'time_weight_default_rating',
        "games_played_weight": 0.05,
        'games_played_div_factor': 120,
    },

    'fast_time_weight_rating': {

        'column_name': 'opponent_adjusted_performance_rating',
        'column_names_equal_to': ['player_id'],
        'parameter': 1.4,
        'max_days_ago': 100,
        'backup_column_name': 'time_weight_default_rating',
        "games_played_weight": 0.05,
        'games_played_div_factor': 120,
    },

    'time_weighted_opponent_adjusted_kpr': {

        'column_name': 'opponent_adjusted_kpr',
        'column_names_equal_to': ['player_id'],
        'parameter': 1.3,
        'max_days_ago': 500,
        'hardcoded_backup_value':0.68,
        "games_played_weight": 0.2,
        'games_played_div_factor': 70,
    },




}

