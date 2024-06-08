#%%
from ctypes import Union
import sqlite3 as db
import pandas as pd
import numpy as np
from types import SimpleNamespace
import json
import sqlalchemy

"""
THINGS TO DO:
- Add fines not related to matched split by "Key" players
- Add extras such as potential kits etc
- Add G mase extras and sign up fee for start of season
- Work out how to reconcile the balances
- add typing from python lessons to improve coding safety


PROCESS FOR MOVING TO DB AND FAST API:
- Raw data kept in database
- New entries added to database
- Read data using pandas
- Use FastAPI to present data
- This can all be done by a jupyter notebook
- https://www.youtube.com/watch?v=qNVsQ4R9Lsg
"""



#%%



#%%


#%% Define fixed fees

pitch_fee = 96
ref_fee = 50
match_fee = pitch_fee + ref_fee

#%% create dummy payment and match data to test

payment1 = {"id": "2023-08-09-AB-EXT-50",
     "payment_data": [{
    "date": "2023-08-09",
    "from": "AB",
     "to" : "EXT",
     "amount": 50,
     "reason": "top-up"
     }]
}

game1 = {"match_date": "2023-09-01",
     "match_data" : [{"date": "2023-09-01",
         "competition": "League",
         "opponent": "Athenians",
         "score": [5,1],
         "ref_pay": "AB",
         "player_data": {
             "GM": {"ap":1, "g":0,"a":0},
             "BS": {"ap":1, "g":0,"a":0},
             "AB": {"ap":0.5, "g":0,"a":0},
             "JS": {"ap":1, "g":1,"y": 1}
                  }
         }]}

game2 = {"match_date": "2023-10-01",
     "match_data" : [{"date": "2023-09-01",
         "competition": "League",
         "opponent": "Athenians",
         "score": [5,1],
         "ref_pay": "AB",
         "player_data": {
             "JOE": {"ap":1, "g":0,"a":0},
             "JIM": {"ap":1, "g":0,"a":0},
             "JAMES": {"ap":0.5, "g":0,"a":0},
             "JARRYD": {"ap":1, "g":1,"y": 1}
                  }
         }]}

game3 = {"match_date": "2023-11-01",
     "match_data" : [{"date": "2023-11-01",
         "competition": "Cup",
         "opponent": "Athenians",
         "score": [5,1],
         "ref_pay": "AB",
         "player_data": {
             "JOE": {"ap":1, "g":0,"a":0},
             "JIM": {"ap":1, "g":0,"a":0},
             "JAMES": {"ap":0.5, "g":0,"a":0},
             "JARRYD": {"ap":1, "g":1,"y": 1}
                  }
         }]}



#%% Define player list

players = {     "ext": "External Payments",
                'refs': 'Referee Payments',
                'ruskin': 'Ruskin Club',
                'anand': "Anand Bhakta",
                'aidan': "Aidan Hughes",
                'sups': "Ben Supple",
                'roks': "Rokib Choudhury",
                'boobs': "Joe Boobier",
                'g': "George Mason",
                'suds': "James Sudweeks",
                'bean': "Ben Scrivner",
                'stirl': "Jack Stirland",
                'wints': "Max Winter",
                'duz': "Tarun Bhakta",
                'tommy': "Peter Collins",
                'hunter': "Hunter Godson", 
                'letch': "Eddie Letcher",
                'ben jones': "Ben Jones",
                'fred': "Fred Ianelli",
                'gaddes': "Jack Gaddes",
                'lex': "Alex Marsh",
                'dec': "Dec Hall" ,
                'toby': "Toby Bridges",
                'ishaq': "Sheik Ishaq",
                'mk': "Muhammad Mikaeel",
                'joe s': "Joe Shorrock",
                'josh': "Josh K?",
                'hayes': "Ben Hayes",
                'harley': "Harley Sylvester",
                'rokun': "Rokun Choudhury",
                'danny': "Danny ?",
                'max b': "Max Borland",
                'ol': "Ollie Mathieson",
                'andy': "Andy Jenkinson",
                'alex f': "Alex Ferguson",
                'alex h': "Alex Hurrel",
                'benj': "Oliver Benjamin",
                'stokes': "Jake Stokes",
                'charlie': "Charlie Hymas",
                'luke': "Luke Nutt",
                'ben s': "Ben Safari",
                'samad': "Samad",
                'holty': "Sam Holt",
                'nourdine': "Nourdine"}


#%% Generate create_payment function and raw_payment_data df

raw_payment_data = pd.DataFrame(data=None, columns=["id","payment_data"], index=[id])

def create_payment(date, frm, to, amount, reason):

    #define global variables
    global raw_payment_data
    global players

    #Check player in player list
    if frm in players.values() and to in players.values():

        #generate unique id
        id = str(date)+'-'+str(frm)+'-'+str(to)+'-'+str(amount)

        #create dict of data with id
        input_data = {"id": id,
                    "payment_data": [{
                            "date": date,
                            "from": frm,
                            "to": to,
                            "amount": amount,
                            "reason": reason
                        }]
                    }
        
        #Check for repeated payments
        if len(raw_payment_data.loc[raw_payment_data.id == id, "payment_data"])>0:
            if input(f'Do you want to overwrite {id}...(y/n)') == 'y':
                raw_payment_data.loc[raw_payment_data.id == id, "payment_data"] = input_data['payment_data']

        else:
            raw_payment_data = pd.concat([raw_payment_data, pd.DataFrame(input_data)]).reset_index(drop=True)

            print("new payment added..")
            print(input_data)
    else:
        if frm in players.values():
            raise Exception(f"INVALID PAYMENT SENDER/RECEIVER: {to}")
        else:
            raise Exception(f"INVALID PAYMENT SENDER/RECEIVER: {frm}")

#%% Define custom_bill function to generate multiple payments

