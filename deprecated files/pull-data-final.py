#!/usr/bin/env python
# coding: utf-8

# In[ ]:


print('Starting up.')
import json
import pandas as pd
from datetime import datetime, timedelta
from sseclient import SSEClient
import os
from time import sleep

while True:
    if datetime.today().minute % 15 == 0:
        print('Running job!')
        url = 'https://parkingavailability.charlotte.edu/decks/stream'
        client = SSEClient(url)
        
        for i in client:
            data = i
            break

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        json_data = json.loads(data.data)

        output = pd.DataFrame(json_data)

        output['time'] = dt_string

        try:
            db_url = os.environ['DATABASE_URL_1']
        except:
            print('DB-URL not retrieved from environment correctly.')

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
        print('Done with Job! Sleep.')
    sleep(60)


# In[ ]:




