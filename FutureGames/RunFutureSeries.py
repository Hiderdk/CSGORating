from settings import *
from SQL import *
import datetime
from Functions.Filters import *
from Functions.SingleValue import *
from Functions.Lists import *
from Ratings.SingleGame import SingleGameRatingGenerator
from Ratings.Main import AllGamesGenerator
from Killsprobabilities.ScenarioProbabilities import KillsScenarioProbabilityGenerator
from Functions.GoogleSheets import *
from Functions.AverageValues import create_average_over_under_df

class SeriesPredictionGenerator():

    def __init__(self):
        self.player_ratings = {}

        self.workbook_name = "CSGO_Kills"
        self.schedule_dict = {
            'Date':[],
            'Team1':[],
            'Team2':[],
            'Win Probability1':[],
            'Win Probability2':[],
        }
        pass

    def load_data(self):
        self.all_game_all_team = pd.read_pickle(
            local_file_path + "//all_game_all_team").sort_values(by='start_date_time',
                                                                                      ascending=False)
        self. all_game_all_player = pd.read_pickle(local_file_path+"//all_game_all_player_rating").sort_values(by='start_date_time',ascending=False)

        self.all_player = pd.read_pickle(local_file_path + "//all_player")
        self.all_team = pd.read_pickle(local_file_path + "//all_team")
        min_date =self.all_game_all_player.head(1)['start_date_time'].iloc[0]
        pre_series_player = get_all_from_series_player(min_date)
        historical_series_ids =  self.all_game_all_player ['series_id'].unique().tolist()
        self.future_series_player = pre_series_player[~pre_series_player.series_id.isin(        historical_series_ids)]




    def main(self):

        series_ids = self.future_series_player['series_id'].unique().tolist()
        for series_id in series_ids:

            single_series_all_player = get_rows_where_column_equal_to(self.future_series_player,series_id,"series_id")
            start_date_time =    single_series_all_player .head(1)['start_date_time'].iloc[0]

            team_ids = get_unique_values_from_column_in_list_format(single_series_all_player,"team_id")
            team_names = get_unique_values_from_column_in_list_format(single_series_all_player, "team_name")
            team_player_ids = get_team_player_dictionary(single_series_all_player, "team_id", "player_id")
            SingleGame = SingleGameRatingGenerator(team_ids, team_player_ids, start_date_time, self.all_game_all_player,self.all_player,
                                                   update_dataframe=False, single_game_all_player=single_series_all_player)

            SingleGame.calculcate_ratings()
            player_id_to_player_name = self.get_player_ids_to_player_names(single_series_all_player)
            team_player_names = self.create_team_player_names(team_player_ids,player_id_to_player_name)

            team_ratings = [
                SingleGame.team_ratings[team_ids[0]],
                SingleGame.team_ratings[team_ids[1]],
            ]


            win_probabilities = self.get_win_probability_regular_time(SingleGame,team_ids)


            self.schedule_dict['Date'].append(start_date_time)
            self.schedule_dict['Team1'].append(team_names[0])
            self.schedule_dict['Team2'].append(team_names[1])
            self.schedule_dict['Win Probability1'].append(str(round(win_probabilities[0]*100,0)) + "%")
            self.schedule_dict['Win Probability2'].append(str(round(win_probabilities[1]*100,0)) + "%")

            if self.is_over_under_kill_series(start_date_time,team_ratings,single_series_all_player) is True:

                expected_player_kill_percentages = \
                        self.calculcate_expected_player_kill_percentages(team_player_ids, player_id_to_player_name,
                                                                         SingleGame)

                KillsScenarioProbability = KillsScenarioProbabilityGenerator(team_player_names, team_ratings,
                                                                             expected_player_kill_percentages,
                                                                             win_probabilities)
                scenario_df = KillsScenarioProbability.generate_round_probabilities()
                over_under_variations_df = KillsScenarioProbability.create_over_under_variations(scenario_df)
                sheet_name = str(team_names[0]) +'_' + str(team_names[1])
                create_new_sheet_if_not_exist(sheet_name,self.workbook_name)

                win_rate_df =self.get_historical_team_stats_df(team_ids,team_names,win_probabilities)
                append_df_to_sheet(win_rate_df,sheet_name,self.workbook_name,row_number=1,column_number=12)
                historical_over_df = create_average_over_under_df(self.all_game_all_player, team_player_ids,
                                                                  player_id_to_player_name,months_back=3,
                                                                  name='3M Stats')
                append_df_to_sheet(historical_over_df, sheet_name, self.workbook_name, row_number=16, column_number=1)

                append_df_to_sheet(over_under_variations_df,sheet_name,self.workbook_name)

        clear_sheet("Schedule",self.workbook_name)
        append_df_to_sheet(self.schedule_dict, "Schedule", self.workbook_name)

    def get_historical_team_stats_df(self,team_ids,team_names,win_probabilities):
        min_date = datetime.datetime.now() - datetime.timedelta(3 * 365 / 12)
        filtered_game_all_team = self.all_game_all_team[self.all_game_all_team['start_date_time'] > min_date]
        win_rates_3_month =[]
        for team_id in team_ids:
            filtered_game_single_team =filtered_game_all_team[filtered_game_all_team['team_id']==team_id]
            win_rates_3_month.append(filtered_game_single_team['won'].mean())

        win_rate_dict = {
            'Team Stats': ["Win Probability", "3 Month Win Rate"],
            team_names[0]: [win_probabilities[0], win_rates_3_month[0]],
            team_names[1]: [win_probabilities[1], win_rates_3_month[1]],
            'ot': [win_probabilities['ot'], ""]

        }
        return  pd.DataFrame.from_dict(win_rate_dict)

    def is_over_under_kill_series(self,start_date_time,team_ratings,single_series_all_player):
        max_days_in_future_player_kills = 5
        min_average_rating_player_kills = 1300
        prize_pool = single_series_all_player['prize_pool'].iloc[0]
        is_offline = single_series_all_player['is_offline'].iloc[0]
        current_day = datetime.datetime.today()
        days_in_the_future = (start_date_time - current_day).days
        if days_in_the_future <= max_days_in_future_player_kills:
            if sum(team_ratings) / len(
                team_ratings) > min_average_rating_player_kills  or prize_pool >=100000:
                    return True
        return False

    def calculcate_expected_player_kill_percentages(self,team_player_ids,player_id_to_player_name,SingleGame):
        expected_player_kill_percentages = {}
        for team_id,player_ids in team_player_ids.items():
            team_estimated_kprs = []
            player_names = []
            for player_id in player_ids:
                estimated_kpr = SingleGame.single_game_stored_player_values[player_id]['time_weighted_opponent_adjusted_kpr']
                team_estimated_kprs.append(estimated_kpr)
                player_name = player_id_to_player_name[player_id]
                player_names.append(player_name)

            for player_number,player_name in enumerate(player_names):
                estimated_kill_percentage = team_estimated_kprs[player_number]/sum(team_estimated_kprs)
                expected_player_kill_percentages[player_name] = estimated_kill_percentage

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
            player_name = self.all_player[self.all_player['player_id']==player_id]['player_name'].iloc[0]

            player_id_to_player_name[player_id] = player_name

        return player_id_to_player_name

    def get_win_probability_regular_time(self,SingleGame,team_ids):
        win_probabilities = {}
        rating_difference = SingleGame.team_ratings[team_ids[0]]- SingleGame.team_ratings[team_ids[1]]
        win_probabilities['ot'] = 0.07
        win_probabilities[0] = round(0.93/(0.93+10**(-rating_difference/3000)),3)
        win_probabilities[1] = 0.93-      win_probabilities[0]

        return win_probabilities




if __name__ == '__main__':
    SeriesPrediction = SeriesPredictionGenerator()
    SeriesPrediction.load_data()
    SeriesPrediction.main()