def custom_bill(date, payee, recipients, amount, even_split, reason):
    #define global variables
    global raw_payment_data
    global players

    #Check player in player list
    if payee in players.values() and [recipient in players.values() for recipient in recipients]:

        #Number of players to split by
        count = len(recipients)
        to = payee

        #for loop to create each payment
        for recipient in recipients:
            if even_split:
                frm = recipient
                amnt = amount/count
                create_payment(date, frm, to, -amnt, f"Bill Split - {reason}")
            elif not even_split:
                frm = recipient[0]
                amnt = recipient[0]
                create_payment(date, frm, to, -amnt, f"Bill Split - {reason}")

#%% Define create_game function and raw_games df 

raw_games_data = pd.DataFrame(data=None, columns=["match_date", "match_data"])
raw_games_data.set_index("match_date")

def create_game(date, competition, opponent, score, ref_pay, player_data):

    #Define global variables
    global raw_games_data
    global players

    #Checking all players are valid
    if all(player in players.values() for player in player_data.keys()):

        #Generated nested data
        input_data = {"match_date": date,
        "match_data" : [{"date": date,
            "competition": competition,
            "opponent": opponent,
            "score": score,
            "ref_pay": ref_pay,
            "player_data": player_data
            }]}
        
        #define variables for for loops
        yellow_cards = 0
        goals = 0
        assists = 0
        total_apps = 0

        #calculate fines and add to match data
        for key, value in input_data["match_data"][0]["player_data"].items():
            yellow_cards += value.get("y",0)
            total_apps += value.get("ap", 0)
            goals += value.get("g", 0)
            assists += value.get("a", 0)

        #Add total fee to match data
        total_fee = match_fee + yellow_cards*12
        print(total_fee)
        for key, value in input_data["match_data"][0]["player_data"].items():
            value["f"] = round(total_fee*value.get("ap")/total_apps,4)
        
        #Print data
        print("Total Goals: " +str(goals))
        print("Total Assists: " +str(assists))
        print("Total Yellow Cards: " +str(yellow_cards))
        print("Total Match Fee: " +str(total_fee))
        print("Total Apps: " +str(total_apps))
        
        #Check for duplicate games
        if len(raw_games_data.loc[raw_games_data.match_date == date, "match_data"])>0:
            if input(f'Do you want to overwrite {date}...(y/n)') == 'y':
                create_payment(date, ref_pay, players["refs"], 50, "Match Fee - "+str(opponent))
                create_payment(date, players['ruskin'], players["ext"], pitch_fee, "Pitch Fee - "+str(opponent))
                raw_games_data.loc[raw_games_data.match_date == date, "match_data"] = input_data['player_data']
                print("new game added..")
                print(input_data)

        else:
            create_payment(date, ref_pay, players["refs"], 50, "Match Fee - "+str(opponent))
            create_payment(date, players['ruskin'], players["ext"], pitch_fee, "Pitch Fee - "+str(opponent))
            raw_games_data = pd.concat([raw_games_data, pd.DataFrame(input_data)])
            print("new game added..")
            print(input_data)

    else:
        raise Exception("INVALID PLAYER SELECTION")

# %% ACTUAL GAMES SUBMISSIONS BELOW

create_game("2023-09-05",
            "League",
            "St. Johns Deaf",
            [4,3],
            players["duz"],
            {
             players["stokes"]: {"ap":1,    "g":0,"a":0},
             players["charlie"]: {"ap":1,   "g":0,"a":0, "y":1},
             players["luke"]: {"ap":1, "g":0,"a":0},
             players["harley"]: {"ap":0.8, "g":0,"a":0, "sb":1},
             players["boobs"]: {"ap":0.8, "g":0,"a":0},             
             players["fred"]: {"ap":1, "g":0,"a":0},
             players["roks"]: {"ap":1, "g":0,"a":0},
             players["andy"]: {"ap":1, "g":2,"a":0, "m":1},
             players["dec"]: {"ap":1, "g":1,"a":0},
             players["suds"]: {"ap":1, "g":0,"a":0},
             players["alex f"]: {"ap":0.4, "g":0,"a":0},             
             players["ben s"]: {"ap":0.5, "g":0,"a":0}
                  })
#%%

create_game("2023-09-13",
            "League",
            "Aloysius",
            [5,0],
            players["g"],
            {
             players["alex h"]:  {"ap":1, "g":0,"a":0},
             players["anand"]:   {"ap":1, "g":0,"a":0},
             players["mk"]:      {"ap":1, "g":0,"a":0},
             players["sups"]:    {"ap":1, "g":0,"a":0},
             players["harley"]:  {"ap":1, "g":0,"a":0},
             players["boobs"]:   {"ap":0.6, "g":0,"a":0},             
             players["fred"]:    {"ap":1, "g":0,"a":0},
             players["roks"]:    {"ap":1, "g":1,"a":0},
             players["andy"]:    {"ap":1, "g":3,"a":0, "m": 1},
             players["dec"]:     {"ap":1, "g":1,"a":0},
             players["suds"]:    {"ap":1, "g":0,"a":0},
             players["hunter"]:  {"ap":0.4, "g":0,"a":0}
                  })

create_game("2023-09-20",
            "League",
            "Streatham FC",
            [8,2],
            players["anand"],
            {
             players["alex h"]:  {"ap":1, "g":0,"a":0},
             players["anand"]:   {"ap":1, "g":1,"a":0},
             players["mk"]:      {"ap":1, "g":1,"a":0},
             players["fred"]:    {"ap":1, "g":0,"a":0},
             players["roks"]:    {"ap":1, "g":1,"a":0},
             players["andy"]:    {"ap":1, "g":1,"a":0},
             players["duz"]:     {"ap":1, "g":1,"a":0},
             players["g"]:       {"ap":1, "g":2,"a":0, "m":1},
             players["stirl"]:   {"ap":1, "g":0,"a":0, "sb":1},
             players["hunter"]:  {"ap":1, "g":1,"a":0},
             players["benj"]:    {"ap":0.6, "g":0,"a":0}
                  })

