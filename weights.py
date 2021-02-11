'''
    Ability to import dictionary of stat weights to api_v5
'''

import pandas as pd
import statsmodels.api as sm

def get_regression_coef(df, win):
    ''' Function: get_regression_coef
        Parameters: df (dataframe), win (string)
        Returns: coef_weights (dict)
    '''

    # creates empty list coef and dict coef_weights
    coef = []
    coef_weights = {}

    # for loop iterates through columns
    for col in df.columns[:-1]:

        # for linear regression data
        x_stat = df[col]
        y_stat = df[win]
        x_stat = sm.add_constant(x_stat)
        model = sm.OLS(y_stat, x_stat).fit()

        # grabbing coefficients from data
        model_coef = list(model.params)
        model_coef.append(col)
        coef.append(model_coef)

    # for loop addes coef to coef_weights
    for i in range(len(coef)):
        coef_weights[coef[i][2]] = coef[i][1]

    # returns coef_weights
    return coef_weights

# reads csv, creates dataframe
team_nba_df = pd.read_csv('team_stats(2018)v2.csv', index_col = 1)
team_nba_df = team_nba_df.drop(columns = ['Rk', '2P', 'FTA', 'FGA'])

# calls get_regression_coef
Cont = get_regression_coef(team_nba_df, 'Wins')
