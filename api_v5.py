'''
    api_v5.py

    This file takes data from api and multiple csv files to create a
    culmulative csv file of nba player stats and salaries with our player
    win contribution stat (Cont) at the end.

    Also, it runs a function to create a separate csv for modifying
    teams' season stats necessary for creating our statistic.

    Our statistic is created from linear regression analysis from graphs.py  
'''

import requests
import csv
import pandas as pd
from team_stats_player_salaries import *

# calls team_stats
team_stats()

from weights import Cont

#  input season year (ie. 2017 for 2017-2018 season)
season_year = 2017

def convert_csv(csv_file):
    ''' Function: convert_csv
        Parameters: csv_file
        Returns: data (list)
    '''
    # create empty list data and variable counter
    data = []
    counter = 0

    # opens csv
    with open(csv_file) as infile:
        csv_contents = csv.reader(infile, delimiter = ',')

        # for loop ignores header
        for row in csv_contents:
            if counter == 0:
                counter += 1

            # appends rows to data
            else:
                data.append(row)

    # returns data
    return data

def player_names():
    ''' Function: player_names
        Parameters: none
        Returns: player_name (list)
    '''

    # creates empty list id_salary
    id_salary = []

    # calls convert_csv
    salaries = convert_csv('salaries_1985to2018.csv')

    # for loop appends to id_salary
    for i in range(len(salaries)):
        if int(salaries[i][5]) == season_year and salaries[i][0] == 'NBA':
            id_salary.append([salaries[i][1], salaries[i][2]])

    # creates empty lists player_id and player_name
    player_id = []
    player_name = []

    # calls convert_csv
    players = convert_csv('players.csv')

    # for loop appends to player_id
    for i in range(len(players)):
        player_id.append([players[i][0], players[i][20]])

    # for loop appends to player_name if id_salary has a match
    for i in range(len(id_salary)):
        for j in range(len(player_id)):
            if id_salary[i][0] == player_id[j][0]:
                player_name.append(player_id[j][1])

    # return player_name
    return player_name
                
def player_id():
    ''' Function: player_id
        Parameters: none
        Returns: id_list (list), name_list (list)
    '''

    # calls player_names
    players = player_names()

    # creates empty lists id_list and name_list
    id_list = []
    name_list = []

    # for loop calls balldontlie api
    for i in range(33):
        http_params = {'per_page': 100,
                       'page': i + 1}
        url = ("https://www.balldontlie.io/api/v1/players")
        names = requests.get(url, params = http_params)

        # while loop for if request fails, retry
        while names.status_code != 200:
            names = requests.get(url, params = http_params)

        # converts call to json
        names = names.json()

        # for loop appends id to id_list and name to name_list from json
        for i in range(len(names['data'])):
            name_player = (names['data'][i]['first_name'] + " "
                            + names['data'][i]['last_name'])

            # skips repeats if any
            if name_player in players:
                if int(names['data'][i]['id']) in id_list:
                    pass
                id_list.append(int(names['data'][i]['id']))
                name_list.append(name_player)

    # returns id_list and name_list
    return id_list, name_list

def season_average(playerId):
    ''' Function: season_average
        Parameters: playerId
        Returns: averages (json)
    '''

    # calls balldontlie api
    http_params = {'season': season_year,
                   'player_ids[]': playerId}
    url = ("https://www.balldontlie.io/api/v1/season_averages")
    averages = requests.get(url, params = http_params)

    # while loop for if request fails, retry
    while averages.status_code != 200:
        averages = requests.get(url, params = http_params)

    # converts call to json
    averages = averages.json()

    # returns averages
    return averages


