import trueskill
from trueskill_generator.game_team import  create_game_team_trueskill
from trueskill_generator.game_player import  create_game_player_trueskill
import pandas as pd
from sklearn.metrics import log_loss
from sklearn.linear_model import LogisticRegression
filepath_dataframes =r"C:\Users\Mathias\PycharmProjects\Ratings\Files"
df_file_name = "all_game_all_player_rating"
all_game_all_player =  pd.read_pickle(filepath_dataframes + "//" + df_file_name).sort_values(by=['start_date_time','game_number'])
all_game_all_player = all_game_all_player[all_game_all_player['start_date_time'].between('2015-07-01','2016-04-01')]


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
    'sigma':[0.5,0.75,1,1.5,2],
    'beta':[0.5,0.75,1,1.5,2],
    'tau':[0.08,0.1,0.15]
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

    return min (logloss_ts,logloss_logistic)


best_score = 999
for sigma in parameters['sigma']:
    for beta in parameters['beta']:
        for tau in parameters['tau']:

            env = trueskill.setup(sigma=sigma, beta=beta, tau=tau)
            all_game_all_player = create_game_player_trueskill(all_game_all_player.copy(), env)
            logloss = get_logloss(all_game_all_player)

            if logloss < best_score:
                best_score = logloss
                best_sigma = sigma
                best_entity = "player"
                best_tau = tau
                best_beta = beta

            print("player", sigma, beta, tau, logloss)

            trueskill.setup(sigma=sigma, beta=beta, tau=tau)
            all_game_all_team = create_game_team_trueskill(all_game_all_team.copy(),env)

            logloss = get_logloss(all_game_all_team)

            if logloss < best_score:
                best_score = logloss
                best_sigma = sigma
                best_entity = "team"
                best_tau = tau
                best_beta = beta

            print("team",sigma,beta,tau,logloss)





print(best_score,best_entity,best_sigma,best_beta,best_tau)

