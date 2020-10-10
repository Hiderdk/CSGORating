player_time_weight_methods = {

    'time_weight_default_rating': {

        'column_name': 'opponent_adjusted_performance_rating',
        'column_names_equal_to': {'player_id':['player_id']},
        'parameter': 0.5,
        'max_days_ago': 500,
        'backup_column_name': 'start_time_weight_rating',
        'backup_source': "all_player",
        "games_played_weight": 1,
        'games_played_div_factor': 6,
    },

    'time_weight_rating': {

        'column_name': 'opponent_adjusted_performance_rating',
        'column_names_equal_to': {'player_id':['player_id']},
        'parameter': 1.15,
        'max_days_ago': 120,
        'backup_column_name': 'time_weight_default_rating',
        "games_played_weight": 0.05,
        'games_played_div_factor': 20,
    },

    'map_time_weight_rating': {

        'column_name': 'opponent_adjusted_performance_rating',
        'column_names_equal_to': {'player_id': ['player_id'],'map':'map'},
        'parameter': 9,
        'max_days_ago': 120,
        'backup_column_name': 'time_weight_rating',
        "games_played_weight": 0.05,
        'games_played_div_factor': 25,
    },


    'time_weighted_default_kpr': {

        'column_name': 'kpr',
        'column_names_equal_to': {'player_id': ['player_id']},
        'parameter': 0.3,
        'max_days_ago': 500,
        'hardcoded_backup_value': 0.68,
        "games_played_weight": 1,
        'games_played_div_factor': 35,
    },

    'time_weighted_kpr': {

        'column_name': 'kpr',
        'column_names_equal_to': {'player_id': ['player_id']},
        'parameter': 1.2,
        'max_days_ago': 140,
        'backup_column_name': 'time_weighted_default_kpr',
        "games_played_weight": 0.05,
        'games_played_div_factor': 30,
    },

    'time_weighted_default_opponent_adjusted_kpr': {

        'column_name': 'opponent_adjusted_kpr',
        'column_names_equal_to':{'player_id':['player_id']},
        'parameter': 0.3,
        'max_days_ago': 500,
        'hardcoded_backup_value': 0.68,
        "games_played_weight": 1,
        'games_played_div_factor': 15,
    },

    'time_weighted_opponent_adjusted_kpr': {

        'column_name': 'opponent_adjusted_kpr',
        'column_names_equal_to': {'player_id':['player_id']},
        'parameter': 1.2,
        'max_days_ago': 140,
        'backup_column_name': 'time_weighted_default_opponent_adjusted_kpr',
        "games_played_weight": 0.05,
        'games_played_div_factor': 30,
    },

    'fast_time_weighted_opponent_adjusted_kpr': {

        'column_name': 'opponent_adjusted_kpr',
        'column_names_equal_to': {'player_id':['player_id']},
        'parameter': 1.5,
        'max_days_ago': 140,
        'backup_column_name': 'time_weighted_default_opponent_adjusted_kpr',
        "games_played_weight": 0.05,
        'games_played_div_factor': 30,
    },

    'map_time_weighted_opponent_adjusted_kpr': {

        'column_name': 'opponent_adjusted_kpr',
        'column_names_equal_to': {'map':['mirage','inferno','dust2','nuke','overpass','vertigo','train'],'player_id':['player_id']},
        'parameter': 1.2,
        'max_days_ago': 170,
        'backup_column_name': 'time_weighted_opponent_adjusted_kpr',
        "games_played_weight": 0.05,
        'games_played_div_factor': 15,
    },

}