create_game("2023-09-27",
            "League",
            "London Internationale 1s",
            [4,6],
            players["duz"],
            {
             players["alex h"]:  {"ap":1, "g":0,"a":0},
             players["anand"]:   {"ap":1, "g":0,"a":0},
             players["sups"]:    {"ap":1, "g":0,"a":0},
             players["harley"]:  {"ap":1, "g":0,"a":0},
             players["fred"]:    {"ap":1, "g":0,"a":0},
             players["roks"]:    {"ap":1, "g":1,"a":0},
             players["boobs"]:   {"ap":1, "g":0,"a":0},
             players["duz"]:     {"ap":1, "g":0,"a":1},
             players["g"]:       {"ap":1, "g":0,"a":1},
             players["stirl"]:   {"ap":0.6, "g":1,"a":0},
             players["hunter"]:  {"ap":1, "g":1,"a":1},
             players["benj"]:    {"ap":0.5, "g":0,"a":0}
                  })
                
create_game("2023-10-10",
            "Tom Keane",
            "Bonva United",
            [2,1],
            players["anand"],
            {
             players["alex h"]:  {"ap":1,   "g":0,"a":0},
             players["anand"]:   {"ap":1,   "g":0,"a":1},
             players["sups"]:    {"ap":1,   "g":1,"a":0, "m":1},
             players["harley"]:  {"ap":0.7, "g":0,"a":0},
             players["fred"]:    {"ap":1,   "g":0,"a":0},
             players["roks"]:    {"ap":1,   "g":0,"a":0},
             players["boobs"]:   {"ap":1,   "g":0,"a":0},
             players["duz"]:     {"ap":1,   "g":0,"a":1},
             players["bean"]:    {"ap":1,   "g":0,"a":0},
             players["suds"]:    {"ap":1,   "g":0,"a":0},
             players["dec"]:     {"ap":1,   "g":1,"a":0, "y":1},
             players["ben s"]:   {"ap":0.5, "g":0,"a":0, "y":1}
                  })

create_game("2023-10-24",
            "League",
            "Inter Mile End",
            [2,8],
            players["sups"],
            {
             players["anand"]:      {"ap":1,    "g":0},
             players["sups"]:       {"ap":1,    "g":0,  "a":0},
             players["g"]:          {"ap":0.7,  "g":0,  "a":0, "y":1},
             players["benj"]:       {"ap":1,    "g":0,  "a":0, "y":1},
             players["stirl"]:      {"ap":1,    "g":1,  "a":0, "y":1, "sb":1},
             players["roks"]:       {"ap":1,    "g":0,  "a":0},
             players["duz"]:        {"ap":1,    "g":0,  "a":1},
             players["mk"]:         {"ap":1,    "g":0,  "a":0},
             players["suds"]:       {"ap":1,    "g":0,  "a":0},
             players["dec"]:        {"ap":1,    "g":1,  "a":0, "y":1}
                  })

create_game("2023-11-08",
            "League",
            "HP Finchely",
            [1,2],
            players["sups"],
            {
             players["anand"]:      {"ap":1,    "g":0,          "y": 1},
             players["sups"]:       {"ap":1,    "g":0,  "a":0},
             players["g"]:          {"ap":0.7,  "g":0,  "a":1},
             players["bean"]:       {"ap":1,    "g":0,  "a":0},
             players["stirl"]:      {"ap":0.5,  "g":0,  "a":0},
             players["roks"]:       {"ap":1,    "g":0,  "a":0},
             players["boobs"]:      {"ap":1,    "g":1,  "a":0},
             players["mk"]:         {"ap":0.5,  "g":0,  "a":0},
             players["suds"]:       {"ap":1,    "g":0,  "a":0},
             players["dec"]:        {"ap":1,    "g":0,  "a":0},
             players["andy"]:       {"ap":1,    "g":0,  "a":0, "y":1},
             players["alex h"]:     {"ap":1,    "g":0,  "a":0}
                  })

create_game("2023-11-15",
            "League",
            "Drayton",
            [3,2],
            players["sups"],
            {
             players["anand"]:      {"ap":1,    "g":0},
             players["sups"]:       {"ap":1,    "g":0,  "a":1},
             players["g"]:          {"ap":1,    "g":1,  "a":2},
             players["bean"]:       {"ap":1,    "g":0,  "a":0},
             players["benj"]:       {"ap":0.3,  "g":0,  "a":0},
             players["mk"]:         {"ap":0.5,  "g":0,  "a":0},
             players["boobs"]:      {"ap":1,    "g":0,  "a":0},
             players["fred"]:       {"ap":1,    "g":0,  "a":0},
             players["suds"]:       {"ap":1,    "g":0,  "a":0, "y": 1},
             players["dec"]:        {"ap":1,    "g":0,  "a":0},
             players["andy"]:       {"ap":1,    "g":2,  "a":0, "m":1},
             players["alex h"]:     {"ap":1,    "g":0,  "a":0},
             players["toby"]:       {"ap":0.5,  "g":0,  "a":0},
             players["duz"]:        {"ap":0.6,  "g":0,  "a":0},
                  })

create_game("2023-11-29",
            "League",
            "CYP",
            [5,2],
            players["duz"],
            {
             players["anand"]:      {"ap":1,    "g":0,  "a":1},
             players["sups"]:       {"ap":1,    "g":0,  "a":1},
             players["bean"]:       {"ap":0.7,  "g":0,  "a":0},
             players["benj"]:       {"ap":0.3,  "g":0,  "a":0},
             players["mk"]:         {"ap":1,    "g":1,  "a":1},
             players["boobs"]:      {"ap":0.8,   "g":0,  "a":1},
             players["fred"]:       {"ap":1,    "g":0,  "a":0},
             players["suds"]:       {"ap":1,    "g":0,  "a":0},
             players["dec"]:        {"ap":1,    "g":2,  "a":0},
             players["andy"]:       {"ap":1,    "g":2,  "a":1, "y": 1, "m": 1},
             players["alex h"]:     {"ap":1,    "g":0,  "a":0},
             players["toby"]:       {"ap":0.4,  "g":0,  "a":0},
             players["duz"]:       {"ap":0.8,  "g":0,  "a":0},
                  })

