from Ratings.Main import  RatingGenerator
from TimeWeight.timeweightconfigurations import player_time_weight_methods
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
import time

parameter_configuration = {
    'time_weight_default_rating':{
        'parameter':[0.5],
        'games_played_div_factor': [5,8]
    },
    'time_weight_rating':{
        'parameter':[1.25],
        'games_played_div_factor':[5,8],
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


min_mean_abs_error = 9999999

for start_rating_quantile in [0.1,0.14]:

    for i in range(90):

        try:
            Rating = RatingGenerator(
                min_date="2015-07-01",
                max_date="2017-07-10",
                insert_final_file=False,
                parameter_configuration=configuration,
                start_rating_quantile=start_rating_quantile,
                verbose=False,
            )
            Rating.main()
            print("Rating model finished")
            break
        except Exception as e:

            print(e)
            time.sleep(400)

    Rating.all_series_all_team['rating_difference'] = Rating.all_series_all_team['time_weight_rating'] - \
                                                      Rating.all_series_all_team['opponent_time_weight_rating']
    mean_abs_error = abs(
        Rating.all_series_all_team['opponent_adjusted_performance_rating'] - Rating.all_series_all_team[
            'time_weight_rating']).mean()
    # logloss = get_logloss(Rating.all_series_all_team, "won", ["rating_difference"])
    print("Mean Abs Error", mean_abs_error, start_rating_quantile)

    if mean_abs_error < min_mean_abs_error:
        min_start_rating_quantile = start_rating_quantile

        print("Min logloss", mean_abs_error, start_rating_quantile)


print("Min logloss",mean_abs_error, min_default_parameter,min_default_div_factor,min_parameter,min_div_factor)