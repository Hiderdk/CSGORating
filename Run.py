from Ratings.Main import RatingGenerator
from FutureGames.RunFutureSeries import SeriesPredictionGenerator
from trueskill_generator.run_trueskill import run_trueskill
newest_games_only = True


min_date = "2015-07-01"

run_trueskill(newest_games_only=True, min_date=min_date)
AllGames = RatingGenerator(newest_games_only, min_date)
AllGames.main()
SeriesPrediction = SeriesPredictionGenerator(calculcate_win_probabilities=True, make_sheet_for_newest_series_only=False)
SeriesPrediction.load_data()
SeriesPrediction.main()

