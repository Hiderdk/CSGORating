from Functions.Miscellaneous import *

player_time_weight_methods = {


    'time_weighted_opponent_adjusted_kpr': {

        'column_name': 'opponent_adjusted_kpr',
        'column_names_equal_to': ['player_id'],
        'parameter': 1.3,
        'max_days_ago': 500,
        'hardcoded_backup_value':25,
        'weight_multiplier': 'team_kills_weight_ratio',
        "games_played_weight": 0.2,
        'games_played_div_factor': 40,
    },



    'default_rating': {

        'column_name': 'opponent_adjusted_performance_rating',
        'column_names_equal_to': ['player_id'],
        'parameter': 0.2,
        'max_days_ago': 500,
        'backup_column_name': 'start_rating',
        'backup_calculation': get_start_rating,
        "games_played_weight": 1,
        'games_played_div_factor': 30,
    },

    'rating': {

        'column_name':'opponent_adjusted_performance_rating',
        'column_names_equal_to':['player_id'],
        'parameter': 1.2,
        'max_days_ago': 500,
        'backup_column_name': 'default_rating',
        "games_played_weight": 0.05,
        'games_played_div_factor':60,
    },

}

