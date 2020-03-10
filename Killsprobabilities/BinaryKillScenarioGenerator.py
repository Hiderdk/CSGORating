import scipy.stats as ss
import pandas as pd

class BinaryKillScenarioGenerator():

    def __init__(self):

        self.scenario_dict = {
           # 'result': [],
            'team_name': [],
            'player_name': [],
            'team_kills': [],
            'player_kills': [],
            'team_kill_probability': [],
            'scenario_probability': [],
        }



    def create_scenario_probabilities_for_single_player_single_team_kill(self,team_name,player_name,estimated_player_kill_percentage,team_kill,team_kill_probability):

        self.player_name = player_name
        self.team_name = team_name
        self.team_kill = team_kill
        self.team_kill_probability = team_kill_probability
        self.binomial_probability_object = ss.binom(team_kill, estimated_player_kill_percentage)

        if team_kill == 0:
            self.append_0_team_kill_scenario()

        for self.player_kill in range(int(team_kill)):
            self.player_kill_probability = self.binomial_probability_object.pmf(self.player_kill)
            self.scenario_probability = self.player_kill_probability * self.team_kill_probability
            # self.get_player_kill_probability()

            self.append_scenario()




    def append_0_team_kill_scenario(self):
        self.scenario_dict['team_name'].append(self.team_name)
       # self.scenario_dict['result'].append(self.result)
        self.scenario_dict['player_name'].append(self.player_name)
        self.scenario_dict['team_kills'].append(self.team_kills)
        self.scenario_dict['team_kill_probability'].append(self.team_kill_probability)
        self.scenario_dict['scenario_probability'].append(self.team_kill_probability)
        self.scenario_dict['player_kills'].append(0)


    def append_scenario(self):
        self.scenario_dict['team_name'].append(self.team_name)
        #self.scenario_dict['result'].append(self.result)
        self.scenario_dict['player_name'].append(self.player_name)
        self.scenario_dict['team_kills'].append(self.team_kill)
        self.scenario_dict['team_kill_probability'].append(self.team_kill_probability)

        self.scenario_dict['scenario_probability'].append(self.scenario_probability)
        self.scenario_dict['player_kills'].append(self.player_kill)



    def get_team_names(self):
        self.team_names = self.scenario_df['team_name'].unique().tolist()

    def get_side_id_player_names(self):

        self.side_id_player_names = {}

        for self.team_name in self.team_names:
            self.side_id_player_names[self.team_name] = \
                self.scenario_df[self.scenario_df['team_name']==self.team_name]['player_name'].unique().tolist()



    def create_google_sheets_dict(self):

        self.google_sheets_dict = {
            'Model Estimations':["Estimated Kills","Kill Percentage"],
        }

        for side_id in self.side_id_player_names:
            for player_name in self.side_id_player_names[side_id]:

                self.google_sheets_dict[player_name] = []


    def get_filtered_rows_for_single_team(self):

        self.single_team_rows = self.team_scenario_df.loc[
            (self.team_scenario_df['team_name']==self.team_name) ]


    def calculate_weighted_team_estimated_kills(self):

        self.weighted_team_total_estimated_kills = (np.sum(
            self.single_team_rows['team_kill_probability_given_win_probability'].values*
            self.single_team_rows  ['team_kills'].values))


    def get_filtered_rows_for_single_player(self):

        self.single_player_rows = self.scenario_df.loc[
            (self.scenario_df['team_name'] == self.team_name) &
            (self.scenario_df['player_name']==self.player_name)]


    def calculate_weighted_player_estimated_kills(self):
        self.weighted_total_estimated_kills = (np.sum(
            self.single_player_rows['scenario_probability'].values *
            self.single_player_rows['player_kills'].values))

    def calculate_weighted_player_estimated_kill_percentage(self):
        team_df = self.scenario_df[self.scenario_df['team_name']==self.team_name]
        player_df = team_df[team_df['player_name']==self.player_name]
        player_kill_estimation = (player_df['player_kills'] * player_df['scenario_probability']).sum()
        team_kill_estimation = (player_df['team_kills']*player_df['scenario_probability']).sum()
        self.weighted_total_estimated_kill = player_kill_estimation
        self.weighted_total_estimated_kill_percentage = player_kill_estimation/team_kill_estimation
      #  self.single_player_rows['kill_percentage'] = \
     #      (self.single_player_rows['player_kills']/self.single_player_rows['team_kills'])

       # self.weighted_total_estimated_kill_percentage = (np.sum(
        #    self.single_player_rows['scenario_probability'].values *
        #    self.single_player_rows['kill_percentage'].values))



    def update_google_sheets_first_row(self):
        self.google_sheets_dict[self.player_name].append(round(self.weighted_total_estimated_kills,2) )
        self.google_sheets_dict[self.player_name].append(str(self.weighted_total_estimated_kill_percentage*100)+'%' )

    def calculate_over_probability(self):

        self.single_player_over_kills = (
                self.single_player_rows[
                self.single_player_rows['player_kills'] >= self.kills]
            )

        self.over_player_kill_probability =  self.single_player_over_kills['scenario_probability'].sum()

    def append_first_column_to_google_sheet_dict(self):
        string = "Over " + str(self.kills-0.5)
        self.google_sheets_dict["Model Estimations"].append(string)

    def append_to_google_sheet_dict(self):
        self.google_sheets_dict[self.player_name].append(str(int(self.over_player_kill_probability*100))+'%' )


    def convert_to_dataframe(self):

        self.google_sheets_df = pd.DataFrame.from_dict(self.google_sheets_dict)








if __name__ == '__main__':
    result_variations = [-16,-15,15,16]
    BinaryKillScenario = BinaryKillScenarioGenerator()
    estimated_player_kill_percentage = 0.2
    team_kill = 90
    result = 4
    team_kill_probability = 0.15
    result_probability = 0.08
    player_name = "device"
    team_name = "Astralis"
    BinaryKillScenario.create_scenario_probabilities_for_single_player_single_team_kill\
        (player_name,estimated_player_kill_percentage,team_kill,team_kill_probability,result,result_probability,team_name)
    BinaryKillScenario.scenario_df = BinaryKillScenario.scenario_dict