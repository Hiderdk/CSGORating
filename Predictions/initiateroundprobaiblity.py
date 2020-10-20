import pickle
import pandas as pd
from Predictions.RoundWinProbability import RoundProbabilityGenerator
loaded_model = pickle.load(
    open(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\round_difference_probability", 'rb'))
prob = loaded_model.predict_proba(0.52)
rp = RoundProbabilityGenerator(simulations=28000)
df = pd.read_pickle(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\_newall_game_all_team_rating")
df = df.drop_duplicates(subset=['game_id'])
df['rating_difference'] = df['time_weight_rating'] - df['opponent_time_weight_rating']
df['default_rating_difference'] = df['time_weight_default_rating'] - df['opponent_time_weight_default_rating']

df = df[df['start_date_time'] > '2020-03-01']
from sklearn.linear_model import LogisticRegression

model = LogisticRegression()
X = df[['rating_difference', 'default_rating_difference']]
model.fit(X, df['won'])
df['prob'] = model.predict_proba(X)[:, 1]
df['round_difference'] = df['rounds_won'] - df['rounds_lost']


rp.fit(df)
pickle.dump(rp, open(r"C:\Users\Mathias\PycharmProjects\Ratings\Files\models\round_difference_probability", "wb"))
