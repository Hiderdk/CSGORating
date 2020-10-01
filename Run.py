from Ratings.Main import RatingGenerator
from FutureGames.RunFutureSeries import SeriesPredictionGenerator
newest_games_only = True


min_date = "2015-07-01"
AllGames = RatingGenerator(newest_games_only, min_date)
AllGames.main()

SeriesPrediction = SeriesPredictionGenerator(calculcate_win_probabilities=True, make_sheet_for_newest_series_only=False)
SeriesPrediction.load_data()
SeriesPrediction.main()

