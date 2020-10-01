from trueskill import win_probability
import numpy as np

def create_game_player_trueskill(df, env, start_rating_quantile,start_ratings={}):
    player_ratings = {}
    region_players = {}
    region_players_rating = {}
    game_ids = df['game_id'].unique().tolist()
    for game_id in game_ids:

        single_rows = df[df['game_id'] == game_id].sort_values(by='won', ascending=False)
        if len(single_rows) != 10:
            continue

        team_ids = single_rows['team_id'].unique().tolist()
        single_game_player_ratings = {}
        single_game_player_regions= {}
        single_game_player_ids = {}
        team_player_sigmas = {}
        team_player_mus = {}
        indexes = []

        for team_number,team_id in enumerate(team_ids):

            single_game_player_ratings[team_number] = []

            single_game_player_regions[team_number] = []



            team_player_sigmas[team_number] = []
            team_player_mus[team_number] = []
            single_game_player_ids[team_id] = []

            single_team_rows = single_rows[single_rows['team_id']==team_id]
            for index, row in single_team_rows.iterrows():
                indexes.append(index)
                player_id = row['player_id']
                region = row['region']
                single_game_player_regions[team_number].append(region)
                single_game_player_ids[team_id].append(player_id)
                if player_id not in player_ratings:
                    if region not in region_players:
                        region_players[region] = []
                        region_players_rating[region] = []

                    count_region_players = len(region_players_rating[region])
                    if count_region_players > 60:
                        start_rating = np.percentile(region_players_rating[region], start_rating_quantile)  #
                    else:
                        start_rating = start_ratings[region]

                    player_ratings[player_id] = env.Rating(start_rating)


                    region_players[region].append(player_id)
                    region_players_rating[region].append(start_rating)



                single_game_player_ratings[team_number].append(player_ratings[player_id])
                team_player_sigmas[team_number].append(    player_ratings[player_id].sigma)
                team_player_mus[team_number].append(    player_ratings[player_id].mu)


            single_game_player_ratings[team_number] = tuple(single_game_player_ratings[team_number])


        all_sigmas = team_player_sigmas[0]+team_player_sigmas[1]
        all_mus = team_player_mus[0]+team_player_mus[1]
        all_opponent_sigmas = team_player_sigmas[1]+team_player_sigmas[1]
        all_opponent_mus = team_player_mus[1]+team_player_mus[1]
        t0 =    single_game_player_ratings[0]
        t1 = single_game_player_ratings[1]
        win_prob = win_probability(t0, t1,env.beta)
        all_probs = [win_prob,win_prob,win_prob,win_prob,win_prob,1-win_prob,1-win_prob,1-win_prob,1-win_prob,1-win_prob]
        df.at[indexes, 'prob'] = all_probs
        df.at[indexes, 'sigma'] = all_sigmas
        df.at[indexes, 'mu'] = all_mus
        df.at[indexes, 'opponent_sigma'] = all_opponent_sigmas
        df.at[indexes, 'opponent_mu'] = all_opponent_mus

        new_ratings = env.rate([t0,t1],ranks=[0,1])

        team_number = -1
        for team_id in  single_game_player_ids:
            team_number+=1
            for player_number,player_id in enumerate(single_game_player_ids[team_id]):
                region = single_game_player_regions[team_number][player_number]
                player_ratings[player_id] = new_ratings[team_number][player_number]

                ix = region_players[region].index(player_id)
                region_players_rating[ix] = player_ratings[player_id].mu


    all_game_all_team = df.groupby(['game_id','team_id','start_date_time','team_name','game_number','won'])[['prob','sigma','mu','opponent_mu','opponent_sigma']].mean().reset_index()

    return all_game_all_team
