from settings import *
from SQL import *
from Functions.Filters import *
from Functions.SingleValue import *
from Functions.Lists import *
from Ratings.SingleGame import SingleGameRatingGenerator
from Ratings.Main import AllGamesGenerator
from Killsprobabilities.ScenarioProbabilities import KillsScenarioProbabilityGenerator
from Functions.GoogleSheets import *

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

        self. all_game_all_player = pd.read_pickle(local_file_path+"//all_game_all_player_performance_rating_old").sort_values(by='start_date_time',ascending=False)
        self.all_player = pd.read_pickle(local_file_path + "//all_player")
        min_date =self.all_game_all_player.head(1)['start_date_time'].iloc[0]
        pre_series_player = get_all_from_series_player(min_date)
        historical_series_ids =  self.all_game_all_player ['series_id'].unique().tolist()
        self.future_series_player = pre_series_player[~pre_series_player.series_id.isin(        historical_series_ids)]
        pass

    def main(self):

        series_ids = self.future_series_player['series_id'].unique().tolist()
        for series_id in series_ids:

            single_series_all_player = get_rows_where_column_equal_to(self.future_series_player,series_id,"series_id")
            start_date_time =    single_series_all_player .head(1)['start_date_time'].iloc[0]
            team_ids = get_unique_values_from_column_in_list_format(single_series_all_player,"team_id")
            team_player_ids = get_team_player_dictionary(single_series_all_player, "team_id", "player_id")
            SingleGame = SingleGameRatingGenerator(team_ids, team_player_ids, start_date_time, self.all_game_all_player,self.all_player,
                                                   update_dataframe=False, single_game_all_player=single_series_all_player)

            SingleGame.calculcate_ratings()
            expected_player_kill_percentages = self.calculcate_expected_player_kill_percentages(team_player_ids,SingleGame)
            team_ratings =  SingleGame.team_ratings[team_ids[0]]- SingleGame.team_ratings[team_ids[1]]

            win_probabilities = self.get_win_probability(SingleGame,team_ids)

            self.schedule_dict['Date'].append(start_date_time)
            self.schedule_dict['Team1'].append(team_ids[0])
            self.schedule_dict['Team2'].append(team_ids[1])
            self.schedule_dict['Win Probability1'].append(win_probabilities[team_ids[0]])
            self.schedule_dict['Win Probability2'].append(win_probabilities[team_ids[1]])

            KillsScenarioProbability = KillsScenarioProbabilityGenerator(team_player_ids, team_ratings,
                                                                         expected_player_kill_percentages,
                                                                         win_probabilities)
            scenario_df = KillsScenarioProbability.generate_round_probabilities()
            over_under_variations_df = KillsScenarioProbability.create_over_under_variations(scenario_df)
            sheet_name = team_ids[0] +'_' + team_ids[1]
            create_new_sheet_if_not_exist(sheet_name,self.workbook_name)
            append_df_to_sheet(over_under_variations_df,sheet_name,self.workbook_name)

        clear_sheet("Schedule",self.workbook_name)
        append_df_to_sheet(self.schedule_dict, "Schedule", self.workbook_name)

    def calculcate_expected_player_kill_percentages(self,team_player_ids,SingleGame):
        expected_player_kill_percentages = {}
        for team_id,player_ids in team_player_ids.items():
            team_estimated_kprs = []
            for player_id in player_ids:
                estimated_kpr = SingleGame.single_game_stored_player_values[player_id]['time_weighted_opponent_adjusted_kpr']
                team_estimated_kprs.append(estimated_kpr)

            for player_number,player_id in enumerate(player_ids):
                estimated_kill_percentage = team_estimated_kprs[player_number]/sum(team_estimated_kprs)
                expected_player_kill_percentages[player_id] = estimated_kill_percentage

        return expected_player_kill_percentages

    def get_win_probability(self,SingleGame,team_ids):
        win_probabilities = {}
        rating_difference = SingleGame.team_ratings[team_ids[0]]- SingleGame.team_ratings[team_ids[1]]
        win_probabilities[team_ids[0]] = 1/(1+10**(-rating_difference/3000))
        win_probabilities[team_ids[1]] = 1- win_probabilities[team_ids[0]]
        return win_probabilities




if __name__ == '__main__':
    SeriesPrediction = SeriesPredictionGenerator()
    SeriesPrediction.load_data()
    SeriesPrediction.main()