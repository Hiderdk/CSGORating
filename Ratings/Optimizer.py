from Ratings.Main import  RatingGenerator
from TimeWeight.timeweightconfigurations import player_time_weight_methods
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
import time

parameter_configuration = {
    'time_weight_default_rating':{
        'parameter':[0.5],
        'games_played_div_factor': [10]
    },
    'time_weight_rating':{
        'parameter':[1,1.15],
        'games_played_div_factor':[45],
        'max_days_ago':[120]
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
                for max_days_ago in parameter_configuration['time_weight_rating']['max_days_ago']:

                    configuration['time_weight_default_rating']['parameter'] = default_parameter
                    configuration['time_weight_default_rating']['games_played_div_factor'] = default_div_factor
                    configuration['time_weight_rating']['parameter'] = parameter
                    configuration['time_weight_rating']['games_played_div_factor'] = div_factor
                    configuration['time_weight_rating']['max_days_ago'] = max_days_ago
                    for i in range(90):

                        try:
                            Rating = RatingGenerator(
                                min_date="2016-01-04",
                                max_date="2016-05-10",
                                insert_final_file=False,
                                parameter_configuration=configuration,
                                verbose=False,
                            )
                            Rating.main()
                            print("Rating model finished")
                            break
                        except Exception as e:
                            print(e)
                            time.sleep(400)

                    Rating.all_series_all_team['rating_difference'] =  Rating.all_series_all_team['time_weight_rating']-Rating.all_series_all_team['opponent_time_weight_rating']
                    mean_abs_error = abs(Rating.all_series_all_team['opponent_adjusted_performance_rating']   -Rating.all_series_all_team['time_weight_rating']).mean()
                    #logloss = get_logloss(Rating.all_series_all_team, "won", ["rating_difference"])
                    print("Mean Abs Error", mean_abs_error, default_parameter, default_div_factor, parameter, div_factor,max_days_ago)

                    if mean_abs_error < min_mean_abs_error:
                        min_default_parameter = default_parameter
                        min_default_div_factor = default_div_factor
                        min_parameter = parameter
                        min_div_factor = div_factor
                        min_mean_abs_error = mean_abs_error
                        min_max_days_ago = max_days_ago

                        print("Min logloss", mean_abs_error, min_default_parameter, min_default_div_factor, min_parameter,
                              min_div_factor,min_max_days_ago)


print("Min logloss",min_logloss, min_default_parameter,min_default_div_factor,min_parameter,min_div_factor)