create_game("2023-12-06", #Red Card Fred to be handled as a bill £35 + £15
            "Tom Keane",
            "St. Johns Deaf",
            [2,3],
            players["sups"],
            {
             players["anand"]:      {"ap":1},
             players["sups"]:       {"ap":1},
             players["mk"]:         {"ap":1},
             players["boobs"]:      {"ap":0.5, "a":1},
             players["fred"]:       {"ap":1},
             players["suds"]:       {"ap":1},
             players["dec"]:        {"ap":1, "g":2, "y":1},
             players["andy"]:       {"ap":1, "y":1},
             players["alex h"]:     {"ap":1},
             players["toby"]:       {"ap":1},
             players["duz"]:        {"ap":0.7},
             players["g"]:          {"ap":1},
                  })

create_game("2023-12-13",
            "League",
            "London Internationale 1s",
            [7,2],
            players["sups"],
            {
             players["anand"]:      {"ap":1,                "y":1},
             players["sups"]:       {"ap":1,        "a":1},
             players["mk"]:         {"ap":1, "g":1, "a":2},
             players["roks"]:       {"ap":1},
             players["benj"]:       {"ap":1,        "a":1},
             players["suds"]:       {"ap":1},
             players["dec"]:        {"ap":1, "g":2},
             players["andy"]:       {"ap":1,                "y":1},
             players["alex h"]:     {"ap":1},
             players["duz"]:        {"ap":1},
             players["g"]:          {"ap":1, "g":4, "a":1}
                  })

create_game("2024-01-10",
            "League",
            "Streatham",
            [3,4],
            players["sups"],
            {
             players["anand"]:      {"ap":1},
             players["sups"]:       {"ap":1,        "a":1},
             players["hunter"]:     {"ap":1, "g":1, "y":1},
             players["roks"]:       {"ap":0.3, "g":1, "a":1},
             players["bean"]:       {"ap":1},
             players["suds"]:       {"ap":1},
             players["dec"]:        {"ap":1, "g":1, "a": 1},
             players["fred"]:       {"ap":1},
             players["alex h"]:     {"ap":1},
             players["duz"]:        {"ap":1},
             players["harley"]:     {"ap":0.3},
             players["nourdine"]:   {"ap":0.5},
             players["boobs"]:      {"ap":1}
                  })

create_game("2024-01-17",
            "Cup",
            "Streatham",
            [9,3],
            players["sups"],
            {
             players["sups"]:       {"ap":1},
             players["hunter"]:     {"ap":1, "y":1},
             players["g"]:          {"ap":1, "g":1},
             players["bean"]:       {"ap":0.7},
             players["suds"]:       {"ap":1},
             players["dec"]:        {"ap":0.5, "g":6},
             players["alex h"]:     {"ap":1},
             players["duz"]:        {"ap":1},
             players["toby"]:       {"ap":0.3},
             players["stirl"]:      {"ap":1, "g":1},
             players["boobs"]:      {"ap":1, "g":1},
             players["mk"]:         {"ap":0.5},
             players["benj"]:       {"ap":1}
                  })

create_game("2024-01-30",
            "League",
            "St. Johns Deaf",
            [6,3],
            players["sups"],
            {
             players["sups"]:       {"ap":1, "y":1},
             players["hunter"]:     {"ap":1, "g":1, "a":2},
             players["g"]:          {"ap":1, "g":1},
             players["bean"]:       {"ap":0.5,"g":1, "a":1, "y":1},
             players["suds"]:       {"ap":1},
             players["anand"]:      {"ap":1},
             players["alex h"]:     {"ap":1},
             players["duz"]:        {"ap":1},
             players["stirl"]:      {"ap":1, "g":1, "a":1},
             players["mk"]:         {"ap":1, "g":2},
             players["samad"]:      {"ap":1},
             players["benj"]:       {"ap":0.5}
                  })

create_game("2024-02-06",
            "League",
            "Aloysius",
            [4,2],
            players["sups"],
            {
             players["sups"]:       {"ap":1,},
             players["g"]:          {"ap":1, "g":1, "a":1},
             players["suds"]:       {"ap":1, "m":1},
             players["anand"]:      {"ap":1},
             players["alex h"]:     {"ap":1},
             players["duz"]:        {"ap":1},
             players["stirl"]:      {"ap":1, "a":2},
             players["mk"]:         {"ap":1, "a":1},
             players["benj"]:       {"ap":0.7},
             players["dec"]:        {"ap":1, "g":3},
             players["fred"]:        {"ap":1},
             players["holty"]:      {"ap":0.3}
                  })

create_game("2024-03-07",
            "Ken Doherty",
            "Athenians",
            [4,1],
            players["anand"],
            {
             players["alex h"]:     {"ap":1},
             players["suds"]:       {"ap":1, "g":1},
             players["benj"]:       {"ap":0.75},
             players["anand"]:      {"ap":1},
             players["holty"]:      {"ap":1},
             players["samad"]:      {"ap":1},

             players["sups"]:       {"ap":1, "y":1},
             players["boobs"]:      {"ap":0.75},
             players["g"]:          {"ap":0.5},

             players["stirl"]:      {"ap":1, "g":1},
             players["mk"]:         {"ap":1, "g":1},
             players["dec"]:        {"ap":1, "y":1, "g":1}
                  })

create_game("2024-03-20",
            "Invitation Cup",
            "Spicegun",
            [3,1],
            players["anand"],
            {
             players["alex h"]:     {"ap":1},
             players["suds"]:       {"ap":1},
             players["benj"]:       {"ap":0.5, "a":1, "y":1},
             players["anand"]:      {"ap":1},
             players["fred"]:      {"ap":1},
             players["samad"]:      {"ap":1, "g":1, "y":1},

             players["duz"]:        {"ap":1},
             players["harley"]:     {"ap":0.5, "y":1},
             players["toby"]:       {"ap":1},

             players["stirl"]:      {"ap":1, "g":1},
             players["mk"]:         {"ap":1, "a":1},
             players["dec"]:        {"ap":1, "g":1}
                  })

