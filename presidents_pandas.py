import pandas as pd
election_years = range(1788,2024,4)
candidates_dict = {year: get_election_info(year) for year in election_years}

series_list = [ pd.Series(candidate_info) for year in candidates_dict.keys() \
                    for candidate_info in candidates_dict[year] ]
        
#more efficient than appending to df individually
df = pd.concat(series_list, axis=1).transpose()
df.set_index(keys=["year", "nominee"], inplace=True)
#Format needed_votes column
df["needed_votes"] = df["needed_votes"].str.replace("at least ", "").str.replace(" electoral", "")
df["needed_votes"] = df["needed_votes"].astype("int")
#Format turnout column
df["turnout"] = df["turnout"].astype("float")
#Format party column
df["party"] = df["party"].str.replace("independent", "Independent")
df["party"] = df["party"].astype("category")
#Format home_state column
df["home_state"] = df["home_state"].astype("category")
#Format electoral_vote column
df["electoral_vote"] = df["electoral_vote"].astype("int")
#Format states_carried column
df["states_carried"] = df["states_carried"].astype("int")
#Format popular_vote column
df["popular_vote"] = df["popular_vote"].str.replace("-", "0")
df["popular_vote"] = df["popular_vote"].astype("int")
#Format percentage column
df["percentage"] = df["percentage"].str.replace("-", "0")
df["percentage"] = df["percentage"].astype("float")
#Format running_mate column
df["running_mate"] = df["running_mate"].str.replace("\'\'", "") #Get rid of quotes around italicized 'None'
df["running_mate"].fillna("None", inplace=True)
