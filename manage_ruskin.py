#%%
import pandas as pd
import numpy as np

"""
THINGS TO DO:
- make payments split across everyone by doing matched fee / total apps * apps
- create balances for players
- don't allow submission of player data if they aren't in a list of players
"""


#%% CREATE DUMMY DATA TO GET THE BALL ROLLING

pitch_fee = 96
ref_fee = 50
match_fee = pitch_fee + ref_fee



p = {"id": "2023-08-09-AB-EXT-50",
     "payment_data": [{
    "date": "2023-08-09",
    "from": "AB",
     "to" : "EXT",
     "amount": 50,
     "reason": "top-up"
     }]
}

raw_payment_data = pd.DataFrame(data=p, columns=["id","payment_data"], index=[id])




#%%

def create_payment(date, frm, to, amount, reason):

    global raw_payment_data
    id = str(date)+'-'+str(frm)+'-'+str(to)+'-'+str(amount)

    input_data = {"id": id,
                  "payment_data": [{
                        "date": date,
                        "from": frm,
                        "to": to,
                        "amount": amount,
                        "reason": reason
                    }]
                 }
    if len(raw_payment_data.loc[raw_payment_data.id == id, "payment_data"])>0:
        if input(f'Do you want to overwrite {id}...(y/n)') == 'y':
            raw_payment_data.loc[raw_payment_data.id == id, "payment_data"] = input_data['payment_data']

    else:
        raw_payment_data = pd.concat([raw_payment_data, pd.DataFrame(input_data)])

        print("new payment added..")
        print(input_data)
    
#%%

create_payment("2023-09-27", "AB", "TB", 50, "top-up")

#%% CREATE DUMMY DATA TO GET THE BALL ROLLING

d = {"match_date": "2023-09-01",
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

raw_games_data = pd.DataFrame(data=d, columns=["match_date", "match_data"])
raw_games_data.set_index("match_date")


#%% DEFINE FUNCTION TO ADD DATA TO RAW GAMES DATA

def create_game(date, competition, opponent, score, ref_pay, player_data):

    global raw_games_data

    input_data = {"match_date": date,
     "match_data" : [{"date": date,
         "competition": competition,
         "opponent": opponent,
         "score": score,
         "ref_pay": ref_pay,
         "player_data": player_data
         }]}
    
    if len(raw_games_data.loc[raw_games_data.match_date == date, "match_data"])>0:
        if input(f'Do you want to overwrite {date}...(y/n)') == 'y':
            raw_games_data.loc[raw_games_data.match_date == date, "match_data"] = input_data['player_data']
            create_payment(date, ref_pay, "REFS", 50, "Match Fee - "+str(opponent))

    else:
        raw_games_data = pd.concat([raw_games_data, pd.DataFrame(input_data)])
        create_payment(date, ref_pay, "REFS", 50, "Match Fee - "+str(opponent))
        print("new game added..")
        print(input_data)


#%% TEST OUT ADDING DATA TO RAW GAMES DATA

create_game("2023-09-08",
            "League",
            "Wood Lane",
            [5-1],
            "AB",
            {
             "GM": {"ap":1, "g":0,"a":0},
             "BS": {"ap":1, "g":0,"a":0},
             "AB": {"ap":0.5, "g":0,"a":0},
             "JS": {"ap":1, "g":1,"y": 1}
                  })


raw_games_data




players_list = ['anand',
                'aidan',
                'sups',
                'roks',
                'boobs',
                'g',
                'suds',
                'bean',
                'stirl',
                'wints',
                'duz',
                'tommy',
                'hunter', 
                'letch',
                'ben jones',
                'fred',
                'gaddes',
                'lex',
                'dec' ,
                'toby',
                'ishaq',
                'mk',
                'joe s',
                'josh',
                'hayes',
                'harley',
                'rokun',
                'danny',
                'max b',
                'ol',
                'andy',
                'alex f',
                'alex h',
                'benj',
                'stokes',
                'charlie',
                'luke',
                'ben s']






# %% ACTUAL GAMES SUBMISSIONS BELOW

create_game("2023-09-05",
            "League",
            "St. Johns Deaf",
            [4,3],
            "duz",
            {
             "stokes": {"ap":1, "g":0,"a":0},
             "charlie": {"ap":1, "g":0,"a":0, "y":1},
             "luke": {"ap":1, "g":0,"a":0},
             "harley": {"ap":0.8, "g":0,"a":0, "sb":1},
             "boobs": {"ap":0.8, "g":0,"a":0},             
             "fred": {"ap":1, "g":0,"a":0},
             "roks": {"ap":1, "g":0,"a":0},
             "andy": {"ap":1, "g":2,"a":0, "m":1},
             "dec": {"ap":1, "g":1,"a":0},
             "suds": {"ap":1, "g":0,"a":0},
             "alex f": {"ap":0.4, "g":0,"a":0},             
             "ben s": {"ap":0.5, "g":0,"a":0}
                  })

create_game("2023-09-13",
            "League",
            "Aloysius",
            [5,0],
            "g",
            {
             "alex h":  {"ap":1, "g":0,"a":0},
             "anand":   {"ap":1, "g":0,"a":0},
             "mk":      {"ap":1, "g":0,"a":0},
             "sups":    {"ap":1, "g":0,"a":0},
             "harley":  {"ap":1, "g":0,"a":0},
             "boobs":   {"ap":0.6, "g":0,"a":0},             
             "fred":    {"ap":1, "g":0,"a":0},
             "roks":    {"ap":1, "g":1,"a":0},
             "andy":    {"ap":1, "g":3,"a":0, "m": 1},
             "dec":     {"ap":1, "g":1,"a":0},
             "suds":    {"ap":1, "g":0,"a":0},
             "hunter":  {"ap":0.4, "g":0,"a":0}
                  })

create_game("2023-09-20",
            "League",
            "Streatham FC",
            [8,2],
            "anand",
            {
             "alex h":  {"ap":1, "g":0,"a":0},
             "anand":   {"ap":1, "g":1,"a":0},
             "mk":      {"ap":1, "g":1,"a":0},
             "fred":    {"ap":1, "g":0,"a":0},
             "roks":    {"ap":1, "g":1,"a":0},
             "andy":    {"ap":1, "g":1,"a":0},
             "duz":     {"ap":1, "g":1,"a":0},
             "g":       {"ap":1, "g":2,"a":0, "m":1},
             "stirl":   {"ap":1, "g":0,"a":0, "sb":1},
             "hunter":  {"ap":1, "g":1,"a":0},
             "benj":    {"ap":0.6, "g":0,"a":0}
                  })

create_game("2023-09-27",
            "League",
            "London Internationale 1s",
            [4,6],
            "duz",
            {
             "alex h":  {"ap":1, "g":0,"a":0},
             "anand":   {"ap":1, "g":0,"a":0},
             "sups":    {"ap":1, "g":0,"a":0},
             "harley":  {"ap":1, "g":0,"a":0},
             "fred":    {"ap":1, "g":0,"a":0},
             "roks":    {"ap":1, "g":1,"a":0},
             "boobs":   {"ap":1, "g":0,"a":0},
             "duz":     {"ap":1, "g":0,"a":1},
             "g":       {"ap":1, "g":0,"a":1},
             "stirl":   {"ap":0.6, "g":1,"a":0},
             "hunter":  {"ap":1, "g":1,"a":1},
             "benj":    {"ap":0.5, "g":0,"a":0}
                  })
                
create_game("2023-10-10",
            "Tom Keane",
            "Bonva United",
            [2,1],
            "anand",
            {
             "alex h":  {"ap":1, "g":0,"a":0},
             "anand":   {"ap":1, "g":0,"a":1},
             "sups":    {"ap":1, "g":1,"a":0},
             "harley":  {"ap":0.7, "g":0,"a":0, "y":1}, #check the yellow on this
             "fred":    {"ap":1, "g":0,"a":0},
             "roks":    {"ap":1, "g":1,"a":0},
             "boobs":   {"ap":1, "g":0,"a":0},
             "duz":     {"ap":1, "g":0,"a":1},
             "bean":    {"ap":1, "g":0,"a":0},
             "suds":    {"ap":1, "g":0,"a":0},
             "dec":     {"ap":1, "g":1,"a":0},
             "ben s":   {"ap":0.5, "g":0,"a":0, "m":1, "y":1}
                  })

create_payment("2023-06-20", "anand", "ext", 100, "sign up")
create_payment("2023-08-25", "anand", "ext", 165, "sign up")
create_payment("2023-09-14", "anand", "ext", 200, "pitches")
create_payment("2023-09-14", "fred", "anand", 50, "top-up")
create_payment("2023-09-14", "dec", "anand", 50, "top-up")
create_payment("2023-09-14", "stirl", "anand", 50, "top-up")
create_payment("2023-09-14", "roks", "anand", 50, "top-up")
create_payment("2023-09-14", "harley", "anand", 25, "top-up")
create_payment("2023-09-18", "suds", "anand", 50, "top-up")
create_payment("2023-09-21", "andy", "anand", 50, "top-up")
create_payment("2023-09-21", "boobs", "anand", 50, "top-up")
create_payment("2023-09-25", "anand", "ext", 12, "fine")
create_payment("2023-09-25", "sups", "anand", 50, "top-up")
create_payment("2023-09-27", "sups", "anand", 50, "top-up")
create_payment("2023-10-02", "anand", "ext", 200, "pitches")
create_payment("2023-10-02", "fred", "anand", 50, "top-up")
create_payment("2023-10-02", "harley", "anand", 13.5, "top-up")
create_payment("2023-10-03", "stirl", "anand", 30, "top-up")
create_payment("2023-10-10", "bean", "anand", 14, "match fee cash")

#%%


# %%
result = pd.json_normalize(raw_payment_data["payment_data"], ["date", "from", "to", "amount", "reason"])
result
# %%