create_game("2024-03-26", #add yellows
            "League",
            "Inter Mile End",
            [2,6],
            players["anand"],
            {
             players["alex h"]:     {"ap":1},
             players["holty"]:       {"ap":.75},
             players["benj"]:       {"ap":1},
             players["anand"]:      {"ap":1},
             players["fred"]:      {"ap":1},
             players["samad"]:      {"ap":1},

             players["duz"]:        {"ap":1},
             players["harley"]:     {"ap":0.5},
             players["alex f"]:      {"ap":.75},

             players["stirl"]:      {"ap":1, "g":2},
             players["mk"]:         {"ap":1},
             players["dec"]:        {"ap":1}
                  })

create_game("2024-04-10", #add yellows
            "League",
            "St. Johns",
            [3,6],
            players["anand"],
            {
             players["alex h"]:     {"ap":1},
             players["holty"]:       {"ap":.25},
             players["benj"]:       {"ap":1},
             players["anand"]:      {"ap":1},
             players["fred"]:      {"ap":1},
             players["suds"]:      {"ap":1},

             players["duz"]:        {"ap":.75},
             players["sups"]:     {"ap":1},
             players["toby"]:      {"ap":1, "g":1},

             players["stirl"]:      {"ap":1,},
             players["g"]:         {"ap":1, "g":1},
             players["dec"]:        {"ap":1}
                  })

create_game("2024-04-23",
            "League",
            "CYP",
            [5,2],
            players["anand"],
            {
             players["holty"]:       {"ap":1},
             players["benj"]:       {"ap":0.4},
             players["anand"]:      {"ap":1},
             players["roks"]:      {"ap":1},
             players["samad"]:      {"ap":1},
             players["suds"]:      {"ap":0.6},

             players["duz"]:        {"ap":.25},
             players["sups"]:     {"ap":.75},
             players["andy"]:      {"ap":1, "a":1},
             players["boobs"]:      {"ap":0.4},

             players["stirl"]:      {"ap":1, "g":1, "a":2},
             players["g"]:         {"ap":1, "a":1, "g":1},
             players["dec"]:        {"ap":1, "g":3, "y":1},
             players["mk"]:        {"ap":0.6}
                  })

create_game("2024-05-08", #add goals and assists
            "Invitation Cup",
            "Camden",
            [6,4],
            players["anand"],
            {
             players["alex h"]:       {"ap":1,"y":1},
             players["fred"]:       {"ap":0.2},
             players["anand"]:      {"ap":1},
             players["roks"]:      {"ap":0.8},
             players["samad"]:      {"ap":1,"y":1},
             players["suds"]:      {"ap":1},

             players["duz"]:        {"ap":0.3},
             players["sups"]:     {"ap":1},
             players["andy"]:      {"ap":0.7,"y":1},
             players["boobs"]:      {"ap":1},

             players["stirl"]:      {"ap":1, "sb":1},
             players["g"]:         {"ap":1,"y":1},
             players["dec"]:        {"ap":0.8,},
             players["hunter"]:      {"ap":0.2}
                  })

create_game("2024-05-22", #add goals and assists
            "League",
            "HP Finchley",
            [2,1],
            players["anand"],
            {
             players["holty"]:       {"ap":1},

             players["anand"]:      {"ap":1},
             players["roks"]:      {"ap":1,"y":1},
             players["samad"]:      {"ap":1},
             players["benj"]:      {"ap":0.7,"y":1},
             players["suds"]:      {"ap":0.3},
             players["fred"]:      {"ap":0.3},

             players["duz"]:        {"ap":1},
             players["sups"]:     {"ap":1},
             players["toby"]:      {"ap":1,},

             players["stirl"]:      {"ap":1, "sb":1, "y":1}, #adding yellow for fine
             players["mk"]:         {"ap":1},
             players["dec"]:        {"ap":0.8,"g":2},
             players["hunter"]:     {"ap":0.2,},
                  })

create_game("2024-05-30", #add goals and assists
            "League",
            "Camden",
            [2,1],
            players["anand"],
            {
             players["holty"]:       {"ap":1},

             players["anand"]:      {"ap":1},
             players["roks"]:      {"ap":1},
             players["samad"]:      {"ap":1},
             players["benj"]:      {"ap":0.7},
             players["fred"]:      {"ap":1},

             players["duz"]:        {"ap":1},
             players["sups"]:     {"ap":1, "y":1},
             players["toby"]:      {"ap":0.3},
             players["boobs"]:      {"ap":0.7,},
             players["andy"]:      {"ap":1, "y":1},

             players["stirl"]:      {"ap":1, "y":1},
             players["mk"]:         {"ap":1},
             players["dec"]:        {"ap":0.8,},
             players["hunter"]:     {"ap":0.2,},
                  })

                
#%% ACTUAL PAYMENT SUBMISSIONS BELOW

custom_bill("2023-06-10", players["g"], 
                            [players['aidan'],
                            players['roks'],
                            players['boobs'],
                            players['g'],
                            players['suds'],
                            players['stirl'],
                            players['duz'],
                            players['tommy'],
                            players['hunter'],
                            players['letch'],
                            players['ben jones'],
                            players['dec'],
                            players['toby'],
                            players['mk'],
                            players['joe s'],
                            players['harley']], 70, True, "End of Season Meal")
