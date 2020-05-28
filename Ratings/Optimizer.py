from Ratings.Main import  RatingGenerator
from TimeWeight.timeweightconfigurations import player_time_weight_methods
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

parameter_configuration = {
    'time_weight_default_rating':{
        'parameter':[0.6,0.8],
        'games_played_div_factor': [25,35]
    },
    'time_weight_rating':{
        'parameter':[0.8,0.95],
        'games_played_div_factor':[50,65]
    }
}

configuration = player_time_weight_methods

def get_logloss(df,target,feature):
    mean = df[feature].mean()
    std = df[feature].std()
    standardized_values =(df[feature]-mean)/std
    model = LogisticRegression().fit(standardized_values,df[target])
    prob = model.predict_proba(standardized_values)

    return log_loss(df[target],prob)


min_logloss = 999

for default_parameter in parameter_configuration['time_weight_default_rating']['parameter']:
    for default_div_factor in  parameter_configuration['time_weight_default_rating']['games_played_div_factor']:

        for parameter in parameter_configuration['time_weight_rating']['parameter']:
            for div_factor in parameter_configuration['time_weight_rating']['games_played_div_factor']:

                configuration['time_weight_default_rating']['parameter'] = default_parameter
                configuration['time_weight_default_rating']['games_played_div_factor'] = default_div_factor
                configuration['time_weight_rating']['parameter'] = parameter
                configuration['time_weight_rating']['games_played_div_factor'] = div_factor


                Rating = RatingGenerator(
                    min_date="2016-01-01",
                    max_date="2016-01-05",
                    insert_final_file=False,
                    parameter_configuration=configuration,
                    verbose=False,
                )
                Rating.main()
                Rating.all_game_all_team['rating_difference'] =  Rating.all_game_all_team['time_weight_rating']-Rating.all_game_all_team['opponent_time_weight_rating']
                logloss = get_logloss( Rating.all_game_all_team, "won",["rating_difference"])
                if logloss < min_logloss:
                    min_default_parameter = default_parameter
                    min_default_div_factor = default_div_factor
                    min_parameter = parameter
                    min_div_factor = div_factor
                    min_logloss = logloss

                    print("Min logloss", min_default_parameter,min_default_div_factor,min_parameter,min_div_factor)

