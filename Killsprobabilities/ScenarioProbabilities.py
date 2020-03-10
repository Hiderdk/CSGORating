from TimeWeightRatings.SingleGame import SingleGameRatingGenerator
from Functions.Miscellaneous import *
from Killsprobabilities.BinaryKillScenarioGenerator import BinaryKillScenarioGenerator
import scipy.stats as ss
v = 3
ot_probability = 0.08

class KillsScenarioProbabilityGenerator():

    def __init__(self,team_players,ml_models_dict,player_ratings,expected_player_kill_percentages,result_probabilities):
        self.team_players = team_players
        self.result_probabilities = result_probabilities
        self.player_ratings = player_ratings
        self.ml_models_dict=ml_models_dict
        self.expected_player_kill_percentages = expected_player_kill_percentages


    def get_team_ids(self):
        team_ids = []
        for team in self.team_players:
            team_ids.append(team)
            return team_ids

        return team_ids

    def get_timeweight_player_ratings(self,start_date_time):
        team_ids = self.get_team_ids()
        SingleGameRating = SingleGameRatingGenerator(team_ids, self.team_players, start_date_time)
        SingleGameRating.main()

    def generate_round_probabilities(self):

        team_ratings = []
        for team in self.team_players:
            team_ratings.append(self.get_team_ratings_from_player_ratings(team))

        BinaryKillScenario = BinaryKillScenarioGenerator()
        for number,team in enumerate(self.team_players):
            unscaled_values = {
                'rating_difference':team_ratings[number]-team_ratings[-number+1]
            }
            team_kill_probabilities = self.create_team_kill_probabilities(unscaled_values)

            for team_kill,team_kill_probability in team_kill_probabilities.items():

                for player in self.team_players[team]:
                    estimated_player_kill_percentage = expected_player_kill_percentages[player]

                    BinaryKillScenario.create_scenario_probabilities_for_single_player_single_team_kill \
                                (team,player, estimated_player_kill_percentage, team_kill, team_kill_probability)


        scenario_df = pd.DataFrame.from_dict(BinaryKillScenario.scenario_dict)
        scenario_df.to_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\scenario_df")
        over_under_variations = self.create_over_under_variations(scenario_df,team_players)
        print(over_under_variations)

    def create_team_kill_probabilities(self,unscaled_values):
        team_kill_probabilities = {}

        for result, result_probability in self.result_probabilities.items():
            ml_model_scaled_data = self.ml_models_dict[str(result) + '_scaled']
            self.ml_model = self.ml_models_dict[str(result)]
            scaled_values = scale_features_and_insert_to_dataframe(ml_model_scaled_data, unscaled_values)
            round_probabilities = self.ml_model.predict_proba(scaled_values)[0]
            round_difference_classes = self.ml_model.classes_

            for number, round_difference in enumerate(round_difference_classes):
                if round_difference == 0:
                    continue
                round_probability = round_probabilities[number]
                if result == "ot":
                    team_kill_probabilities_lookup_table =       self.ml_models_dict['ot_team_kill_probabilities']
                else:
                    team_kill_probabilities_lookup_table = self.ml_models_dict['team_kill_probabilities']
                team_kill_probabilities_given_outcome = team_kill_probabilities_lookup_table[round_difference]
                result_outcome_probability = round_probability * result_probability

                for team_kill,team_kill_probability in team_kill_probabilities_given_outcome.items():
                    if team_kill not in team_kill_probabilities:
                        team_kill_probabilities[team_kill] = 0
                    team_kill_probabilities[team_kill] +=team_kill_probability * result_outcome_probability


        return team_kill_probabilities


    def get_team_ratings_from_player_ratings(self,team):
        team_rating = 0
        for player in self.team_players[team]:
            team_rating += self.player_ratings[player]/len(self.team_players[team])

        return     team_rating


    def create_over_under_variations(self,scenario_df,team_players):
        self.google_sheet_player_kill_over_dict = {
            'Line':[]
        }
        for kill in range(13,25):
            self.google_sheet_player_kill_over_dict['Line'].append("Over" + str(kill+0.5))

        for team in team_players:
            for player in team_players[team]:
                player_df = scenario_df[scenario_df['player_name']==player]
                self.google_sheet_player_kill_over_dict[player] = []

                for kill in range(13, 25):
                    rows = player_df[player_df['player_kills']>kill]
                    sum = rows['scenario_probability'].sum()
                    self.google_sheet_player_kill_over_dict[player].append(sum)

        return  self.google_sheet_player_kill_over_dict

class AllGamesGenerator():
    pass

if __name__ == '__main__':
    AllGames = AllGamesGenerator()
    ml_models_dict = {}
    net_round_wins_0 = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\total_kills_csgo_0")
    net_round_wins_ot = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\total_kills_csgo_ot")
    net_round_wins_1 = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\total_kills_csgo_1")
    net_round_wins_0_scaled = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\total_kills_csgo_0_scaled")
    net_round_wins_1_scaled = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\total_kills_csgo_1_scaled")
    net_round_wins_ot_scaled = pd.read_pickle(
        r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\total_kills_csgo_ot_scaled")


    ml_models_dict = {
        "0":  net_round_wins_0,
        "1":net_round_wins_1,
        "0_scaled": net_round_wins_0_scaled,
         "1_scaled":net_round_wins_1_scaled,
        'ot':net_round_wins_ot,
        'ot_scaled':net_round_wins_ot_scaled,
        'team_kill_probabilities' :pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\ot_0_net_rounds_to_kills"),
        'ot_team_kill_probabilities': pd.read_pickle(
            r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\ot_1_net_rounds_to_kills"),
    }
    AllGames.all_game_all_player = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\all_game_all_player_performance_rating")
    team_players = {
        'Astralis':['Device','Dupreeh','Magisk','Xyp9x'],
        'Natus Vincere':['S1mple','Electronic','Perfecto','Bomblch','flamie'],
    }

    #KillsScenarioProbability.get_timeweight_player_ratings("2019-12-01")
    expected_player_kill_percentages = {
        'Device':0.21,
        'Dupreeh':0.21,
        'Magisk':0.2,
        'Gla1ve':0.19,
        'Xyp9x':0.18,
        'S1mple': 0.21,
        'Electronic': 0.21,
        'Perfecto': 0.2,
        'Bomblch': 0.19,
        'flamie': 0.18,
    }
    player_ratings = {
        'Device': 4000,
        'Dupreeh': 4000,
        'Magisk': 4000,
        'Gla1ve': 4000,
        'Xyp9x': 4000,
        'S1mple': 4000,
        'Electronic': 3200,
        'Perfecto': 3200,
        'Bomblch':3200,
        'flamie': 3200,
    }

    result_probabilities = {0:0.56,1:0.36,'ot':0.08}
    KillsScenarioProbability = KillsScenarioProbabilityGenerator(team_players,ml_models_dict,player_ratings,expected_player_kill_percentages,result_probabilities)
    KillsScenarioProbability.get_team_ids()
    KillsScenarioProbability.generate_round_probabilities()