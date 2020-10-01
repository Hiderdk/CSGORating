from Ratings.Main import  RatingGenerator
from TimeWeight.timeweightconfigurations import player_time_weight_methods
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
import time
import traceback

parameter_configuration = {
        'time_weight_default_rating': {

        'column_name': 'opponent_adjusted_performance_rating',
        'column_names_equal_to': {'player_id':['player_id']},
        'parameter': 0.4,
        'max_days_ago': 500,
        'backup_column_name': 'start_time_weight_rating',
        'backup_source': "all_player",
        "games_played_weight": 1,
        'games_played_div_factor': 5,
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

}

start_rating_regions = {'Europe': 1800, 'Africa': -900, 'Asia': 0,
                        'North America': 940, 'South America': 0,
                        'Middle East': 100, 'Oceania': -200, 'Brazil': 500,None:0}

configuration = player_time_weight_methods

def get_logloss(df,target,feature):


    mean = df[feature].mean()
    std = df[feature].std()
    standardized_values =(df[feature]-mean)/std
    model = LogisticRegression().fit(standardized_values,df[target])
    prob = model.predict_proba(standardized_values)

    return log_loss(df[target],prob)


min_mean_abs_error = 9999999

performance_multipliers = [40000]

expected_player_percentage_contribution_betas = [9000]

for squared_performance_factor in [1.4]:
    for team_rating_prediction_beta in [5300]:
        for performance_multiplier in performance_multipliers:
            for expected_player_percentage_contribution_beta in expected_player_percentage_contribution_betas:

                for games_played_div_factor in [20,25]:

                    for start_rating_quantile in [0.1,0.13]:

                        for europe_start_rating in [1600,1800]:

                            for na_start_rating in [800,940]:

                                start_rating_regions['Europe'] = europe_start_rating
                                start_rating_regions['North America'] = na_start_rating


                                parameter_configuration['time_weight_rating']['games_played_div_factor'] = games_played_div_factor


                                st = time.time()

                                for i in range(90):

                                    try:
                                        Rating = RatingGenerator(
                                            min_date="2016-03-01",
                                            max_date="2016-11-10",
                                            insert_final_file=False,
                                            parameter_configuration=parameter_configuration,
                                            #start_rating_quantile=start_rating_quantile,
                                            verbose=False,
                                            update_frequency=15200,
                                            start_rating_quantile=start_rating_quantile,
                                            team_rating_prediction_beta=team_rating_prediction_beta,
                                            expected_player_percentage_contribution_beta = expected_player_percentage_contribution_beta,
                                            performance_multiplier = performance_multiplier,
                                            squared_performance_factor=squared_performance_factor
                                        )
                                        Rating.main()
                                        print("Rating model finished")
                                        break
                                    except Exception as e:
                                        traceback.print_exc()
                                        #print(e)
                                        time.sleep(400)

                                Rating.all_game_all_team['rating_difference'] = Rating.all_game_all_team['time_weight_rating'] - \
                                                                                  Rating.all_game_all_team['opponent_time_weight_rating']
                                mean_abs_error = abs(
                                    Rating.all_game_all_team['opponent_adjusted_performance_rating'] - Rating.all_game_all_team[
                                        'time_weight_rating']).mean()

                                game1 = Rating.all_game_all_team[Rating.all_game_all_team['game_number']==1]

                                min_logloss = 999

                                X = Rating.all_game_all_team[['rating_difference']]
                                y = Rating.all_game_all_team['won']
                                model = LogisticRegression().fit(X, y)
                                prob = model.predict_proba(X)
                                if log_loss(y, prob) < min_logloss:
                                    min_logloss = log_loss(y, prob)



                            print("logloss", min_logloss,europe_start_rating,na_start_rating,games_played_div_factor,start_rating_quantile,
                                  performance_multiplier,squared_performance_factor,expected_player_percentage_contribution_beta,team_rating_prediction_beta)
                            print(time.time()-st)




