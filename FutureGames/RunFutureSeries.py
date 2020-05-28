from settings import *
from SQL import *
import datetime

from Functions.Lists import *
from Ratings.SingleGame import SingleGameRatingGenerator

from Predictions.ScenarioProbabilities import KillsScenarioProbabilityGenerator
from Functions.GoogleSheets import *
from Functions.AverageValues import create_average_over_under_df
from TimeWeight.timeweightconfigurations import player_time_weight_methods
from Functions.Miscellaneous import scale_features_and_insert_to_dataframe

ot_default_probability = 0.093

covered_tournaments = ['ESL Pro League Season 11 North America']

class SeriesPredictionGenerator():

    def __init__(self,calculcate_win_probabilities=True,calculcate_kill_probabilities=True):
        self.calculcate_win_probabilities = calculcate_win_probabilities
        self.calculcate_kill_probabilities = calculcate_kill_probabilities

        self.player_ratings = {}
        self.ml_models_dict = {
            "won_regular": pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\own_won_csgo_regular"),
            "won_regular_scaled": pd.read_pickle(
                r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\own_won_csgo_regular_scaled"),
            "won": pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\own_won_csgo_all"),
            "won_scaled": pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\own_won_csgo_all_scaled"),

        }
        self.workbook_name = "CSGO"
        self.schedule_dict = {
            'Date':[],
            'Tournament':[],
            'Team1':[],
            'Team2':[],
            'Win Probability1':[],
            'Win Probability2':[],
            'Rating1':[],
            'Rating2':[],
        }
        pass

    def load_data(self):
        self.all_game_all_team = pd.read_pickle(
            local_file_path + "//all_game_all_team_rating").sort_values(by='start_date_time',
                                                                                      ascending=False)
        self. all_game_all_player = pd.read_pickle(local_file_path+"//all_game_all_player_rating").sort_values(by='start_date_time',ascending=False)
        self.all_game_all_player = self.all_game_all_player[self.all_game_all_player['opponent_region'].notna()]


        self.all_player = pd.read_pickle(local_file_path + "//all_player")
        self.all_team = pd.read_pickle(local_file_path + "//all_team")
        min_date =datetime.datetime.now()- datetime.timedelta(0.2)
        pre_series_player = get_all_from_series_player(min_date).sort_values(by='start_date_time',ascending=True)
        historical_series_ids =  self.all_game_all_player ['series_id'].unique().tolist()
        self.future_series_player = pre_series_player[~pre_series_player.series_id.isin(        historical_series_ids)]




    def main(self):

        series_ids = self.future_series_player['series_id'].unique().tolist()

        schedule_df = read_google_sheet("Schedule",self.workbook_name)
        sheet_names = []
        for series_id in series_ids:

            single_series_all_player = get_rows_where_column_equal_to(self.future_series_player,series_id,"series_id")
            start_date_time =    single_series_all_player .head(1)['start_date_time'].iloc[0]
            current_day = datetime.datetime.today()
            days_in_the_future = (start_date_time - current_day).days
            if days_in_the_future > 6:
                break

            team_ids = get_unique_values_from_column_in_list_format(single_series_all_player,"team_id")
            team_names = get_unique_values_from_column_in_list_format(single_series_all_player, "team_name")
            team_player_ids = get_team_player_dictionary(single_series_all_player, "team_id", "player_id")
            player_id_to_player_name = self.get_player_ids_to_player_names(single_series_all_player)
            team_player_names = self.create_team_player_names(team_player_ids, player_id_to_player_name)
            sheet_name = str(team_names[0]) + '_' + str(team_names[1])
            sheet_names.append(sheet_name)



            single_series_schedule_row = schedule_df[(schedule_df['Team1'] == team_names[0])
                                                     & (schedule_df['Team2'] == team_names[1])
                                                     ]

            if   self.calculcate_win_probabilities is True or len(single_series_schedule_row)==0:
                time_weight_configurations ={
                    'time_weight_default_rating':player_time_weight_methods['time_weight_default_rating'],
                    'time_weight_rating':player_time_weight_methods['time_weight_rating'],
                    'time_weighted_default_opponent_adjusted_kpr':player_time_weight_methods['time_weighted_default_opponent_adjusted_kpr'],
                    'time_weighted_opponent_adjusted_kpr':player_time_weight_methods['time_weighted_opponent_adjusted_kpr'],
                    'map_time_weighted_opponent_adjusted_kpr': player_time_weight_methods[
                        'map_time_weighted_opponent_adjusted_kpr'],

                }
                SingleGame = SingleGameRatingGenerator(team_ids, team_player_ids, start_date_time, self.all_game_all_player,self.all_player,
                                                       time_weight_configurations,update_dataframe=False, single_game_all_player=single_series_all_player)

                try:
                    SingleGame.calculcate_ratings()
                except IndexError:
                    print("Couldnt do series", team_names)
                    continue

                team_ratings = [
                    round(SingleGame.team_ratings[team_ids[0]],0),
                    round(SingleGame.team_ratings[team_ids[1]],0),
                ]
                win_probabilities = self.get_win_probability_regular_time(team_ratings)


            elif self.calculcate_win_probabilities is False:
                time_weight_configurations = {
                    'time_weighted_default_opponent_adjusted_kpr': player_time_weight_methods[
                        'time_weighted_default_opponent_adjusted_kpr'],
                    'time_weighted_opponent_adjusted_kpr':player_time_weight_methods['time_weighted_opponent_adjusted_kpr'],

                }
                SingleGame = SingleGameRatingGenerator(team_ids, team_player_ids, start_date_time,
                                                       self.all_game_all_player, self.all_player,
                                                       time_weight_configurations, update_dataframe=False,
                                                       single_game_all_player=single_series_all_player)

                SingleGame.calculcate_ratings()

                team_ratings = [
                    float(single_series_schedule_row['Rating1'].iloc[0]),
                    float(single_series_schedule_row['Rating2'].iloc[0]),
                ]

                win_probabilities = self.get_win_probability_regular_time(team_ratings)

            print(sheet_name, win_probabilities)
            self.schedule_dict['Date'].append(start_date_time)
            self.schedule_dict['Team1'].append(team_names[0])
            self.schedule_dict['Team2'].append(team_names[1])
            self.schedule_dict['Win Probability1'].append(str(round(win_probabilities['0_all']*100,0)) + "%")
            self.schedule_dict['Win Probability2'].append(str(round(win_probabilities['1_all']*100,0)) + "%")
            self.schedule_dict['Rating1'].append(team_ratings[0])
            self.schedule_dict['Rating2'].append(team_ratings[1])
            self.schedule_dict['Tournament'].append(single_series_all_player['tournament_name'].iloc[0])



            if self.is_over_under_kill_series(start_date_time,team_ratings,single_series_all_player) is True:

                expected_player_kill_percentages = \
                        self.calculcate_expected_player_kill_percentages(team_player_ids, player_id_to_player_name,
                                                                         SingleGame)

                KillsScenarioProbability = KillsScenarioProbabilityGenerator(team_player_names, team_ratings,
                                                                             expected_player_kill_percentages,
                                                                             win_probabilities)

                scenario_df = KillsScenarioProbability.generate_round_probabilities()
                over_under_variations_df = KillsScenarioProbability.create_over_under_variations(scenario_df)


                historical_over_df = create_average_over_under_df(self.all_game_all_player, team_player_ids,
                                                                  player_id_to_player_name, months_back=4,
                                                                  name='4M Stats')
                win_rate_df,estimated_team_kills =self.get_historical_team_stats_df_and_estimated_team_kills(scenario_df,team_ids,team_names,win_probabilities)
                map_kpr_df = self.create_map_kpr_df(player_id_to_player_name,team_player_ids, SingleGame.single_game_stored_player_values,
                                                    estimated_team_kills)

                try:
                    clear_sheet(sheet_name, self.workbook_name)
                except Exception:
                    pass





                create_new_sheet_if_not_exist(sheet_name, self.workbook_name)

                try:
                    append_df_to_sheet(win_rate_df,sheet_name,self.workbook_name,row_number=1,column_number=13)

                    append_df_to_sheet(historical_over_df, sheet_name, self.workbook_name, row_number=19, column_number=1)
                    append_df_to_sheet(over_under_variations_df,sheet_name,self.workbook_name)
                    append_df_to_sheet(map_kpr_df, sheet_name, self.workbook_name, row_number=32, column_number=1)
                except Exception as e:
                    print(e)

        delete_old_sheets(self.workbook_name,sheet_names)
        clear_sheet("Schedule",self.workbook_name)
        append_df_to_sheet(pd.DataFrame.from_dict(self.schedule_dict), "Schedule", self.workbook_name)


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



    def get_historical_team_stats_df_and_estimated_team_kills(self,scenario_df,team_ids,team_names,win_probabilities):
        min_date = datetime.datetime.now() - datetime.timedelta(4 * 365 / 12)
        filtered_game_all_team = self.all_game_all_team[self.all_game_all_team['start_date_time'] > min_date]
        win_rates_4_month =[]
        average_kills_4_month = []
        estimated_team_kills = []
        for number,team_id in enumerate(team_ids):

            filtered_game_single_team =filtered_game_all_team[filtered_game_all_team['team_id']==team_id]
            win_rates_4_month.append(round(filtered_game_single_team['won'].mean(),2))
            average_kills_4_month.append(round(filtered_game_single_team['kills'].mean(),1))
            team_rows =  scenario_df[scenario_df['team_name']==team_id]
            estimated_team_kill =round((team_rows['player_kills']*team_rows['scenario_probability']).sum(),1)
            estimated_team_kills.append(estimated_team_kill)


        win_rate_dict = {
            'Team Stats': ["Win Probability", "4 Month Win Rate","Average 4 Months Kills", "Estimated Kills"],
            team_names[0]: [win_probabilities['0_all'], win_rates_4_month[0],average_kills_4_month[0],estimated_team_kills[0]],
            team_names[1]: [win_probabilities['1_all'], win_rates_4_month[1],average_kills_4_month[1],estimated_team_kills[1]],

        }
        return  pd.DataFrame.from_dict(win_rate_dict),estimated_team_kills

    def is_over_under_kill_series(self,start_date_time,team_ratings,single_series_all_player):
        max_days_in_future_player_kills = 5
        min_average_rating_player_kills = 2100
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
            player_names = []
            for player_id in player_ids:
                estimated_kpr = SingleGame.single_game_stored_player_values[player_id]['time_weighted_opponent_adjusted_kpr']

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

    def get_win_probability_regular_time(self,team_ratings):
        win_probabilities = {}
       # team_ratings[0] = 0
       # team_ratings[1] = 0
        rating_difference = team_ratings[0]- team_ratings[1]

        #regular_model = self.ml_models_dict['won_regular']
        #scaled_data_regular = self.ml_models_dict['won_regular_scaled']
        #scaled_df = scale_features_and_insert_to_dataframe(scaled_data_regular, {'rating_difference':rating_difference})
        #win_probability_regular = regular_model.predict_proba(scaled_df)[0][1]
        win_probabilities['ot'] = ot_default_probability
        #win_regular = 1-win_probabilities['ot']
       # other_win_probability =  round(win_regular/(win_regular+10**(-rating_difference/4000)),3)
        #win_probabilities[0] = win_probability_regular
        #win_probabilities[1] = win_regular-      win_probabilities[0]

        all_model = self.ml_models_dict['won']
        scaled_data_all= self.ml_models_dict['won_scaled']
        scaled_df = scale_features_and_insert_to_dataframe(scaled_data_all,
                                                           {'rating_difference': rating_difference})
        win_probability_all = round(all_model.predict_proba(scaled_df)[0][1],3)
        win_probabilities['0_all'] = win_probability_all
        win_probabilities['1_all'] = 1-win_probability_all




        return win_probabilities



if __name__ == '__main__':
    SeriesPrediction = SeriesPredictionGenerator(calculcate_win_probabilities=True)
    SeriesPrediction.load_data()
    SeriesPrediction.main()