from settings import *
from SQL import *
import datetime
from trueskill_generator.run_trueskill import  *
from trueskill_generator.game_player import get_trueskill_start_rating
from trueskill import get_trueskill_win_probability
import traceback
from Functions.Lists import *
from Ratings.SingleGame import SingleGameRatingGenerator

from Predictions.ScenarioProbabilities import KillsScenarioProbabilityGenerator
from Functions.GoogleSheets import *
from Functions.AverageValues import create_average_over_under_df
from TimeWeight.timeweightconfigurations import player_time_weight_methods
from Functions.Miscellaneous import scale_features_and_insert_to_dataframe
from Functions.GoogleSheets import read_google_sheet
MAXDAYCOUNTSHEET_LOW_TIER = 2
MAXDAYCOUNTSHEET_HIGHTIER = 10
from Predictions.SeriesWin import SeriesWinProbability
ot_default_probability = 0.093

ACTIVE_MAPS = ['mirage','dust2','train','nuke','inferno','overpass','vertigo']
covered_tournaments = ['ESL Pro League Season 11 North America']

class SeriesPredictionGenerator():

    def __init__(self, make_sheet_for_newest_series_only=False, calculcate_win_probabilities=True, calculcate_kill_probabilities=True):
        self.make_sheet_for_newest_series_only = make_sheet_for_newest_series_only
        self.calculcate_win_probabilities = calculcate_win_probabilities
        self.calculcate_kill_probabilities = calculcate_kill_probabilities

        self.player_ratings = {}
        self.ml_models_dict = {
            "won": pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\csgo_new_won_model"),
            "won_regular": pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\csgo_new_regular_won_model"),
            'won_stacked': pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\game_winner_model"),
            'won_map_stacked': pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\game_winner_model_map"),
            'won_pick_map_stacked': pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\game_winner_model_map_picked"),

        }
        self.workbook_name = "CSGO"
        self.schedule_dict = {
            'Date':[],
            'Tournament':[],
            'Team1':[],
            'Team2':[],
            'Win Probability1':[],
            'Win Probability2':[],
            'Series Win Probability1':[],
            'Series Win Probability2': [],
            'Match Uncertain Ratio': [],
            'Sheet Name':[],
        }


    def load_data(self):
        self.ts_player_ratings = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\player_ratings")
        self.ts_region_players = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\region_players")
        self.ts_region_players_rating = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\region_players_rating")

        self.all_game_all_team = pd.read_pickle(
            local_file_path + "//_newall_game_all_team_rating").sort_values(by=['start_date_time','game_number'],
                                                                                      ascending=[False,False])
        self.all_game_all_player = pd.read_pickle(local_file_path+"//_newall_game_all_player_rating").sort_values(by=['start_date_time','game_number'],ascending=False)
        self.all_game_all_player = self.all_game_all_player[self.all_game_all_player['opponent_region'].notna()]


        self.all_player = pd.read_pickle(local_file_path + "//_newall_player")
        self.all_team = pd.read_pickle(local_file_path + "//_newall_team")
        self.uncertainty_model = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\uncertainty_model")


        st = time.time()
        for index,row in self.all_team.iterrows():
            team_id = row['team_id']
            team_name = row['team_name']
            self.all_game_all_team.loc[self.all_game_all_team['team_id_opponent_y']==team_id,'team_name_opponent'] = team_name

        print(time.time()-st)
        min_date =datetime.datetime.now()- datetime.timedelta(0.2)
        pre_series_player = get_all_from_series_player(min_date).sort_values(by=['start_date_time'],ascending=True)
        historical_series_ids =  self.all_game_all_player ['series_id'].unique().tolist()
        self.future_series_player = pre_series_player[~pre_series_player.series_id.isin(        historical_series_ids)]





    def calculcate_team_certain_ratio(self,team_player_ids,player_stored_values):
        team_certain_ratios = []
        for team,player_ids in team_player_ids.items():
            certain_ratios = []
            for player_id in player_ids:

                certain_ratio = player_stored_values[player_id]['time_weight_rating_certain_ratio']
                certain_ratios.append(certain_ratio)

            team_certain_ratios.append(sum(certain_ratios)/len(certain_ratios))

        return team_certain_ratios


    def generate_averaged_squared_team_certain_ratio(self,team_certain_ratios,squared_factor=0.5):
        team_squared_certain_ratios = []
        for team_number,certain_ratio in enumerate(team_certain_ratios):

            squared_certain_ratio = certain_ratio**squared_factor
            team_squared_certain_ratios.append(squared_certain_ratio)

        return team_squared_certain_ratios[0]*0.5+team_squared_certain_ratios[1]*0.5


    def get_trueskill_team_players(self,team_player_ids):
        trueskill_team_players = {}
        team_number = -1
        for team in team_player_ids:
            team_number+=1
            trueskill_team_players[team_number] = []
            for player_id in team_player_ids[team]:
                if player_id not in self.ts_player_ratings:
                    region = self.all_player[self.all_player['player_id']==player_id]['region'].iloc[0]
                    start_rating = get_trueskill_start_rating(self.ts_region_players, region, self.ts_region_players_rating, start_rating_quantile,
                                               start_rating_regions)
                    self.ts_player_ratings[player_id] = Rating(start_rating,sigma=sigma)


                trueskill_team_players[team_number].append( self.ts_player_ratings[player_id])


        return trueskill_team_players


    def main(self):

        self.all_game_all_player['games_played'] = self. all_game_all_player.groupby(['player_id']).cumcount()
        min_date= datetime.datetime.today() - datetime.timedelta(2 * 30)
        insert_team = self.all_team[self.all_team['most_recent_date']>min_date].sort_values(by='time_weight_rating',ascending=False).head(150)[['team_name','time_weight_rating']]
        append_df_to_sheet(round(insert_team,0),"TeamRank",self.workbook_name)


        series_ids = self.future_series_player['series_id'].unique().tolist()

        existing_sheet_names = get_sheet_names(self.workbook_name)
        #schedule_df = read_google_sheet("Schedule",self.workbook_name)
       # self.schedule_dict = {}
        #for column in schedule_df.columns:
       #  #   self.schedule_dict[column] = []
       # for index,row in schedule_df.iterrows():
        #    for column in self.schedule_dict:
           #     self.schedule_dict[column] = [row[column]]


        sheet_names = []

        player_configurations =   player_time_weight_methods.copy()



        player_configurations['map_time_weight_rating']['column_names_equal_to']['map'] = ACTIVE_MAPS

        for series_id in series_ids:
            try:
                single_series_all_player = get_rows_where_column_equal_to(self.future_series_player,series_id,"series_id")
                format = single_series_all_player['format'].iloc[0]
                start_date_time =    single_series_all_player .head(1)['start_date_time'].iloc[0]
                current_day = datetime.datetime.today()
                days_in_the_future = (start_date_time - current_day).days


                team_ids = get_unique_values_from_column_in_list_format(single_series_all_player,"team_id")
                team_names = get_unique_values_from_column_in_list_format(single_series_all_player, "team_name")
                team_player_ids = get_team_player_dictionary(single_series_all_player, "team_id", "player_id")
                if len(team_player_ids[team_ids[0]]) != 5 or len(team_player_ids[team_ids[1]]) != 5:
                    continue
                player_id_to_player_name = self.get_player_ids_to_player_names(single_series_all_player)
                team_player_names = self.create_team_player_names(team_player_ids, player_id_to_player_name)
                sheet_name = str(team_names[0]) + '_' + str(team_names[1])

                reverse_sheet_name = str(team_names[1]) + '_' + str(team_names[0])

                if sheet_name not in existing_sheet_names and reverse_sheet_name in existing_sheet_names:
                    sheet_name = reverse_sheet_name

                sheet_names.append(sheet_name)


                SingleGame = SingleGameRatingGenerator(team_ids, team_player_ids, start_date_time,
                                                       self.all_game_all_player, self.all_player,
                                                       player_configurations, update_dataframe=False,
                                                       single_game_all_player=single_series_all_player)

                try:
                    SingleGame.calculcate_ratings()
                except IndexError:
                    print("Couldnt do series", team_names)
                    continue

                team_ratings = [
                    round(SingleGame.team_ratings[team_ids[0]], 0),
                    round(SingleGame.team_ratings[team_ids[1]], 0),
                ]

                team_default_ratings = [
                    round(SingleGame.team_default_ratings[team_ids[0]], 0),
                    round(SingleGame.team_default_ratings[team_ids[1]], 0),
                ]

                trueskill_team_players = self.get_trueskill_team_players(team_player_ids)
                trueskill_win_probability = get_trueskill_win_probability(trueskill_team_players[0],
                                                                          trueskill_team_players[1], beta=5)

                win_probabilities, map_probs_dict,pick_ban_probabilities = self.get_win_probability_regular_time(team_ratings,
                                                                                          trueskill_win_probability,
                                                                                          team_default_ratings,
                                                                                          team_player_ids,
                                                                                          SingleGame.single_game_stored_player_values,
                                                                                          team_names)


                rating_difference = (team_default_ratings[0] - team_default_ratings[1]) * 0.5 + (
                            team_ratings[0] - team_ratings[1]) * 0.5

                step = 0.03
                min_win_probability = win_probabilities['0_all']-step*2
                series_win_probabilities = {}

                for wr in range(5):
                    map_win_probability =round(min_win_probability  +wr *step,2)

                    series_win= SeriesWinProbability( map_win_probability, format, rating_difference)
                    series_win.generate_series_probability()
                    series_win_probabilities[map_win_probability] = series_win


                series_win_probability = series_win_probabilities[round(win_probabilities['0_all'],2)]



                team_certain_ratios = self.calculcate_team_certain_ratio(team_player_ids,
                                                                         SingleGame.single_game_stored_player_values)
                certain_ratio_avg_sq = self.generate_averaged_squared_team_certain_ratio(team_certain_ratios,
                                                                                         squared_factor=0.4)
                # mean_abs_errors = self.get_last_x_number_of_games_abs_error(team_player_ids)

                pred = self.uncertainty_model.predict([[certain_ratio_avg_sq]])[0]
                mean_pred = 1785
                difference = pred - mean_pred
                uncertain_ratio = round(1 / (1 + 10 ** (-difference / 18)), 4)
                map_probs_df = pd.DataFrame.from_dict(map_probs_dict)

                print(team_names, win_probabilities)

                historical_team_stats_dict= self.get_historical_team_stats_dict(  series_win_probability, team_ids,   team_names,   win_probabilities, team_player_ids)
                historical_team_stats_dict['Team Stats'].append("Match Uncertain")
                historical_team_stats_dict[team_names[0]].append(str(round(uncertain_ratio*100,0)) + "%")
                historical_team_stats_dict[team_names[1]].append("")
                historical_team_stats_df = pd.DataFrame.from_dict(historical_team_stats_dict)



                self.schedule_dict['Date'].append(start_date_time)
                self.schedule_dict['Team1'].append(team_names[0])
                self.schedule_dict['Team2'].append(team_names[1])
                self.schedule_dict['Win Probability1'].append(str(round(win_probabilities['0_all']*100,0)) + "%")
                self.schedule_dict['Win Probability2'].append(str(round(win_probabilities['1_all']*100,0)) + "%")
                self.schedule_dict['Series Win Probability1'].append(str(round(series_win_probability.series_win_probability * 100, 0)) + "%")
                self.schedule_dict['Series Win Probability2'].append(str(round((1-series_win_probability.series_win_probability)* 100, 0)) + "%")

                self.schedule_dict['Match Uncertain Ratio'].append(str(round(uncertain_ratio*100,0)) + "%")

                self.schedule_dict['Tournament'].append(single_series_all_player['tournament_name'].iloc[0])
                self.schedule_dict['Sheet Name'].append(sheet_name)

                avg_rating =  sum(team_ratings)/len(team_ratings)

                if sheet_name in existing_sheet_names and self.make_sheet_for_newest_series_only:
                    continue

                if days_in_the_future < MAXDAYCOUNTSHEET_HIGHTIER and avg_rating > 3000 or days_in_the_future <MAXDAYCOUNTSHEET_LOW_TIER  :

                    create_new_sheet_if_not_exist(sheet_name, self.workbook_name)
                    clear_sheet(sheet_name, self.workbook_name)
                    append_df_to_sheet(map_probs_df, sheet_name, workbook_name=self.workbook_name, row_number=21,
                                       column_number=1)
                    handicap_prob_df = self.generate_handicap_probabilities(series_win_probabilities,team_names)





                    append_df_to_sheet(handicap_prob_df,sheet_name,workbook_name=self.workbook_name,row_number=13,column_number=13)

                    leftover_prob = sum(pick_ban_probabilities) / len(pick_ban_probabilities)
                    if format =="bo3":
                        givenmap1_probs_df = self.add_prob_given_map1(team_names,leftover_prob,win_probabilities,format,rating_difference,pick_ban_probabilities)
                        append_df_to_sheet(givenmap1_probs_df,sheet_name,self.workbook_name,row_number=45,column_number=13)

                    if self.is_over_under_kill_series(start_date_time,team_ratings,single_series_all_player) is True:

                        expected_player_kill_percentages = \
                                self.calculcate_expected_player_kill_percentages(team_player_ids, player_id_to_player_name,
                                                                                 SingleGame)

                        KillsScenarioProbability = KillsScenarioProbabilityGenerator(team_player_names, team_ratings,
                                                                                     expected_player_kill_percentages,
                                                                                     win_probabilities)

                        scenario_df = KillsScenarioProbability.generate_round_probabilities()
                        over_under_variations_df = KillsScenarioProbability.create_over_under_variations(scenario_df)


                        #historical_over_df = create_average_over_under_df(self.all_game_all_player, team_player_ids,
                       #                                                   player_id_to_player_name, months_back=4,
                       #                                                   name='4M Stats')


                        estimated_team_kills = self.get_estimated_team_kills(scenario_df,team_ids)

                        map_kpr_df = self.create_map_kpr_df(player_id_to_player_name,team_player_ids, SingleGame.single_game_stored_player_values,
                                                            estimated_team_kills)


                        try:

                            #append_df_to_sheet(historical_over_df, sheet_name, self.workbook_name, row_number=19, column_number=1)
                            append_df_to_sheet(over_under_variations_df,sheet_name,self.workbook_name,row_number=4,column_number=1)
                            append_df_to_sheet(map_kpr_df, sheet_name, self.workbook_name, row_number=32, column_number=1)
                            pass
                        except Exception as e:
                            traceback.print_exc()

                    for team_number, team_id in enumerate(team_ids):
                        append_df_to_sheet(round(self.team_results[team_id],0), sheet_name=sheet_name,
                                           workbook_name=self.workbook_name, row_number=45 + team_number * 19)
                    append_df_to_sheet(historical_team_stats_df, sheet_name, self.workbook_name, row_number=1, column_number=13)
                    player_ratings_dict = {
                        'Players':['Rating']
                    }


                    for player_id in SingleGame.single_game_stored_player_values:
                        player_name = self.all_player[self.all_player['player_id']==player_id]['player_name'].iloc[0]
                        player_ratings_dict[player_name] = [round(SingleGame.single_game_stored_player_values[player_id]['time_weight_rating'],0)]
                    append_df_to_sheet(pd.DataFrame.from_dict(player_ratings_dict),sheet_name,workbook_name=self.workbook_name,row_number=1,column_number=1)
            except Exception as e:
                traceback.print_exc()


        delete_old_sheets(self.workbook_name,sheet_names)
        clear_sheet("Schedule",self.workbook_name)
        append_df_to_sheet(pd.DataFrame.from_dict(self.schedule_dict), "Schedule", self.workbook_name)


    def add_prob_given_map1(self,team_names,leftover_prob,win_probabilities,format,rating_difference,pick_ban_probabilities):
        givenmap1_probs = {
            'Map 1 pick': [],
            team_names[0] + " Map1": [],
            team_names[1] + " Map1": [],
            'Map 2 ' + str(team_names[0]): [],
            'Map 2 ' + str(team_names[1]): [],
            'Series ' + str(team_names[0]): [],
            'Series ' + str(team_names[1]): []
        }

        for round_difference in [-12, -7, -2, 2, 7, 12]:
            if round_difference > 0:
                rounds_won = 16
                rounds_lost = 16 - round_difference
            else:
                rounds_won = 16 + round_difference
                rounds_lost = 16

            for pick in [0, 1]:
                givenmap1_probs[team_names[0] + " Map1"].append(rounds_won)
                givenmap1_probs[team_names[1] + " Map1"].append(rounds_lost)

                sw_pick1 = SeriesWinProbability(win_probabilities['0_all'], format, rating_difference)
                sw_pick1.generate_bo_3_from_map1(round_difference, pick_ban_probabilities[pick],
                                                 pick_ban_probabilities[-pick + 1], leftover_prob,
                                                 self.ml_models_dict['won_stacked'])

                givenmap1_probs['Map 1 pick'].append(team_names[pick])

                if round_difference > 0:
                    map2_win_prob = sw_pick1.series_result_probability['2-0']


                elif round_difference < 0:
                    map2_win_prob = sw_pick1.series_result_probability['1-2'] + sw_pick1.series_result_probability[
                        '2-1']

                map2_prob_str = str(round(map2_win_prob * 100, 1)) + "%"
                map2_prob_team_2str = str(round((1 - map2_win_prob) * 100, 1)) + "%"

                givenmap1_probs['Map 2 ' + str(team_names[0])].append(map2_prob_str)
                givenmap1_probs['Map 2 ' + str(team_names[1])].append(map2_prob_team_2str)

                series_win_prob = sw_pick1.series_result_probability['2-0'] + sw_pick1.series_result_probability['2-1']
                series_win_prob_str = str(round((series_win_prob) * 100, 1)) + "%"
                series_win_prob_team2_str = str(round((1 - series_win_prob) * 100, 1)) + "%"
                givenmap1_probs['Series ' + str(team_names[0])].append(series_win_prob_str)
                givenmap1_probs['Series ' + str(team_names[1])].append(series_win_prob_team2_str)

        givenmap1_probs_df = pd.DataFrame.from_dict(givenmap1_probs)
        return givenmap1_probs_df



    def get_estimated_team_kills(self,scenario_df,team_ids):
        estimated_team_kills = []
        for team_id in team_ids:
            team_rows = scenario_df[scenario_df['team_name']==team_id]

            estimated_team_kill =round((team_rows['player_kills']*team_rows['scenario_probability']).sum(),1)
            estimated_team_kills.append(estimated_team_kill)

        return estimated_team_kills



    def generate_handicap_probabilities(self,series_win_probabilities,team_names):

        hc_column_name = 'Handicap ' + str(team_names[0])

        handicap_probabilities_dict = {
            hc_column_name:[],
        }
        number = -1
        for map_win_probability,series_win_probability in series_win_probabilities.items():
            number +=1


            handicap_probabilities_dict[str(map_win_probability)] = []

            sorted_list = sorted(series_win_probability.round_win_probsmap1,reverse=False)
            sum_prob = 0
            for round_difference in sorted_list:

                prob = series_win_probability.round_win_probsmap1[round_difference]

                handicap = str(-round_difference+0.5)
                if float(handicap) > 0:
                    handicap = "+" + handicap
                if round_difference > -16:
                    if number == 0:
                        handicap_probabilities_dict[hc_column_name].append(handicap)

                    handicap_probabilities_dict[str(map_win_probability)].append(str(round((1-sum_prob)*100,1)) + "%")


                sum_prob += prob
        try:
            df =  pd.DataFrame.from_dict(handicap_probabilities_dict)
        except:
            h = 3
        return df

    def create_map_kpr_df(self,player_id_to_player_name,team_players,single_game_stored_player_values,estimated_team_kills):

        map_kpr_dict = {
            'Estimated KPR Maps':[]
        }


        maps = ['mirage','inferno','dust2','nuke','overpass','vertigo','train']
        for map in maps:
            map_kpr_dict['Estimated KPR Maps'].append(map)

        for team_number,team in enumerate(team_players):
            for map in maps:
                team_sum_estimated_map_kpr = 0
                raw_estimated_map_kprs = {}
                for player_id in team_players[team]:
                    player_name = player_id_to_player_name[player_id]
                    if player_name not in map_kpr_dict:
                        map_kpr_dict[player_name] = []

                    column_name = 'map_time_weighted_opponent_adjusted_kpr_' + map
                    raw_estimated_map_kprs[player_id] = single_game_stored_player_values[player_id][column_name]
                    team_sum_estimated_map_kpr +=   raw_estimated_map_kprs[player_id]


                for player_id in team_players[team]:
                    player_name = player_id_to_player_name[player_id]
                    estimated_kill_percentage =    raw_estimated_map_kprs[player_id] /   team_sum_estimated_map_kpr
                    estimated_map_kpr = round(estimated_kill_percentage*estimated_team_kills[team_number],1)
                    map_kpr_dict[player_name].append(estimated_map_kpr)



        return pd.DataFrame.from_dict(map_kpr_dict)



    def get_historical_team_stats_dict(self,series_win_probability,team_ids,team_names,win_probabilities,team_players):
        min_date_4_months = datetime.datetime.now() - datetime.timedelta(4 * 365 / 12)
        filtered_game_all_team_4_months = self.all_game_all_team[self.all_game_all_team['start_date_time'] > min_date_4_months]
        filtered_game_all_player_4_months = self.all_game_all_player[self.all_game_all_player['start_date_time'] > min_date_4_months]
        self.all_game_all_team['games_played'] = self.all_game_all_team.groupby(['team_name']).cumcount() + 1
        self.all_game_all_player['games_played'] = self.all_game_all_player.groupby(['player_id']).cumcount() + 1


        filtered_game_all_player_12_games =   self.all_game_all_player[  self.all_game_all_player['games_played']<12]
        win_rates_4_month =[]
        average_kills_4_month = []

        performance_rating_4_month = []
        last_15_games_performance_rating = []
        average_performance_rating_recents = []
        recent_game_counts = []
        self.team_results = {}

        for number,team_id in enumerate(team_ids):

            filtered_team_20_games = self.all_game_all_team[(self.all_game_all_team['games_played']<18)&(self.all_game_all_team['team_name']==team_names[number])]

            self.team_results[team_id] = filtered_team_20_games[['start_date_time','team_name','team_name_opponent','time_weight_rating','opponent_time_weight_rating',
                                                                 'rounds_won','rounds_lost','won','opponent_adjusted_performance_rating']].sort_values(by=['start_date_time'],ascending=False)

            self.team_results[team_id] = self.team_results[team_id].rename(columns={'time_weight_rating':'rating','opponent_time_weight_rating':'opponent_rating','opponent_adjusted_performance_rating':'match_rating'})



            filtered_game_single_team_4_months =filtered_game_all_team_4_months[filtered_game_all_team_4_months['team_name']==team_names[number]].sort_values(by=['start_date_time','game_number'],ascending=False)

            win_rates_4_month.append(round(filtered_game_single_team_4_months['won'].mean(),2))
            average_kills_4_month.append(round(filtered_game_single_team_4_months['kills'].mean(),1))



            average_performance_rating_4_months = self.get_average_team_performance(filtered_game_all_player_4_months,team_players[team_id],"opponent_adjusted_performance_rating")
            average_performance_rating_12_games = self.get_average_team_performance(filtered_game_all_player_12_games,
                                                                                    team_players[team_id],
                                                                                    "opponent_adjusted_performance_rating")

            average_performance_rating_recent,average_days_ago = self.get_average_team_performance_recent(
                datetime.datetime.now(),
            self.all_game_all_player,
                team_players[team_id],
           "opponent_adjusted_performance_rating"
            )
            recent_game_counts.append(average_days_ago)
            average_performance_rating_recents.append(average_performance_rating_recent)


            performance_rating_4_month.append(round(average_performance_rating_4_months,0))

            last_15_games_performance_rating.append(round(average_performance_rating_12_games,0))


        win_rate_dict = {
            'Team Stats': ["Series Win Probability","Map Win Probability", "4 Month Win Rate", "4 Month Performance Rating", "12 Games Performance Rating","Recent Days Ago"],
            team_names[0]: [round(series_win_probability.series_win_probability,3),win_probabilities['0_all'], win_rates_4_month[0],
                            performance_rating_4_month[0],last_15_games_performance_rating[0],
                            recent_game_counts[0]],
            team_names[1]: [round(1-series_win_probability.series_win_probability,3),win_probabilities['1_all'], win_rates_4_month[1],
                            performance_rating_4_month[1],last_15_games_performance_rating[1],recent_game_counts[1]],

        }
        if '2-0' in series_win_probability.series_result_probability:
            win_rate_dict['Team Stats'].append("2-0")
            win_rate_dict['Team Stats'].append("2-1")
            win_rate_dict[team_names[0]].append(str(round(series_win_probability.series_result_probability['2-0'] * 100, 1)) + "%")
            win_rate_dict[team_names[0]].append(str(round(series_win_probability.series_result_probability['2-1'] * 100, 1)) + "%")
            win_rate_dict[team_names[1]].append(str(round(series_win_probability.series_result_probability['0-2'] * 100, 1)) + "%")
            win_rate_dict[team_names[1]].append(str(round(series_win_probability.series_result_probability['1-2'] * 100, 1)) + "%")


        return  win_rate_dict


    def get_average_team_performance_recent(self,current_date,df,players,column_name,days_ago_threshold=25,min_game_count=10,max_days_ago=120):
        team_means = []
        sum_date_count = 0
        for player_id in players:
            player_rows= df[df['player_id']==player_id]
            player_performance_ratings = []
            days_ago = 0
            for index,row in player_rows.iterrows():
                days_ago = (current_date-row['start_date_time']).days

                if days_ago > days_ago_threshold and row['games_played'] > min_game_count  or days_ago > max_days_ago:
                    break
                else:
                    player_performance_ratings.append(row[column_name])

            if len(player_performance_ratings) > 0:
                average_player_performance = sum(player_performance_ratings)/len(player_performance_ratings)
                team_means.append(average_player_performance)

            sum_date_count+=days_ago
        if len(team_means) ==0:
           return None,None
        else:
            average_team_mean = sum(team_means)/len(team_means)

        return int(round(average_team_mean,0)),int(round(sum_date_count/5,0))

    def get_average_team_performance(self,df,players,column_name):
        sum_team_mean = 0
        for player_id in players:
            mean= df[df['player_id']==player_id][column_name].mean()
            sum_team_mean+=mean

        return sum_team_mean/5

    def is_over_under_kill_series(self,start_date_time,team_ratings,single_series_all_player):
        max_days_in_future_player_kills = 7
        min_average_rating_player_kills = 2400
        prize_pool = single_series_all_player['prize_pool'].iloc[0]
        is_offline = single_series_all_player['is_offline'].iloc[0]
        tournament_name = single_series_all_player['is_offline'].iloc[0]
        current_day = datetime.datetime.today()
        days_in_the_future = (start_date_time - current_day).days
        if days_in_the_future <= max_days_in_future_player_kills or tournament_name in covered_tournaments:
            if sum(team_ratings) / len(
                team_ratings) > min_average_rating_player_kills  or prize_pool >=100000:
                    return True
        return False

    def calculcate_expected_player_kill_percentages(self,team_player_ids,player_id_to_player_name,SingleGame):
        expected_player_kill_percentages = {}
        expected_player_kill_map_percentages = {}
        for team_id,player_ids in team_player_ids.items():
            team_estimated_kprs = []
            team_estimated_map_kprs = []
            raw_estimated_kprs = []
            adjustment_bonus = []
            player_names = []
            for player_id in player_ids:
                adjustment_bonus.append(SingleGame.single_game_stored_player_values[player_id]['time_weighted_opponent_adjusted_kpr']-
                                        SingleGame.single_game_stored_player_values[player_id]['time_weighted_kpr'])
                raw_estimated_kprs.append(SingleGame.single_game_stored_player_values[player_id]['time_weighted_opponent_adjusted_kpr'])

            average_adjustment_bonus = sum(adjustment_bonus)/len(adjustment_bonus)

            for player_number,player_id in enumerate(player_ids):

                estimated_kpr = raw_estimated_kprs[player_number]-average_adjustment_bonus
                team_estimated_kprs.append(estimated_kpr)
                team_estimated_map_kprs.append(estimated_kpr)
                player_name = player_id_to_player_name[player_id]
                player_names.append(player_name)

            for player_number,player_name in enumerate(player_names):
                estimated_kill_percentage = team_estimated_kprs[player_number]/sum(team_estimated_kprs)
                expected_player_kill_percentages[player_name] = estimated_kill_percentage
                expected_player_kill_map_percentages[player_name] = team_estimated_map_kprs[player_number]/sum(team_estimated_map_kprs)

        return expected_player_kill_percentages


    def create_team_player_names(self,team_player_ids,player_id_to_player_name):
        team_player_names = {}
        for team in team_player_ids:
            team_player_names[team] = []
            for player_id in team_player_ids[team]:
                player_name = player_id_to_player_name[player_id]
                team_player_names[team].append(player_name)

        return team_player_names


    def get_player_ids_to_player_names(self,single_series_all_player):
        player_id_to_player_name = {}
        for index,row in single_series_all_player.iterrows():
            player_id = row['player_id']
            try:
                player_name = self.all_player[self.all_player['player_id']==player_id]['player_name'].iloc[0]
            except:
                player_name =None

            player_id_to_player_name[player_id] = player_name

        return player_id_to_player_name

    def get_win_probability_regular_time(self,team_ratings,trueskill_win_probability,team_default_ratings,team_player_ids,single_game_stored_player_values,team_names):
        win_probabilities = {}

        rating_difference = team_ratings[0]- team_ratings[1]
        default_rating_difference = team_default_ratings[0] - team_default_ratings[1]

        all_model = self.ml_models_dict['won']
       # regular_model = self.ml_models_dict['won_regular']
       # feature_dict = {'rating_difference':rating_difference}
       # X =self.convert_feature_dict_to_df(feature_dict)
        #probs = regular_model.predict_proba(X)
        #win_probabilities['ot'] = probs[0][1]
       # win_probabilities['0_time'] = round(all_model.predict_proba(X)[0][1],3)
       # win_probabilities['1_time'] = round(all_model.predict_proba(X)[0][0],3)

        X = self.convert_feature_dict_to_df({
            'rating_difference':rating_difference,
            'default_rating_difference':default_rating_difference,
           # 'trueskill_win_probability':trueskill_win_probability
        })
        # probs = regular_model.predict_proba(X)
        # win_probabilities['ot'] = probs[0][1]
        win_probabilities['0_all'] = round(self.ml_models_dict['won_stacked'].predict_proba(X)[0][1], 3)
        win_probabilities['1_all'] = round(self.ml_models_dict['won_stacked'].predict_proba(X)[0][0], 3)

        map_probs_dict = {
            'Win Probability':ACTIVE_MAPS,
            team_names[0]:[],
            team_names[1]:[],
            team_names[0]+ ' Picked':[],
            team_names[1] + ' Picked': [],
            team_names[0] + ' Leftover': [],
            team_names[1] + ' Leftover': [],
        }
        map_prob_pickeds = []
        map_prob_opp_pickeds = []
        for map in ACTIVE_MAPS:
            team_ratings = {}
            number = -1
            for team,player_ids in team_player_ids.items():
                number+=1
                player_ratings = []
                for player_id in player_ids:
                    column_name = 'map_time_weight_rating_'+map.lower()
                    rating = single_game_stored_player_values[player_id][column_name]
                    player_ratings.append(rating)

                team_ratings[number] = sum(player_ratings)/len(player_ratings)

            map_rating_difference = team_ratings[0]-team_ratings[1]
            map_prob = self.ml_models_dict['won_map_stacked'].predict_proba([[rating_difference,default_rating_difference,map_rating_difference]])[0][1]

            map_prob_picked = self.ml_models_dict['won_pick_map_stacked'].predict_proba(
                [[rating_difference, default_rating_difference,trueskill_win_probability, map_rating_difference,2]])[0][1]

            map_prob_opp_picked = self.ml_models_dict['won_pick_map_stacked'].predict_proba(
                [[rating_difference, default_rating_difference,trueskill_win_probability, map_rating_difference,0]])[0][1]

            map_prob_pickeds.append(map_prob_picked)
            map_prob_opp_pickeds.append(map_prob_opp_picked)


            map_prob_leftover = self.ml_models_dict['won_pick_map_stacked'].predict_proba(
                [[rating_difference, default_rating_difference,trueskill_win_probability, map_rating_difference,1]])[0][1]

            map_prob_str0 = str(int(round(map_prob*100,0) )) + "%"
            map_prob_str1 = str(int(round((1-map_prob) * 100, 0))) + "%"
            map_probs_dict[team_names[0]].append(map_prob_str0)
            map_probs_dict[team_names[1]].append(map_prob_str1)

            map_prob_picked_str0 = str(int(round(map_prob_picked * 100, 0))) + "%"
            map_prob_picked_str1 = str(int(round((1- map_prob_opp_picked) * 100, 0))) + "%"
            map_prob_picked_str0left = str(int(round(( map_prob_leftover) * 100, 0))) + "%"
            map_prob_picked_str1left = str(int(round((1-map_prob_leftover) * 100, 0))) + "%"


            map_probs_dict[team_names[0] + ' Picked'].append(map_prob_picked_str0)
            map_probs_dict[team_names[1] + ' Picked'].append(map_prob_picked_str1)
            map_probs_dict[team_names[0] +' Leftover'].append(map_prob_picked_str0left)
            map_probs_dict[team_names[1] + ' Leftover'].append(map_prob_picked_str1left)


        map_picks = [sum(map_prob_pickeds)/len(map_prob_pickeds),sum(map_prob_opp_pickeds)/len(map_prob_opp_pickeds)]

        return win_probabilities,map_probs_dict,map_picks


    def convert_feature_dict_to_df(self,feature_dict):
        X_dict = {}
        for column,value in feature_dict.items():
            X_dict[column] = [value]


        X = pd.DataFrame.from_dict(X_dict)

        return X



if __name__ == '__main__':
    SeriesPrediction = SeriesPredictionGenerator(calculcate_win_probabilities=True,
                                                 make_sheet_for_newest_series_only=False)
    SeriesPrediction.load_data()
    SeriesPrediction.main()