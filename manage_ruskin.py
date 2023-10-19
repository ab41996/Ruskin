#%%
import pandas as pd
import numpy as np
from types import SimpleNamespace

"""
THINGS TO DO:
- Add fines not related to matched split by "Key" players
- Add extras such as potential kits etc
- Add G mase extras and sign up fee for start of season
- Work out how to reconcile the balances
"""


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

#%% Define player list

players = {     "ext": "External Payments",
                'refs': 'Referee Payments',
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
                'ben s': "Ben Safari"}


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
                raw_games_data.loc[raw_games_data.match_date == date, "match_data"] = input_data['player_data']
                print("new game added..")
                print(input_data)

        else:
            create_payment(date, ref_pay, players["refs"], 50, "Match Fee - "+str(opponent))
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
             players["stokes"]: {"ap":1, "g":0,"a":0},
             players["charlie"]: {"ap":1, "g":0,"a":0, "y":1},
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
             players["alex h"]:  {"ap":1, "g":0,"a":0},
             players["anand"]:   {"ap":1, "g":0,"a":1},
             players["sups"]:    {"ap":1, "g":1,"a":0, "m":1},
             players["harley"]:  {"ap":0.7, "g":0,"a":0},
             players["fred"]:    {"ap":1, "g":0,"a":0},
             players["roks"]:    {"ap":1, "g":1,"a":0},
             players["boobs"]:   {"ap":1, "g":0,"a":0},
             players["duz"]:     {"ap":1, "g":0,"a":1},
             players["bean"]:    {"ap":1, "g":0,"a":0},
             players["suds"]:    {"ap":1, "g":0,"a":0},
             players["dec"]:     {"ap":1, "g":1,"a":0, "y":1},
             players["ben s"]:   {"ap":0.5, "g":0,"a":0, "y":1}
                  })
#%% ACTUAL PAYMENT SUBMISSIONS BELOW

create_payment("2023-06-20", players["anand"], players["ext"], 100, "sign up")
create_payment("2023-08-25", players["anand"], players["ext"], 165, "sign up")
create_payment("2023-09-14", players["anand"], players["ext"], 200, "pitches")
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
create_payment("2023-10-01", players["anand"], players["ext"], 200, "pitches")
create_payment("2023-10-02", players["fred"], players["anand"], 50, "top-up")
create_payment("2023-10-02", players["suds"], players["anand"], 50, "top-up")
create_payment("2023-10-02", players["harley"], players["anand"], 13.5, "top-up")
create_payment("2023-10-03", players["stirl"], players["anand"], 30, "top-up")
create_payment("2023-10-10", players["bean"], players["anand"], 14, "match fee cash")
create_payment("2023-10-12", players["anand"], players["ext"], 100, "pitch fee")

create_payment("2023-10-17", players["boobs"], players["anand"], 50, "top-up")
create_payment("2023-10-17", players["harley"], players["anand"], 10.60, "top-up")
create_payment("2023-10-17", players["hunter"], players["anand"], 32, "top-up")
create_payment("2023-10-17", players["alex h"], players["anand"], 55, "top-up")
create_payment("2023-10-19", players["anand"], players["ext"], 100, "pitch fee")
create_payment("2023-10-19", players["anand"], players["ext"], 24, "fines")



#%% Definig generate balances function
payments = pd.json_normalize(raw_payment_data["payment_data"])
games = pd.json_normalize(raw_games_data["match_data"])

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

# %% Define get payments 
def get_payments(player):
    global payments

    cash_payments = payments[(payments['from']==player)|(payments['to']==player)]
    match_fees = games.filter(regex=f'{player}.f$|date|opponent').fillna(0)
    print(cash_payments)
    print(match_fees)

#%% get payments for a playuer
get_payments(players["anand"])

# %% generate balances and print
generate_balances()
# %%
payments
# %%
payments
# %%
games
# %%
player_balances[player_balances.index != "Anand Bhakta"].sum()

# %%
player_balances.sum()
# %%
games.filter(like='Ben Supple')
# %%
