import trueskill
from trueskill_generator.game_team import  create_game_team_trueskill
from trueskill_generator.game_player import  create_game_player_trueskill
import pandas as pd
from sklearn.metrics import log_loss
from sklearn.linear_model import LogisticRegression
filepath_dataframes =r"C:\Users\Mathias\PycharmProjects\Ratings\Files"
df_file_name = "all_game_all_player_rating"
all_game_all_player =  pd.read_pickle(filepath_dataframes + "//" + df_file_name).sort_values(by=['start_date_time','game_number'])
all_game_all_player = all_game_all_player[all_game_all_player['start_date_time'].between('2015-07-01','2016-07-01')]


group_sum = all_game_all_player.groupby(['team_id', 'game_id'])['kills'].sum().reset_index()



all_game_all_team = all_game_all_player.groupby(
    ['opponent_region', 'rounds_won', 'rounds_lost', 'team_id', 'team_name', 'team_id_opponent', 'game_id',
     'start_date_time', 'game_number', 'series_id'])[
    ['opponent_adjusted_performance_rating', 'won', 'time_weight_rating',
     'time_weight_rating_certain_ratio']].mean().reset_index()

# self.all_game_all_team =  merge_dataframes_on_different_column_names_on_right(self.all_team,self.all_game_all_team,"team_id","team_id")
all_game_all_team = pd.merge(group_sum, all_game_all_team, on=['team_id', 'game_id'])
all_game_all_team['lost'] = -all_game_all_team['won'] + 1
sub_df = all_game_all_team[
    ['time_weight_rating_certain_ratio', 'time_weight_rating', 'game_id', 'team_id_opponent']]. \
    rename(columns={"time_weight_rating": "opponent_time_weight_rating",
                    "time_weight_rating_certain_ratio": "opponent_time_weight_rating_certain_ratio"})

all_game_all_team = pd.merge(sub_df, all_game_all_team, left_on=['game_id', 'team_id_opponent'],
                                  right_on=['game_id', 'team_id'])


start_rating = 25


trueskill.setup(draw_probability=0)

parameters = {
    'sigma':[4],
    'beta':[6],
    'tau':[0.02,0.03]
}



def get_logloss(df):
    logloss_ts = log_loss(df['won'], df['prob'])

    df['rating_difference'] = df['mu'] - df['opponent_mu']

    model = LogisticRegression()
    X = df[['rating_difference']]
    y = df['won']
    model.fit(X, y)
    df['prob_lr'] = model.predict_proba(X)[:, 1]
    logloss_logistic = log_loss(y, df['prob_lr'])

    return logloss_ts,logloss_logistic

start_rating_regions = {'Europe': 25, 'Africa': 25, 'Asia': 25,
                        'North America': 25, 'South America': 25,
                        'Middle East': 25, 'Oceania': 25, 'Brazil': 25,None:25}


best_score = 999
for sigma in parameters['sigma']:
    for beta in parameters['beta']:
        for tau in parameters['tau']:

            for eu_start_rating in [26,26.5,27]:

                for na_start_rating in [25.5,26]:

                    for start_rating_quantile in [13,18,25]:

                        start_rating_regions['Europe'] = eu_start_rating
                        start_rating_regions['North America'] = na_start_rating

                        env = trueskill.setup(sigma=sigma, beta=beta, tau=tau)
                        new_game_team = create_game_player_trueskill(all_game_all_player.copy(), env,start_rating_quantile,start_ratings=start_rating_regions)
                        logloss_ts,logloss_logistic = get_logloss(new_game_team)

                        logloss = min(logloss_ts,logloss_logistic )
                        if logloss < best_score:
                            best_score = logloss
                            best_sigma = sigma
                            best_entity = "player"
                            best_tau = tau
                            best_beta = beta

                        print("player", logloss_ts,logloss_logistic,sigma, beta, tau)

                        def run_team():
                            trueskill.setup(sigma=sigma, beta=beta, tau=tau)
                            new_all_game_all_team = create_game_team_trueskill(all_game_all_team.copy(),env,start_rating_quantile,start_ratings=start_rating_regions)

                            team_logloss_ts,team_logloss_logistic = get_logloss(new_all_game_all_team)
                            logloss = min(team_logloss_ts, team_logloss_logistic)
                            if logloss < best_score:
                                best_score = logloss
                                best_sigma = sigma
                                best_entity = "team"
                                best_tau = tau
                                best_beta = beta

                            print("team",team_logloss_ts,team_logloss_logistic,sigma,beta,tau,logloss)





print(best_score,best_entity,best_sigma,best_beta,best_tau)

