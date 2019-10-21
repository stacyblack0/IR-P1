#!/usr/bin/env python
# coding: utf-8

# In[20]:


import pandas as pd
import pickle as pkl
import numpy as np
from scipy import sparse as sps
from scipy import sparse
from sklearn.preprocessing import normalize
from sklearn.feature_extraction.text import TfidfVectorizer


# In[3]:


proc = pd.read_csv('Final_proc.csv')


# In[7]:


def tf_idf(data_table, col_name):
    corpus_list = []
    for item in data_table[col_name]:
        corpus_list.append(item)
    tfidf_matrix = TfidfVectorizer().fit_transform(corpus_list)
    return tfidf_matrix


# In[5]:


#proc_sample = proc.sample(frac = .0001)


# In[6]:


#proc_sample.head()


# In[ ]:


a = tf_idf(proc, 'processed_content')
pkl.dump(a, 'tf_idf.pkl')


# In[ ]:




