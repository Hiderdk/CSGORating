from Functions.Miscellaneous import *

player_time_weight_methods = {

    'time_weighted_default_opponent_adjusted_kpr': {

        'column_name': 'opponent_adjusted_kpr',
        'column_names_equal_to': ['player_id'],
        'parameter': 0.2,
        'max_days_ago': 500,
        'hardcoded_backup_value': 0.68,
        "games_played_weight": 1,
        'games_played_div_factor': 70,
    },

    'time_weighted_opponent_adjusted_kpr': {

        'column_name': 'opponent_adjusted_kpr',
        'column_names_equal_to': ['player_id'],
        'parameter': 1.5,
        'max_days_ago': 140,
        'backup_column_name': 'time_weighted_default_opponent_adjusted_kpr',
        "games_played_weight": 0.05,
        'games_played_div_factor': 70,
    },

    'fast_time_weighted_opponent_adjusted_kpr': {

        'column_name': 'opponent_adjusted_kpr',
        'column_names_equal_to': ['player_id'],
        'parameter': 2,
        'max_days_ago': 140,
        'backup_column_name': 'time_weighted_default_opponent_adjusted_kpr',
        "games_played_weight": 0.05,
        'games_played_div_factor': 70,
    },

    'time_weight_default_rating': {

        'column_name': 'opponent_adjusted_performance_rating',
        'column_names_equal_to': ['player_id'],
        'parameter': 0.3,
        'max_days_ago': 500,
        'backup_column_name': 'start_time_weight_rating',
        'backup_source':"all_player",
        "games_played_weight": 1,
        'games_played_div_factor': 35,
    },

    'time_weight_rating': {

        'column_name': 'opponent_adjusted_performance_rating',
        'column_names_equal_to': ['player_id'],
        'parameter': 1.2,
        'max_days_ago': 100,
        'backup_column_name': 'time_weight_default_rating',
        "games_played_weight": 0.05,
        'games_played_div_factor': 75,
    },

    'fast_time_weight_rating': {

        'column_name': 'opponent_adjusted_performance_rating',
        'column_names_equal_to': ['player_id'],
        'parameter': 1.7,
        'max_days_ago': 100,
        'backup_column_name': 'time_weight_default_rating',
        "games_played_weight": 0.05,
        'games_played_div_factor': 75,
    },





}