create_payment("2023-06-20", players["ext"], players["ruskin"], 129.15, "rolled over")
create_payment("2023-06-20", players["anand"], players["ruskin"], 100, "NO INVOICE: Annual Subscription")
create_payment("2023-06-20", players["ruskin"], players["ext"], 100, "Annual Subscription")
create_payment("2023-06-20", players["ext"], players["ruskin"], 50, "Raffle")
create_payment("2023-08-25", players["anand"], players["ruskin"], 165, "INVOICE(17/08/23): pitch fee + fines")
create_payment("2023-08-25", players["ruskin"], players["ext"], 65, "fines")
create_payment("2023-09-14", players["anand"], players["ruskin"], 200, "INVOICE(04/09/23): pitch fee")
create_payment("2023-09-14", players["fred"], players["anand"], 50, "top-up")
create_payment("2023-09-14", players["dec"], players["anand"], 50, "top-up")
create_payment("2023-09-14", players["stirl"], players["anand"], 50, "top-up")
create_payment("2023-09-14", players["roks"], players["anand"], 50, "top-up")
create_payment("2023-09-14", players["harley"], players["anand"], 25, "top-up")
create_payment("2023-09-18", players["suds"], players["anand"], 50, "top-up")
create_payment("2023-09-21", players["andy"], players["anand"], 50, "top-up")
create_payment("2023-09-21", players["boobs"], players["anand"], 50, "top-up")
create_payment("2023-09-25", players["anand"], players["ext"], 12, "fine")
create_payment("2023-09-25", players["sups"], players["anand"], 50, "top-up")
create_payment("2023-09-27", players["sups"], players["anand"], 50, "top-up")
create_payment("2023-10-01", players["anand"], players["ruskin"], 200, "INVOICE(18/09/23): pitch fee")
create_payment("2023-10-02", players["fred"], players["anand"], 50, "top-up")
create_payment("2023-10-02", players["suds"], players["anand"], 50, "top-up")
create_payment("2023-10-02", players["harley"], players["anand"], 13.5, "top-up")
create_payment("2023-10-03", players["stirl"], players["anand"], 30, "top-up")
create_payment("2023-10-10", players["bean"], players["anand"], 14, "match fee cash")
create_payment("2023-10-12", players["anand"], players["ruskin"], 100, "INVOICE(02/10/23): pitch fee")
create_payment("2023-10-17", players["boobs"], players["anand"], 50, "top-up")
create_payment("2023-10-17", players["harley"], players["anand"], 10.60, "top-up")
create_payment("2023-10-17", players["hunter"], players["anand"], 32, "top-up")
create_payment("2023-10-17", players["alex h"], players["anand"], 55, "top-up")
create_payment("2023-10-19", players["anand"], players["ruskin"], 100, "INVOICE(16/10/23): pitch fee")
create_payment("2023-10-19", players["anand"], players["ext"], 24, "fines")
create_payment("2023-10-27", players["sups"], players["anand"], 50, "top-up")
create_payment("2023-11-01", players["suds"], players["anand"], 50, "top-up")
create_payment("2023-11-01", players["alex h"], players["anand"], 50, "top-up")
create_payment("2023-11-02", players["anand"], players["sups"], 50, "returning money")
create_payment("2023-11-03", players["stirl"], players["anand"], 30, "top-up")
create_payment("2023-11-06", players["andy"], players["anand"], 50, "top-up")
create_payment("2023-11-07", players["roks"], players["anand"], 100, "top-up")
create_payment("2023-11-08", players["bean"], players["anand"], 15, "top-up")
create_payment("2023-11-09", players["benj"], players["anand"], 50, "top-up")
custom_bill("2023-11-09", players["roks"], 
                            [players['andy'],
                            players['roks'],
                            players['boobs'],
                            players['g'],
                            players['suds'],
                            players['stirl'],
                            players['duz'],
                            players['dec'],
                            players['fred'],
                            players['bean'],
                            players['alex h'],
                            players['benj'],
                            players['mk'],
                            players['harley'],
                            players['anand'],
                            players['sups'],
                            ], 38, True, "New Socks and Shorts")
create_payment("2023-11-09", players["dec"], players["sups"], 50, "match fees")
create_payment("2023-11-16", players["bean"], players["anand"], 15, "top-up")
create_payment("2023-11-16", players["anand"], players["ruskin"], 240, "INVOICE(06/11/23): pitch fee")
create_payment("2023-11-16", players["anand"], players["ext"], 24, "fine")
create_payment("2023-11-18", players["anand"], players["sups"], 50, "payback")
create_payment("2023-11-20", players["duz"], players["anand"], 50, "top-up")
create_payment("2023-11-20", players["g"], players["anand"], 50, "top-up")
create_payment("2023-11-21", players["letch"], players["anand"], 4, "top-up")
create_payment("2023-11-27", players["sups"], players["anand"], 50, "top-up")
custom_bill("2023-11-20", players["anand"], 
                            [players['andy'],
                            players['roks'],
                            players['boobs'],
                            players['g'],
                            players['suds'],
                            players['stirl'],
                            players['duz'],
                            players['dec'],
                            players['fred'],
                            players['bean'],
                            players['alex h'],
                            players['benj'],
                            players['mk'],
                            players['harley'],
                            players['anand'],
                            players['sups'],
                            ], 10, True, "Club Fine - Missed Match Report[PART OF INVOICE]")
create_payment("2023-11-28", players["anand"], players["ruskin"], 120, "INVOICE(20/11/23): pitch fee")
create_payment("2023-12-01", players["alex h"], players["anand"], 50, "top-up")
create_payment("2023-12-01", players["suds"], players["anand"], 50, "top-up")
create_payment("2023-12-04", players["anand"], players["ext"], 12, "fines CYP 1 yellow")
create_payment("2023-12-04", players["dec"], players["sups"], 100, "top-up")
create_payment("2023-12-05", players["sups"], players["anand"], 100, "top-up")
custom_bill("2023-12-05", players["anand"], 
                            [players['andy'],
                            players['roks'],
                            players['boobs'],
                            players['g'],
                            players['suds'],
                            players['stirl'],
                            players['duz'],
                            players['dec'],
                            players['fred'],
                            players['bean'],
                            players['alex h'],
                            players['benj'],
                            players['mk'],
                            players['harley'],
                            players['anand'],
                            players['sups'],
                            ], 15, True, "Club Fine - Missed Match Report/Inappropriate dress[PART OF INVOICE]")
create_payment("2023-12-05", players["anand"], players["ruskin"], 140, "INVOICE(04/12/23): pitch fee")
create_payment("2023-12-05", players["fred"], players["anand"], 50, "top-up")
create_payment("2023-12-11", players["anand"], players["sups"], 50, "match repay")
custom_bill("2023-12-20", players["anand"], 
                            [players["anand"],
                            players["sups"],
                            players["mk"],
                            players["boobs"],
                            players["fred"],
                            players["suds"],
                            players["dec"],
                            players["andy"],
                            players["alex h"],
                            players["toby"],
                            players["duz"],
                            players["g"]
                            ], 35, True, "Fred Red Card vs St. Johns")
