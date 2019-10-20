
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from datetime import datetime


# # only run here and below

# In[1]:


# converts a string to a set of words
def make_set(x):
    return set(str(x).split())

# split string, put in set, and then convert again to string
def split_join(x):
    x = set(x.split())
    return ' '.join(x)


# ### Candidate queries

# In[2]:


# gets candidate queries and the sessions where those candidate queries occur
def get_sessions(df, q):
    # find indeces where the user's query is part of a query in the query log, and apply to dataframe
    df_criterion = df['q_split'].map(lambda x: q.issubset(x) and len(x) == (len(q)+1))
    qdf = df[df_criterion]
    # return searches in same session as the query, and candidate queries
    return df[df.AnonID.isin(qdf.AnonID.values)], qdf


# ### Freq(CQ)
# frequency of CQ in QL / max freq of any query in QL

# In[36]:


def freq(CQ,frequencies):
    return frequencies.loc[CQ]


# ### Mod(CQ,q')
# num sessions q' is modified to CQ / num sessions q' appears in QL

# In[4]:


# gets the indeces of the query in the sessions
def get_qsessions(q, sessions):
    s_criterion = sessions['q_split'].map(lambda x: x == q)
    q_sessions = sessions[s_criterion]
    return q_sessions


# In[5]:


def mod(CQ, frequencies, q, sessions):

    # split candidate string, put in set, and then convert to string
    CQ = split_join(CQ)

    # get the indeces of the query in the sessions
    q_sessions = get_qsessions(q, sessions)
    q_index = q_sessions.index

    # num sessions q' is modified to CQ
    # TODO: per-session instead
    mod_count = 0
    for i in q_index:
        if sessions['q_split_join'].loc[i+1]  == CQ:
            mod_count += 1
    q_count = len(frequencies)

    return mod_count / q_count


# ### Time(CQ,q')
# min diff between times of q' and CQ in sessions / length of longest session in QL

# In[6]:


def time(CQ, q, sessions):
    CQ = split_join(CQ)
    q_sessions = get_qsessions(q, sessions)
    q_index = q_sessions.index
    min_time = 0 # in seconds
    for i in q_index:
        if sessions['q_split_join'].loc[i+1]  == CQ:
            time_range = sessions['q_time'].loc[i+1] - sessions['q_time'].loc[i]
            if time_range < min_time or min_time == 0:
                min_time = time_range
    return min_time


# ### Score(CQ,q')
# (Freq(CQ) + Mod(CQ,q') + Time(CQ,q')) / (1 - Min{Freq(CQ,q'), Mod(CQ,q'), Time(CQ,q'))

# In[39]:


def score(CQ, q,frequencies, sessions):
    #print(type(CQ))
    fr = freq(CQ,frequencies)
    mo = mod(CQ, frequencies, q, sessions)
    ti = time(CQ, q, sessions)
    return (fr + mo + ti) / (1 - min(fr, mo, ti))


# ### import data

# In[8]:


import pandas as pd
import numpy as np
import pickle as pkl


# In[9]:


#pkl_file = open('suggestions_df.pkl', 'rb')
#df = pkl.load(pkl_file)
#pkl_file.close()
#df.head()


# In[10]:


#pkl_file_2 = open('frequencies.pkl', 'rb')
#frequencies = pkl.load(pkl_file_2)
#pkl_file_2.close()


# ### single function to call

# In[40]:


# get top 5 query suggestions
def get_top_5_simple(df, frequencies, q):

    q = set(q.split(' '))
    sessions, cand = get_sessions(df, q)

    #cand['score'] = cand['Query'].map(lambda x: score(x, q, frequencies, sessions))
    cand['score'] = [score(row['Query'], q, frequencies, sessions) for index, row in cand.iterrows()]

    cand = cand.sort_values(by='score', ascending=False)
    # drop query suggestions that are duplicates (just different arrangement of words)
    top_5 = cand.drop_duplicates(subset='q_split_join')[:5]

    return top_5['Query'].values


# In[43]:


#query = 'make money'
#top5 = get_top_5_simple(df, frequencies, query)
#top5
