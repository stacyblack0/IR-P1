#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np


# In[2]:


final_index = pd.read_csv('final_index.csv')


# In[3]:


final_index.head()


# In[4]:


final_index.drop(columns=['Unnamed: 0'], inplace = True)


# In[5]:


term_doc_list = final_index.groupby(['token'])['doc'].apply(list)


# In[ ]:


term_doc = term_doc_list.to_frame().reset_index()


# In[ ]:


term_doc.to_csv(r'term_doc.csv')

