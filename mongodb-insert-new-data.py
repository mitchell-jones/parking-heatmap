# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 19:59:03 2022

@author: Mitchell Gaming PC
"""

from omegaconf import DictConfig
import hydra
import pandas as pd
import pymongo
from datetime import datetime
from sseclient import SSEClient
import json
from time import sleep
import certifi

def update_data(mycol):
    interval = 1 # Should be 15
    while True:
        print('Checking!')
        if datetime.today().minute % interval == 0:
            print('Running job!')
            url = 'https://parkingavailability.charlotte.edu/decks/stream'
            client = SSEClient(url)
            
            for i in client:
                data = i
                break

            now = datetime.now()
            dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
            
            d_string = now.strftime("%m/%d/%Y")
            
            json_data = json.loads(data.data)

            output = pd.DataFrame(json_data)

            output['datetime'] = dt_string
            
            output['date'] = d_string

            print('Done with Job!')
            
            mycol.insert_many(output.to_dict('records'))
        print('Sleeping!')
        sleep(60)

@hydra.main(version_base=None, config_path=".", config_name="config")
def my_app(cfg: DictConfig):
    
    user = cfg['auth']['user']
    
    password = cfg['auth']['password']
    
    url = f"mongodb+srv://{user}:{password}@cluster0.ggajmmx.mongodb.net/?retryWrites=true&w=majority"
    
    client = pymongo.MongoClient(url, tlsCAFile=certifi.where())
    
    mydb = client["personalprojects"]
    
    mycol = mydb["parkingdata"]
    
    update_data(mycol)

if __name__ == "__main__":
    my_app()