custom_bill("2023-12-20", players["anand"], 
                            [
                            players["fred"]
                            ], 15, True, "Fred Red Card vs St. Johns. Misconduct claim")
create_payment("2023-12-20", players["anand"], players["ext"], 83+15, "fines")
create_payment("2023-12-20", players["toby"], players["sups"], 35, "top-up")
create_payment("2023-12-20", players["anand"], players["sups"], 15, "repay")
create_payment("2023-12-20", players["boobs"], players["anand"], 50, "top-up")
create_payment("2023-12-20", players["benj"], players["anand"], 50, "top-up")
create_payment("2023-12-27", players["sups"], players["anand"], 50, "top-up")
create_payment("2024-01-02", players["suds"], players["anand"], 50, "top-up")
create_payment("2024-01-02", players["alex h"], players["anand"], 50, "top-up")
create_payment("2024-01-08", players["anand"], players["ruskin"], 150, "pitches")
custom_bill("2023-01-21", players["anand"], 
                            [players["fred"]
                            ], 35, True, "Fred Red Card vs St. Johns 2.0 Misconduct fee")
create_payment("2024-01-22", players["fred"], players["anand"], 35, "red card top-up")
create_payment("2024-01-22", players["anand"], players["ext"], 12, "streatham yellow card 47 fee - 35 custom bill for red card")
create_payment("2024-01-29", players["sups"], players["anand"], 50, "top-up")
create_payment("2024-01-29", players["anand"], players["sups"], 100, "repay")
create_payment("2024-01-29", players["bean"], players["anand"], 50, "top-up")
create_payment("2024-02-01", players["alex h"], players["anand"], 50, "top-up")
create_payment("2024-02-01", players["suds"], players["anand"], 50, "top-up")
create_payment("2024-02-01", players["anand"], players["ext"], 36, "fines")
create_payment("2024-02-01", players["anand"], players["ruskin"], 105, "match fees")
create_payment("2024-02-05", players["andy"], players["anand"], 23.1, "top-up")
create_payment("2024-02-07", players["benj"], players["anand"], 50, "top-up")
create_payment("2024-02-14", players["hunter"], players["anand"], 50, "top-up")
create_payment("2024-02-19", players["anand"], players["ruskin"], 200, "match fees")
create_payment("2024-02-27", players["sups"], players["anand"], 50, "top-up")
create_payment("2024-03-01", players["suds"], players["anand"], 50, "top-up")
create_payment("2024-03-01", players["alex h"], players["anand"], 50, "top-up")
create_payment("2024-03-05", players["anand"], players["ruskin"], 95, "match fees")
custom_bill("2024-03-01", players["ruskin"], 
                            [players['roks'],
                            players['boobs'],
                            players['g'],
                            players['suds'],
                            players['stirl'],
                            players['duz'],
                            players['dec'],
                            players['fred'],
                            players['alex h'],
                            players['benj'],
                            players['mk'],
                            players['anand'],
                            players['sups'],
                            players['holty'],
                            ], pitch_fee, True, "Missed cup match due to team bailing[PART OF INVOICE]")
create_payment("2024-03-20", players["anand"], players["ext"], 24, "fines")
create_payment("2024-03-20", players["anand"], players["ruskin"], 188.55, "INVOICE: 2024-03-18")
create_payment("2024-03-21", players["stirl"], players["anand"], 40, "top-up")
create_payment("2024-03-22", players["fred"], players["anand"], 50, "top-up")
create_payment("2024-03-23", players["dec"], players["anand"], 50, "top-up")
create_payment("2024-03-24", players["holty"], players["anand"], 30, "top-up")
create_payment("2024-03-27", players["sups"], players["anand"], 50, "top-up")
create_payment("2024-03-27", players["anand"], players["ext"], 36, "fines")
create_payment("2024-04-02", players["suds"], players["anand"], 50, "top-up")
create_payment("2024-04-10", players["anand"], players["ruskin"], 207.35, "INVOICE: 2024-04-04")
custom_bill("2024-04-10", players["ruskin"], 
                            [players['roks'],
                            players['boobs'],
                            players['g'],
                            players['suds'],
                            players['stirl'],
                            players['duz'],
                            players['dec'],
                            players['fred'],
                            players['alex h'],
                            players['benj'],
                            players['mk'],
                            players['anand'],
                            players['sups'],
                            players['holty'],
                            players['andy']
                            ], 102, True, "Fines for bad admin INVOICE: 2024-04-04")
create_payment("2024-04-12", players["toby"], players["sups"], 36.34, "top-up")
create_payment("2024-04-12", players["fred"], players["anand"], 20, "top-up")
create_payment("2024-04-13", players["stirl"], players["anand"], 20, "top-up")
create_payment("2024-04-19", players["alex f"], players["anand"], 19, "top-up")
create_payment("2024-04-19", players["duz"], players["anand"], 50, "top-up")
create_payment("2024-04-24", players["holty"], players["anand"], 16.55, "top-up")
create_payment("2024-04-29", players["sups"], players["anand"], 50, "top-up")
create_payment("2024-05-01", players["suds"], players["anand"], 50, "top-up")
create_payment("2024-05-12", players["anand"], players["ext"], 15, "fines")
create_payment("2024-05-16", players["anand"], players["ext"], 48, "fines")
create_payment("2024-05-20", players["anand"], players["ext"], 5, "fines")
create_payment("2024-05-20", players["anand"], players["sups"], 250, "pay-back")
custom_bill("2024-06-08", players["anand"], 
                            [players['roks'],
                            players['boobs'],
                            players['g'],
                            players['suds'],
                            players['stirl'],
                            players['duz'],
                            players['dec'],
                            players['fred'],
                            players['alex h'],
                            players['benj'],
                            players['mk'],
                            players['anand'],
                            players['sups'],
                            players['holty'],
                            players['andy']
                            ], 15, True, "New balls")
