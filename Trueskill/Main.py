from trueskill import Rating, quality_1vs1, rate_1vs1,global_env
alice, bob = Rating(25), Rating(30)  # assign Alice and Bob's ratings
import itertools
from SQL import *
import pandas as pd
df = get_game_team("2019-10-01").sort_values(by='start_date_time',ascending=True)
team_name = df['team_name'].unique().tolist()
ratings = {}
for team_name in team_name:
    ratings[team_name] = Rating(25)
game_ids = df['game_id'].unique().tolist()

import itertools
import math

def get_win_probability(team1, team2):
    sigma1 = [getattr(team1,"sigma")]
    sigma2 = [getattr(team2, "sigma")]
    delta_mu = getattr(team1,"mu")-getattr(team2,"mu")
    sum_sigma = sum(r ** 2 for r in itertools.chain(sigma1,sigma2))
    size = 2
    BETA = (sigma1[0]+sigma2[0])*2
    denom = math.sqrt(2 * (BETA * BETA) +  sum_sigma)
    ts = global_env()
    probability =  ts.cdf(delta_mu / denom)
    if probability > 0.9:
        h = 3
    return ts.cdf(delta_mu / denom)





for game_id in game_ids:
    single_game = df[df['game_id']==game_id]
    winner = single_game[single_game['won']==1]['team_name'].item()
    loser = single_game[single_game['won']==0]['team_name'].item()

    win_probability = get_win_probability(ratings[winner],ratings[loser])

    #TrueSkill(mu=MU, sigma=SIGMA, beta=BETA, tau=TAU,
                    # draw_probability=DRAW_PROBABILITY, backend=None)
    ratings[winner], ratings[loser] =rate_1vs1(ratings[winner], ratings[loser], drawn=False)

    print(getattr(ratings[winner],"mu")-getattr(ratings[loser],"mu"),winner,loser,win_probability)