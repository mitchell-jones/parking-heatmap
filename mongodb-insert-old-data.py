# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 19:59:03 2022

@author: Mitchell Gaming PC
"""

from omegaconf import DictConfig
import hydra
import pandas as pd
import pymongo

@hydra.main(version_base=None, config_path=".", config_name="config")
def my_app(cfg: DictConfig):
    
    user = cfg['auth']['user']
    
    password = cfg['auth']['password']
    
    url = f"mongodb+srv://{user}:{password}@cluster0.ggajmmx.mongodb.net/?retryWrites=true&w=majority"
    
    client = pymongo.MongoClient(url)
    
    # This is legacy data from Heroku.
    data = pd.read_csv('dataclips_mdbxmiekltedbtruzqcdxqmqxfja (1).csv')
    
    mydb = client["personalprojects"]
    
    mycol = mydb["parkingdata"]
    
    mycol.insert_many(data.to_dict('records'))

if __name__ == "__main__":
    my_app()