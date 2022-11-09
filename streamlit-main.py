import streamlit as st
from omegaconf import DictConfig
import hydra
import pandas as pd
import pymongo

@hydra.main(version_base=None, config_path=".", config_name="config")
def extract_data(cfg: DictConfig):
    user = cfg['auth']['user']
    
    password = cfg['auth']['password']
    
    url = f"mongodb+srv://{user}:{password}@cluster0.ggajmmx.mongodb.net/?retryWrites=true&w=majority"
    
    client = pymongo.MongoClient(url)
    
    data = pd.read_csv('dataclips_mdbxmiekltedbtruzqcdxqmqxfja (1).csv')
    
    mydb = client["personalprojects"]
    
    mycol = mydb["parkingdata"]
    
    data = mycol.find()
    
    extracted_data = pd.DataFrame(list(data))
    
    return extracted_data

if __name__ == "__main__":
    data = extract_data()
    st.write(data)