custom_bill("2024-06-08", players["anand"], 
                            [players['roks'],
                            players['boobs'],
                            players['g'],
                            players['suds'],
                            players['stirl'],
                            players['duz'],
                            players['dec'],
                            players['fred'],
                            players['alex h'],
                            players['benj'],
                            players['mk'],
                            players['anand'],
                            players['sups'],
                            players['holty'],
                            players['andy']
                            ], 15, True, "Sin bins")
create_payment("2024-06-08", players["anand"], players["ext"], 81, "fines")

#ADD PAYMENTS FROM TOBY AND BEN J TO SUPS




#ADD ADHOC BILL FOR £8 FOR SUPS CASH WITHDRAWALS
#%% Definig generate balances function
payments = pd.json_normalize(raw_payment_data["payment_data"]) # type: ignore
games = pd.json_normalize(raw_games_data["match_data"]) # type: ignore

def generate_balances():
    #defining global variables
    global raw_payment_data
    global raw_games_data
    global payments
    global games
    global player_balances

    #Generating list of payments from and to players
    player_pay_from = payments.rename(columns={"from": "player", "amount": "amount"}).groupby("player").sum("amount")
    player_pay_to = payments.rename(columns={"to": "player", "amount": "amount"}).groupby("player").sum("amount")
    player_balances = player_pay_from.join(player_pay_to, lsuffix='_from', rsuffix='_to').fillna(0)

    #creating games dataframe and generating total match fees with fines
    player_match_fee_totals = games.filter(regex='f$').sum().reset_index().rename(columns={'index':'player', 0:'match_fees'})
    player_match_fee_totals['player'] = player_match_fee_totals["player"].apply(lambda x: x.split('.')[1])
    player_match_fee_totals = player_match_fee_totals.groupby("player").sum("match_fees")

    #Creating final balances
    player_balances = player_balances.merge(player_match_fee_totals,on='player', how='outer').fillna(0)
    player_balances['balance'] = player_balances['amount_from']-player_balances['amount_to']-player_balances['match_fees']
    print(player_balances)
    return player_balances

# %% Define get payments 
def get_payments(player) -> tuple:
    cash_payments = payments[(payments['from']==player)|(payments['to']==player)].to_json()
    match_fees = games.filter(regex=f'{player}.f$|date|opponent').fillna(0).to_json()
    print(cash_payments)
    print(match_fees)
    return cash_payments, match_fees

#%% get payments for a player
get_payments(players["dec"])

# %% generate balances and print
balances = generate_balances()

#%%
balances['balance'].sum()

player_balances = balances[~balances.index.isin(["Ruskin Club", "External Payments"])]
player_balances['balance'].sum()
# %%
payments
# %%
games
#%%
#%% Creating sqlite database ______________________________
#==================================================FUCNTIONing CODE==================================================================================================================================
#Create a database to store the pandas dataframes
conn = db.connect('ruskin.db')
cn = conn.cursor()

#%% convert json data to string first
raw_payment_data['payment_data'] = raw_payment_data['payment_data'].astype(str)
raw_games_data['match_data'] = raw_games_data['match_data'].astype(str)

#%% create sql tables for raw data pulls
raw_payment_data.to_sql('raw_payments_data', conn, if_exists="replace", dtype={"payment_data": 'JSON'} )
raw_games_data.to_sql('raw_games_data', conn, if_exists="replace", dtype={"games_data": 'JSON'} )

#%%
raw_payment_data.to_sql('raw_payments_data', conn, if_exists="replace", dtype={"payment_data": 'JSON'} )
raw_games_data.to_sql('raw_games_data', conn, if_exists="replace", dtype={"games_data": 'JSON'} )

#%% Generate FastAPI Server
from fastapi import FastAPI, status
from fastapi.params import Body
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
#%%
app = FastAPI()

#%% Define some classes

class User(BaseModel):
    name: str

class Payments(BaseModel): #Add user mode to this somehow
    cash_payments: str
    match_fees: str
    


#%% create home page endpoint
@app.get('/', response_class=PlainTextResponse)
def home():
    return "Welcome to Ruskin Park Rovers"

#%% create get_payments endpoint PYDANTIC WAY?
# @app.get('/payments/{player}', response_class=Payments)
# def show_payments(player): # type: ignore
#     cash_payments, match_fees = get_payments(players[f"{player}"])
#     payment = Payments(cash_payments=cash_payments, match_fees=match_fees)
#     return payment

#%% Create get_payments endpoint
@app.get('/payments/{player}', response_class=JSONResponse)
def show_payments(player):
    cash_payments, match_fees = get_payments(players[f"{player}"])
    return {"Cash Payment": cash_payments, "Match Fees": match_fees}

#%% create generate balances endpoint


#=========================================================FUCNTIONing CODE===========================================================================================================================
#%% validate table creation

# cn.execute("SELECT name from sqlite_master where type ='table';")
# print(cn.fetchall())

# #%%


# #%%
# print(game2["match_date"])
# print(game2["match_data"])


# #%%
# cn.execute(f"INSERT INTO games VALUES (2, '{game1['match_date']}', 'hi')")
# #%%
# data1 = game2['match_data']
# json_data1 = json.dumps(data1)
# binary_data1 = bytes(json_data1, 'utf-8')

# cn.execute("INSERT INTO games (match_data) VALUES (?)", (json_data1,))

# #%%
# #%%

# data1 = game2['match_data']
# json_data1 = json.dumps(data1)
# binary_data1 = bytes(json_data1, 'utf-8')

# data2 = game3['match_data']
# json_data2 = json.dumps(data2)
# binary_data2 = bytes(json_data2, 'utf-8')


# input = [(5, game1['match_date'], json_data1),
#          (6, game2['match_date'], json_data2)
#          ]
# cn.executemany("INSERT INTO games VALUES (?,?,?)", input)

# #%%

# cn.execute("SELECT * FROM games;")
# print(cn.fetchall())

# #%%
# conn.commit()
# cn.close()
# conn.close()
