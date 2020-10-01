class PickBanPredictor():

    def __init__(self,
                 model,
                 team_player_ids,
                 series_team
                 ):
        self.team_player_ids = team_player_ids
        self. series_team = series_team
        self.model = model


    def get_pick_ban_probabilities(self):
        self.model.predict_proba(X)

        return probabilities


