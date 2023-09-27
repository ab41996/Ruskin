#%%
import pandas as pd
import numpy as np



#%% CREATE DUMMY DATA TO GET THE BALL ROLLING

d = {"match_date": "2023-09-01",
     "match_data" : [{"date": "2023-09-01",
         "competition": "League",
         "opponent": "Athenians",
         "score": [5,1],
         "ref_pay": "AB",
         "player_data": {
             "GM": {"Ap":1, "G":4,"A": 1},
             "BS": {"Ap":1, "G":4,"A": 1},
             "AB": {"Ap":0.5, "G":4,"A": 1},
             "JS": {"Ap":1, "G":1,"Y": 1}
                  }
         }]}

raw_games_data = pd.DataFrame(data=d, columns=["match_date", "match_data"])
raw_games_data.set_index("match_date")


#%% DEFINE FUNCTION TO ADD DATA TO RAW GAMES DATA

def create_game(date, competition, opponent, score, ref_pay, player_data):

    global raw_games_data

    input_data = {"match_date": date,
     "data" : [{"date": date,
         "competition": competition,
         "opponent": opponent,
         "score": score,
         "ref_pay": ref_pay,
         "player_data": player_data
         }]}
    
    if len(raw_games_data.loc[raw_games_data.match_date == date, "match_data"])>0:
        if input(f'Do you want to overwrite {date}...(y/n)') == 'y':
            raw_games_data.loc[raw_games_data.match_date == date, "data"] = input_data['player_data']

    else:
        raw_games_data = pd.concat([raw_games_data, pd.DataFrame(input_data)])

        print("new game added..")
        print(input_data)


#%% TEST OUT ADDING DATA TO RAW GAMES DATA

create_game("2023-09-08",
            "League",
            "Wood Lane",
            [5-1],
            "AB",
            {
             "GM": {"Ap":1, "G":4,"A": 1},
             "BS": {"Ap":1, "G":4,"A": 1},
             "AB": {"Ap":0.5, "G":4,"A": 1},
             "JS": {"Ap":1, "G":1,"Y": 1}
                  })


raw_games_data

#%% 



















#%%

class Season:
    def __init__(self, year):
        self.year = year
        self.games = {}
        self.total_goals = 0
        self.total_yellow_cards = 0
        self.total_red_cards = 0
        # self.total_red_cards_35 = 0
        # self.total_red_cards_55 = 0

    def create_game(self, date, competition, opponent, ruskin_score, opp_score, data):
        game = self.Game(date, competition, opponent, ruskin_score, opp_score, data)
        self.games[date] = game
        self.total_goals += ruskin_score

    class Game():
        def __init__(self, date, competition, opponent, ruskin_score, opp_score, data):
            self.date = date
            self.competition = competition
            self.opponent = opponent
            self.ruskin_score = ruskin_score
            self.opp_score = opp_score
            self.score = f"{ruskin_score} - {opp_score}"
            self.data = data

#%%

season_2023 = Season(2023)

#%%

season_2023.year


#%%

season_2023.create_game("2023-09-12", "League","Athenians", 3,2, {"AH":[], "GM":[]})
#%%

season_2023.games["2023-09-12"].score


#%%

class Player():
    def __init__(self):
        self.appearances = 0
        self.minutes = 0
        self.goals = 0
        self.assists = 0
        self.balance = 0



    def add_game(self, date, opponent, competition, score, appearances, goals, assists, yellows, reds, player_initials):
        if date in self.games:
            print(f"Warning: Game data for {date} already exists. Overwriting.")
        game_data = {
            "Date": date,
            "Opponent": opponent,
            "Competition": competition,
            "Score": score,
            "Appearances": appearances,
            "Goals": goals,
            "Assists": assists,
            "Yellows": yellows,
            "Reds": reds
        }
        
        # Create a DataFrame for the game data
        game_df = pd.DataFrame([game_data])

        # Update season totals
        self.total_goals += goals
        self.total_assists += assists
        self.total_yellow_cards += yellows
        self.total_red_cards_35 += reds.count("35")
        self.total_red_cards_55 += reds.count("55")

        # Update player statistics based on initials
        for player_initial in player_initials:
            player = next((p for p in players if p.initials == player_initial), None)
            if player:
                player.appearances += 1
                player.goals += goals
                player.assists += assists
                player.yellow_cards += yellows.count(player_initial)
                player.red_cards += reds.count(player_initial)

        # Add the game to the season
        if date not in self.games:
            self.games[date] = game_df
        else:
            self.games[date] = pd.concat([self.games[date], game_df], ignore_index=True)

    def __str__(self):
        return f"Season Totals: Goals - {self.total_goals}, Assists - {self.total_assists}, Yellow Cards - {self.total_yellow_cards}, Red Cards (35) - {self.total_red_cards_35}, Red Cards (55) - {self.total_red_cards_55}"

# Rest of the code remains the same as in the previous example

# Create a Season object to track the season totals
season = Season()

if __name__ == "__main__":
    date = "2023-09-22"  # Change this to the date of the game
    opponent = "Opponent Team"  # Change this to the opponent's name
    competition = "League"  # Change this to the competition name
    score = "2-1"  # Change this to the game's score
    appearances = [player1.initials, player2.initials]  # List of player initials
    goals = 2
    assists = 1
    yellows = ["P1", "P2", "P1"]  # List of player initials who received yellow cards
    reds = ["P1", "P2", "P1", "P2"]  # List of player initials who received red cards

    # Record game results
    season.add_game(date, opponent, competition, score, appearances, goals, assists, yellows, reds, [player1.initials, player2.initials])

    # Print player information
    for player in players:
        print(player)

    # Print game results
    print(season)

    # Export game data to Excel
    writer = pd.ExcelWriter('football_results.xlsx', engine='xlsxwriter')
    for date, game_df in season.games.items():
        game_df.to_excel(writer, sheet_name=date, index=False)
    writer.save()