def statistics():
    ''' Function: statistics
        Parameters: none
        Returns: df
    '''

    # calls player_id
    playerId, names = player_id()

    # creates empty lists for playerId_lst, name, salary, and general NBA stats
    playerId_lst = []
    name = []
    salary = []
    gp = []
    mi = []
    pts = []
    fgm = []
    fga = []
    fg3m = []
    fg3a = []
    ftm = []
    fta = []
    fg_pct = []
    fg3_pct = []
    ft_pct = []
    ast = []
    reb = []
    oreb = []
    dreb = []
    blk = []
    stl = []
    to = []
    pf = []
    ef = []
    per = []
    con = []

    # for loop appends to lists
    for i in range(len(playerId)):
        avgs = season_average(playerId[i])
        if avgs['data'] != []:
            playerId_lst.append(playerId[i])
            name.append(names[i])
            salary.append(name_salary()[names[i]])
            games_played = avgs['data'][0]['games_played']
            gp.append(games_played)
            minutes = avgs['data'][0]['min']
            min_int = minutes.split(':')

            # changes minutes to decimal form
            avg_min = round((float(min_int[0]) + (float(min_int[1]) / 60)), 3)
            mi.append(avg_min)
            points = avgs['data'][0]['pts']
            pts.append(points)
            made_fg = avgs['data'][0]['fgm']
            fgm.append(made_fg)
            att_fg = avgs['data'][0]['fga']
            fga.append(att_fg)
            made_3pt = avgs['data'][0]['fg3m']
            fg3m.append(made_3pt)
            fg3a.append(avgs['data'][0]['fg3a'])
            made_ft = avgs['data'][0]['ftm']
            ftm.append(made_ft)
            att_ft = avgs['data'][0]['fta']
            fta.append(att_ft)
            fg_pct.append(avgs['data'][0]['fg_pct'])
            fg3_pct.append(avgs['data'][0]['fg3_pct'])
            ft_pct.append(avgs['data'][0]['ft_pct'])
            assists = avgs['data'][0]['ast']
            ast.append(assists)
            rebounds = avgs['data'][0]['reb']
            reb.append(rebounds)
            offreb = avgs['data'][0]['oreb']
            oreb.append(offreb)
            defreb = avgs['data'][0]['dreb']
            dreb.append(defreb)
            blocks = avgs['data'][0]['blk']
            blk.append(blocks)
            steals = avgs['data'][0]['stl']
            stl.append(steals)
            turnovers = avgs['data'][0]['turnover']
            to.append(turnovers)
            fouls = avgs['data'][0]['pf']
            pf.append(fouls)

            # calculates NBA efficiency
            player_ef = ((points + rebounds + assists + steals + blocks -
                         (att_fg - made_fg) - (att_ft - made_ft) - turnovers)
                         / games_played)
            ef.append(player_ef)

            # calculates linearly weighted player efficiency rating
            lin_PER = ((made_fg * 85.910) + (steals * 53.897) +
                       (made_3pt * 51.757) + (made_ft * 46.845) +
                       (blocks * 39.190) + (offreb * 39.190) +
                       (assists * 34.677) + (defreb * 14.707) -
                       (fouls * 17.174) - ((att_ft - made_ft) * 20.091) -
                       ((att_fg - made_fg) * 39.190) -
                       (turnovers * 53.897)) / avg_min
            per.append(lin_PER)

            # calculates contribution 
            find_con = (((made_fg * Cont['FG']) +
                        ((att_fg - made_fg) * Cont['FGMiss']) +
                        (made_3pt * Cont['3P']) + (made_ft * Cont['FT']) +
                        ((att_ft - made_ft) * Cont['FTMiss']) +
                        (offreb * Cont['ORB']) + (defreb * Cont['DRB']) +
                        (assists * Cont['AST']) + (steals * Cont['STL']) +
                        (blocks * Cont['BLK']) + (turnovers * Cont['TOV']) +
                        (fouls * Cont['PF']) + (points * Cont['PF'])) *
                        games_played)
            con.append(find_con)

    # creates dictionary
    dctn = {'Names': name, 'Salary': salary, 'gp': gp, 'min': mi, 'pts': pts,
            'fgm': fgm, 'fga': fga, 'fg3m': fg3m, 'fg3a': fg3a, 'ftm': ftm,
            'fta': fta, 'fg_pct': fg_pct, 'fg3_pct': fg3_pct, 'ft_pct': ft_pct,
            'ast': ast, 'reb': reb, 'oreb': oreb, 'dreb': dreb,'blk': blk,
            'stl': stl, 'to': to, 'pf': pf, 'eff': ef, 'PER': per, 'Cont': con}

    # creates datframe form dictionary with index playerId_lst
    df = pd.DataFrame(dctn)
    df.index = playerId_lst

    # returns dataframe
    return df

def main():
    # calls statistics
    stats = statistics()

    # creates csv from statistics
    stats.to_csv("statistics.csv")
    
main()
