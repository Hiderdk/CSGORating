class RegionPredictionGenerator():

    def __init__(self):
        pass


if __name__ == '__main__':
    RegionPrediction = RegionPredictionGenerator()
    import pandas as pd
    from fuzzywuzzy import process
    from fuzzywuzzy import fuzz
    df = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\all_game_all_player_performance_rating")
    player = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\all_player")
