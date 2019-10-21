import pandas as pd
import numpy as np
from datetime import datetime
import pickle as pkl

# # only run here and below
# converts a string to a set of words
def make_set(x):
    return set(str(x).split())

# split string, put in set, and then convert again to string
def split_join(x):
    x = set(x.split())
    return ' '.join(x)

# ### Candidate queries
# gets candidate queries and the sessions where those candidate queries occur
def get_sessions(df, q):
    # find indeces where the user's query is part of a query in the query log, and apply to dataframe
    df_criterion = df['q_split'].map(lambda x: q.issubset(x) and len(x) == (len(q)+1))
    qdf = df[df_criterion]
    # return searches in same session as the query, and candidate queries
    return df[df.AnonID.isin(qdf.AnonID.values)], qdf

# ### Freq(CQ)
# frequency of CQ in QL / max freq of any query in QL
def freq(CQ,frequencies):
    return frequencies.loc[CQ]

# ### Mod(CQ,q')
# num sessions q' is modified to CQ / num sessions q' appears in QL
# gets the indeces of the query in the sessions
def get_qsessions(q, sessions):
    s_criterion = sessions['q_split'].map(lambda x: x == q)
    q_sessions = sessions[s_criterion]
    return q_sessions

def mod_time(CQ, frequencies, q, sessions, q_index):
    CQ = split_join(CQ)

    mod_count = 0.0
    min_time = 0 # in seconds
    for i in q_index:
        try:
            if sessions['q_split_join'].loc[i+1] == CQ:
                mod_count += 1
            time_range = sessions['q_time'].loc[i+1] - sessions['q_time'].loc[i]
            if time_range < min_time or min_time == 0:
                min_time = time_range
        except:
            pass
    q_count = len(frequencies)

    return (mod_count / q_count), min_time

# ### Score(CQ,q')
# (Freq(CQ) + Mod(CQ,q') + Time(CQ,q')) / (1 - Min{Freq(CQ,q'), Mod(CQ,q'), Time(CQ,q'))
def score(CQ, q,frequencies, sessions, q_index):
    fr = freq(CQ,frequencies)
    mo, ti = mod_time(CQ, frequencies, q, sessions, q_index)
    return (fr + mo + ti) / (1 - min(fr, mo, ti))

# ### single function to call
# get top 5 query suggestions
def get_top_5_simple(df, frequencies, q):
    q = set(q.split(' '))

    sessions, cand = get_sessions(df, q)
    #cand = test_cand.head(500)

    q_sessions = get_qsessions(q, sessions)
    q_index = q_sessions.index

    cand['score'] = [score(row['Query'], q, frequencies, sessions, q_index) for index, row in cand.iterrows()]

    cand = cand.sort_values(by='score', ascending=False)
    # we_need drop query suggestions that are duplicates (just different arrangement of words)
    top_5 = cand.drop_duplicates(subset='q_split_join')[:5]

    return top_5['Query'].values
