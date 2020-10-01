from trueskill import win_probability
def create_game_team_trueskill(df,trueskill,start_rating_quantile,start_ratings={}):
    team_ratings = {}

    game_ids = df['game_id'].unique().tolist()
    for game_id in game_ids:

        single_rows = df[df['game_id'] == game_id].sort_values(by='won', ascending=False)
        teams = []
        new_teams = [0, 0]
        team_ids = []
        indexes = []

        team_sigmas = []
        team_mus = []
        for index, row in single_rows.iterrows():
            indexes.append(index)
            team_id = row['team_id']
            team_ids.append(team_id)
            if team_id not in team_ratings:
                if start_ratings == {}:
                    start_rating = 25
                team_ratings[team_id] = trueskill.Rating(start_rating)

            team_sigmas.append(team_ratings[team_id].sigma)
            team_mus.append(team_ratings[team_id].mu)
            teams.append(team_ratings[team_id])

        new_teams[0], new_teams[1] = trueskill.rate_1vs1(teams[0], teams[1])
        win_prob = win_probability(teams[0], teams[1],trueskill.beta)
        df.at[indexes, 'prob'] = [win_prob, 1 - win_prob]
        df.at[indexes, 'sigma'] = team_sigmas
        df.at[indexes, 'mu'] = team_mus
        df.at[indexes, 'opponent_sigma'] = [team_sigmas[1],team_sigmas[0]]
        df.at[indexes, 'opponent_mu'] =[team_mus[1],team_mus[0]]

        for team_number, team_id in enumerate(team_ids):
            team_ratings[team_id] = new_teams[team_number]


    return df
