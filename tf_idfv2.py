#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import pickle as pkl
import numpy as np
from scipy import sparse as sps
from scipy import sparse
from sklearn.preprocessing import normalize
from sklearn.feature_extraction.text import TfidfVectorizer


# In[2]:


def castString(row):
    return row.replace('"', '').replace('[', '').replace(']', '').replace("'", "").split(', ')


# In[3]:


def filterText(row):
    return [token for token in row if token.isalpha() or token.isdigit()]


# In[4]:


proc = pd.read_csv('Final_proc.csv')
print('proc read from Final_proc.csv')
print(proc.head(5))
print()


# In[ ]:


proc['processed_content'] = proc['processed_content'].apply(lambda row: castString(row))
print('processed content converted')
print(proc.head(5))
print()


# In[16]:


tf = TfidfVectorizer()


# In[17]:


def tf_idf(data_table, col_name):
    corpus_list = []
    for item in data_table[col_name]:
        corpus_list.append(' '.join(item))
    tfidf_matrix = tf.fit_transform(corpus_list)
    return tfidf_matrix


# In[49]:


a = tf_idf(proc, 'processed_content')
print('tf_idf run successfully for proc, processed_content')
pkl.dump(a, open('tf_idf_test.pkl', 'wb'))
print('matrix saved')
print()


# In[51]:


features = tf.get_feature_names()


# In[65]:


token_2_index = dict(zip(features, range(len(features))))
print('token_2_index created')
pkl.dump(token_2_index, open('token_2_index.pkl', 'wb'))
print('token_2_index saved')
print()


# In[ ]:




