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


#%% CREATE DUMMY DATA TO GET THE BALL ROLLING

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



create_payment("2023-09-27", "AB", "TB", 50, "Top-Up")








# %%
