'''
    team_stats_player_salaries.py
    
    NBA Team Stats and Player Salaries
    Pulling from RapidAPI for team wins
    Pulling from two csv files player salaries:
     - salaries_1985to2018.csv
     - players.csv
    Pulling from csv file for team season stats (saved as dataframe):
     - team_stats(2018).csv
'''
import csv
import pandas as pd
import requests

# parameters for the api requests
headers = {
    'x-rapidapi-host': "api-nba-v1.p.rapidapi.com",
    'x-rapidapi-key': "b20705a586msh19f6c5762cf7eb8p1ca43djsndcd90365849b"
    }

# the urls for the different parts of the api we want to request
win_loss_url = "https://api-nba-v1.p.rapidapi.com/standings/standard/2018"

team_url = "https://api-nba-v1.p.rapidapi.com/teams/league/standard"

def get_dict(url):
    ''' Function: get_dict
        Parameters: url (string)
        Returns: response.json() (dictionary)
        Does: pulls dictionary from JSON files from API
    '''
    response = requests.get(url, headers=headers)

    # to make sure response is good
    if response.status_code == 200:
        return response.json()
    
    else:
        print(response.status_code)
        print('Error')
        return none
        

def get_name(team_id):
    ''' Function: get_name
        Parameters: team_id (string)
        Returns: team_name (string)
        Does: returns the name of the team for their id
    '''
    team_info = get_dict(team_url)

    # matching up team id to team name
    for i in range(len(team_info["api"]["teams"])):                   
        if str(team_id) == team_info["api"]["teams"][i]["teamId"]:
            team_name = team_info["api"]["teams"][i]["fullName"]
    
    return team_name


def get_record_names(record_dict):
    ''' Function: get_record_names
        Parameters: record_dict (dictionary)
        Returns: alphabet_teams (dictionary)
        Does: takes in a json dictionary and gives dictionary
              with team_names as keys and the number of wins the team
              has as the values
    '''
    num_wins = []
    team_ids = []

    # appending values to lists
    for i in range(len(record_dict['api']['standings'])):
        num_wins.append(record_dict['api']['standings'][i]['win'])
        team_ids.append(record_dict['api']['standings'][i]['teamId'])

    # calling get_name function to convert ids to names
    for i in range(len(team_ids)):
        team_ids[i] = get_name(team_ids[i])

    # converting two lists to a dictionary
    teams = zip(team_ids, num_wins)

    # alphabetizing dictionary to more easily add to csv data set
    alphabet_teams = sorted(teams)

    return alphabet_teams


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


def name_salary():
    ''' Function: name_salary
        Parameters: none
        Returns: player_name_salary (dictionary)
    '''

    # creates empty list id_salary
    id_salary = []
    
    # calls convert_csv
    salaries = convert_csv('salaries_1985to2018.csv')

    # for loop that appends player id and salary
    for i in range(len(salaries)):
        if int(salaries[i][5]) == 2017 and salaries[i][0] == 'NBA':
            id_salary.append([salaries[i][1], salaries[i][2]])

    player_id = []
    players = convert_csv('players.csv')

    # for loop that appends player id and name from another csv file
    for i in range(len(players)):
        player_id.append([players[i][0], players[i][20]])

    # empty dictionary
    player_name_salary = {}

    # loop to match player names with salary as a dictionary
    # dictionary with names as keys and salaries with values
    for i in range(len(id_salary)):
        for j in range(len(player_id)):
            if id_salary[i][0] == player_id[j][0]:
                player_name_salary[player_id[j][1]] = id_salary[i][1]

    return player_name_salary


def team_stats():
    ''' Function: team_stats
        Parameters: none
        Returns: none
        Does: adds wins and other relevant stats to csv and getting rid
              of some stats too, saving as a version 2 of the csv
    '''
    # reading csv file into dataframe
    df = pd.read_csv('team_stats(2018).csv', index_col = 0)
    df = df.drop([31])

    # getting nba standings with (team, wins) in alphabetized list
    nba_dict = get_dict(win_loss_url)
    nba_standings = get_record_names(nba_dict)

    # unzipping dictionary into two lists
    team_names, wins = zip(*nba_standings)
    wins = list(wins)
    for i in range(len(wins)):
        wins[i] = int(wins[i])/82

    # inserting more relevant stats into dataframe/new csv
    df.insert(4, 'FGMiss', df['FGA'] - df['FG'])
    df.insert(14, 'FTMiss', df['FTA'] - df['FT'])

    # dropping some irrelevant stats
    df = df.drop(columns = ['FG%', '3P%', '2P%', 'FT%', 'TRB', 'G', 'MP', '3PA', '2PA'])

    # adding team wins to dataframe
    df['Wins'] = wins

    # saving the dataframe as a new csv
    df.to_csv('team_stats(2018)v2.csv')
    
