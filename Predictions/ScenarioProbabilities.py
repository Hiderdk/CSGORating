
from Functions.Miscellaneous import *
from Predictions.BinaryKillScenarioGenerator import BinaryKillScenarioGenerator


class KillsScenarioProbabilityGenerator():

    def __init__(self,team_players,team_ratings,expected_player_kill_percentages,result_probabilities):
        self.team_players = team_players
        self.result_probabilities = result_probabilities
        self.team_ratings = team_ratings


        self.ml_models_dict = {
           # 'kills': pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\kills_csgo"),
            #'kills_scaled': pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\kills_csgo_scaled"),
            'kills':pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\csgo_team_kills_model"),
            'net_round_wins_all_scaled':pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\total_kills_csgo_all_scaled"),
            'net_round_wins_all': pd.read_pickle(
                r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\total_kills_csgo_all"),

        }
        self.expected_player_kill_percentages = expected_player_kill_percentages


    def get_team_ids(self):
        team_ids = []
        for team in self.team_players:
            team_ids.append(team)
            return team_ids

        return team_ids

    def update_result_probabilities(self):
        unscaled_values = {
            'rating_difference': self.team_ratings[0] - self.team_ratings[1]

        }


        ml_model_scaled_data = self.ml_models_dict['net_round_wins_all_scaled']
        ml_model = self.ml_models_dict['net_round_wins_all']
        scaled_values = scale_features_and_insert_to_dataframe(ml_model_scaled_data, unscaled_values)
        round_probabilities = ml_model.predict_proba(scaled_values)[0]
        round_difference_classes = ml_model.classes_.tolist()
        index = round_difference_classes.index(0)
        ot_probability= round_probabilities[index]
        ot_probability =ot_probability*0.75
        self.result_probabilities['ot'] = ot_probability





    def generate_round_probabilities(self):
        #self.update_result_probabilities()

        BinaryKillScenario = BinaryKillScenarioGenerator()
        for number,team in enumerate(self.team_players):
            unscaled_values = {
                'rating_difference':self.team_ratings[number]-self.team_ratings[-number+1]
            }

           # ml_model_scaled_data = self.ml_models_dict['kills_scaled']
            ml_model = self.ml_models_dict['kills']
            X = convert_dict_to_df(unscaled_values)
            team_kill_probabilities = ml_model.predict_proba(X)[0]
            team_kills = ml_model.classes_
            sum_k = 0
            for team_kill_number,team_kill in enumerate(team_kills):
                team_kill_probability = team_kill_probabilities[team_kill_number]

                for player in self.team_players[team]:
                    estimated_player_kill_percentage = self.expected_player_kill_percentages[player]

                    BinaryKillScenario.create_scenario_probabilities_for_single_player_single_team_kill \
                                (team,player, estimated_player_kill_percentage, team_kill, team_kill_probability)

                sum_k+=        team_kill_probability*team_kill




        return pd.DataFrame.from_dict(BinaryKillScenario.scenario_dict)

    def create_team_kill_probabilities(self,team_number,unscaled_values):
        team_kill_probabilities = {}
        tot_k = 0

        result_probability = 1
        for team_kill, team_kill_probability in team_kill_probabilities_given_outcome.items():



            if team_kill not in team_kill_probabilities:
                team_kill_probabilities[team_kill] = 0
            team_kill_probabilities[team_kill] +=result_probability * 1


        return team_kill_probabilities




    def create_over_under_variations(self,scenario_df):
        google_sheet_player_kill_over_dict = {
            'Predictions':[]
        }
        google_sheet_player_kill_over_dict['Predictions'].append("Estimated Kill Percentage")
        google_sheet_player_kill_over_dict['Predictions'].append("Estimated Kills")
        for kill in range(12,24):
           google_sheet_player_kill_over_dict['Predictions'].append("Over " + str(kill+0.5))

        for team in self.team_players:
            team_rows = scenario_df[scenario_df['team_name']==team]
            estimated_team_kill = round((team_rows['player_kills'] * team_rows['scenario_probability']).sum(),1)

            for player in self.team_players[team]:
                player_df = scenario_df[scenario_df['player_name']==player]
                google_sheet_player_kill_over_dict[player] = []
                estimated_player_kill = round((player_df['player_kills']*player_df['scenario_probability']).sum(),1)
                estimated_kill_percentage = round(estimated_player_kill/estimated_team_kill,3)
                google_sheet_player_kill_over_dict[player].append(estimated_kill_percentage)
                google_sheet_player_kill_over_dict[player].append(estimated_player_kill)

                for kill in range(12, 24):
                    rows = player_df[player_df['player_kills']>kill]
                    sum = rows['scenario_probability'].sum()
                    percentage_prob = str(round(sum*100,0)) + "%"
                    google_sheet_player_kill_over_dict[player].append(percentage_prob)

        return  pd.DataFrame.from_dict(google_sheet_player_kill_over_dict)

class AllGamesGenerator():
    pass

if __name__ == '__main__':
    AllGames = AllGamesGenerator()

    AllGames.all_game_all_player = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\all_game_all_player_performance_rating")
    team_players = {
        'Astralis':['Device','Dupreeh','Magisk','Xyp9x','Gla1ve'],
        'Natus Vincere':['S1mple','Electronic','Perfecto','Bomblch','flamie'],
    }

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
    team_ratings = {
        'Astralis':4000,
        'Natus Vincere':3500,
    }

    result_probabilities = {0:0.56,1:0.36,'ot':0.08}
    KillsScenarioProbability = KillsScenarioProbabilityGenerator(team_players,team_ratings,expected_player_kill_percentages,result_probabilities)
    KillsScenarioProbability.get_team_ids()
    scenario_df = KillsScenarioProbability.generate_round_probabilities()
    scenario_df.to_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\scenario_df")
    over_under_variations = KillsScenarioProbability.create_over_under_variations(scenario_df)
    print(over_under_variations)
