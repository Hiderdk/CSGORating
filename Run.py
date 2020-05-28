from Ratings.Main import RatingGenerator
from FutureGames.RunFutureSeries import SeriesPredictionGenerator
newest_games_only = True
min_date = "2015-07-01"
AllGames = RatingGenerator(newest_games_only, min_date)
AllGames.main()

SeriesPrediction = SeriesPredictionGenerator(calculcate_win_probabilities=True)
SeriesPrediction.load_data()
SeriesPrediction.main()

round_player_weapon = {
    'steam_id':[1,2,4,],
    'weapon_name':['Ak47','M4a1','AWP']
}

