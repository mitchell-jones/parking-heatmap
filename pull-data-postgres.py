#!/usr/bin/env python
# coding: utf-8

# In[1]:


print('startup')
import json
import pandas as pd
from datetime import datetime
from sseclient import SSEClient


# In[2]:


url = 'https://parkingavailability.charlotte.edu/decks/stream'


# In[3]:


client = SSEClient(url)


# In[4]:


for i in client:
    data = i
    break


# In[5]:


now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")


# In[6]:


json_data = json.loads(data.data)


# In[7]:


output = pd.DataFrame(json_data)


# In[8]:


output['time'] = dt_string


# In[9]:


display(output)


# #### Output Data to Postgres on Heroku

# In[10]:


import os


# In[11]:


try:
    db_url = os.environ['DATABASE_URL_1']
except:
    print('DB-URL not retrieved from environment correctly.')
print(db_url)


# In[18]:


try:
    #import the relevant sql library 
    from sqlalchemy import create_engine
    # link to your database
    engine = create_engine(db_url, echo = False)
    # attach the data frame (df) to the database with a name of the 
    # table; the name can be whatever you like
    output.to_sql('parkingdata', con = engine, if_exists='append')
except:
    print("output to db unsuccessful.")

