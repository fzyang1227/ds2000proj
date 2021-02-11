'''
    Plotting Histograms and Scatter Plots for analysis
    Also makes and prints dataframes sorted by various 
    statistics (see per_million)
    Makes a final csv file with relevant contribution stats
'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

def hist_stat(df):
    ''' Function: hist_stat
        Parameters: df (dataframe)
        Returns: none
        Does: creates histogram
    '''

    # for loop iterates by column, creates histogram, and saves to pdf
    for col in df.columns[4:]:
        df.hist(column = col, bins = 25, grid = False, figsize = (9,6),
                color = '#2FB7D7', rwidth = 0.9)
        plt.savefig('hist_{}.pdf'.format(col))
        plt.show()

def scatter_stat(df, win):
    ''' Function: scatter_stat
        Parameters: df (dataframe), win(string)
        Returns: none
        Does: creates scatterplot
    '''

    # creates empty lists coef and coef_weights
    coef = []
    coef_weights = []

    # for loop iterates by column
    for col in df.columns[:-1]:
        
        # for linear regression data
        x_stat = df[col]
        y_stat = df[win]
        x_stat = sm.add_constant(x_stat)
        model = sm.OLS(y_stat, x_stat).fit()
        print('For ', col, ':', '\n', model.summary(), '\n', sep = '')

        # grabbing coefficients from data
        model_coef = list(model.params)
        model_coef.append(col)
        coef.append(model_coef)
        
        # for making linear regression line
        x_pred = np.linspace(x_stat.min(), x_stat.max(), 50)
        x_pred2 = sm.add_constant(x_pred)
        y_pred = model.predict(x_pred2)
        x_pred = np.delete(x_pred, np.s_[:1], 1)

        # plotting scatter plot with regression line
        df.plot.scatter(x = col, y = win)
        plt.plot(x_pred, y_pred, color = 'red')
        plt.savefig('scatter_{}.pdf'.format(col))
        plt.show()

def scatter_players(df):
    ''' Function: scatter_players
        Parameters: df (dataframe)
        Returns: params
        Does: creates scatterplot
    '''

    # specifies columns
    cols = ['eff', 'PER', 'Cont']

    # empty dictionary of params
    params = {}

    # for loop iterates by specified columns
    for col in cols:
        
        # making linear regression line
        x_stat = df['Salary/$mil']
        y_stat = df[col]
        model = sm.OLS(y_stat, x_stat).fit()
        x_pred = np.linspace(x_stat.min(), x_stat.max(), 50)
        y_pred = model.predict(x_pred)

        # adding to dictionary the coefficients of linear regression
        params[col] = float(model.params)

        # print top players by stat
        top_df = df.sort_values(by = col, ascending = False)
        print('Top/Bottom 10 in {}:\n\n'.format(col),
              top_df.head(10), '\n\n', top_df.tail(10), '\n\n')

        # creates scatterplots and saves to pdf
        fig, ax = plt.subplots()
        df.plot.scatter(x = 'Salary/$mil', y = col, c = 'green', zorder = 2, ax = ax)

        # annotates the top 3 points in the stat
        for index, column in top_df.head(3).iterrows():
            ax.annotate(index, (column['Salary/$mil'] + .5, column[col]))
        plt.plot(x_pred, y_pred, linestyle = '--', color = 'black')
        plt.grid(linestyle = ':')
        plt.savefig('salary_vs_{}.pdf'.format(col))
        plt.show()

    return params


def per_million(df):
    ''' Function: scatter_players
        Parameters: df (dataframe)
        Returns: df (dataframe)
        Does: prints dataframes to view players sorted by how much
              they are over/underpaid based on linear regression line
              Also adds to dataframe.
    '''
    # calls above function and returns the coefficient from linear regression
    params = scatter_players(df)
    
    # specifies columns
    cols = ['eff', 'PER', 'Cont']
    cols_dollar = ['eff/$mil', 'PER/$mil', 'Cont/$mil']
    
    for col in cols:
        
        # adding per million to dataframe
        df['{}/$mil'.format(col)] = (df[col] / (df['Salary/$mil']))

        # calculating difference between how much should be paid
        # and how much they are actually paid based on linear regression
        df['Net Diff. $mil({})'.format(col)] = ((df[col] / params[col]) -
                                                 df['Salary/$mil'])

        # sorting by above metric
        top_df = df.sort_values(by = 'Net Diff. $mil({})'.format(col),
                                ascending = False)
        # moving column to view in idle
        col_name = top_df.pop(col)
        top_df.insert(1, col_name.name, col_name)
        
        print('Top/Bottom 10 in Net Diff. $mil({}):\n'.format(col),
              top_df.head(10), '\n', top_df.tail(10), '\n\n')
        
    return df
        
def main():

    # reads csv, calls hist_stat
    nba_df = pd.read_csv('statistics.csv', index_col = 0)
    hist_stat(nba_df)

    # reads csv, makes dataframe
    team_nba_df = pd.read_csv('team_stats(2018)v2.csv', index_col = 1)
    team_nba_df = team_nba_df.drop(columns = ['Rk', '2P', 'FTA', 'FGA'])

    # calls scatter_stat
    scatter_stat(team_nba_df, 'Wins')

    # modifies nba_df to more suitable dataframe for function
    nba_df_indexed = nba_df.set_index('Names')
    mod_nba = nba_df_indexed[['Salary', 'eff', 'PER', 'Cont']]
    mod_nba['Salary'] = mod_nba['Salary'].div(1000000)
    mod_nba.rename(columns = {'Salary': 'Salary/$mil'}, inplace = True)
    
    # calls per_million
    final_stats = per_million(mod_nba)
    final_stats.to_csv('contribution_stats.csv')
    
main()
