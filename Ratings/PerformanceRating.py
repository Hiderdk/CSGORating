from Functions.Miscellaneous import *
from Functions.AverageValues import *
import pickle
from sklearn import preprocessing
performance_rating= {
    0:{
        'column_name':'kpr','effect':1,'weight':0.47},
    1: {
        'column_name': 'dpr', 'effect': -1, 'weight':0.32},
    2: {
        'column_name': 'net_opening_duels_won',  'effect': 1, 'weight':0.06},
    3:{
        'column_name': 'net_adr', 'effect': 1, 'weight':0.15},
}


def calculcate_predicted_adr(df):
    full_filepath = r"C:\Users\Mathias\PycharmProjects\StatisticalModels\adr"
    X_values = df[['kpr']]
    model = pickle.load(open(full_filepath, 'rb'))
   #scaler = preprocessing.StandardScaler()
    #standardized_X_values =  scaler.fit_transform(X_values)

    return model.predict(X_values)


def add_game_player_simple_ratings(df):
    df['opening_attempts'] = df['opening_kills'] +  df['opening_deaths']
    df['opening_win_rate'] = df['opening_kills'] /  (df['opening_kills'] +
                                                        df['opening_deaths'])

    df['opening_attempt_percentage'] = df['opening_attempts'] / \
                                                                 (df['rounds_won'] +
                                                                  df['rounds_lost'])
    df['opening_win_rate'] = df['opening_win_rate'].fillna(0.5)
    df['expected_opening_duels_won'] = df['opening_attempts']*0.5
    df['net_opening_duels_won'] = df['opening_kills']-df['expected_opening_duels_won']
    df['net_opening_duels_won'] =  df['net_opening_duels_won'].fillna(0)
    df['headshots_percentage'] = df['headshots'] /  df['kills']
    df['kpr'] = df['kills'] / (
                    df['rounds_won'] + df['rounds_lost'])

    df['dpr'] = df['deaths'] / ( df['rounds_won'] + df['rounds_lost'])

    return df


def add_performance_rating(df):
    df['performance_rating'] = 0
    for metric_number, metric_context in performance_rating.items():
        effect = metric_context['effect']
        weight = metric_context['weight']
        column_name = metric_context['column_name']
        mean_value = get_average_value_from_column_name(df, column_name)
        std = get_standard_deviation_from_column_name(df, column_name)
        standardized_values = (df[column_name] - mean_value) / std
        df['performance_rating'] += standardized_values * effect * weight * 100

    return df['performance_rating']
