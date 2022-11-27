import streamlit as st
import pandas as pd
import pymongo
import certifi

def get_client():
    # Get user, pass
    user = st.secrets.auth.user
    password = st.secrets.auth.password

    # MongoDB Auth
    url = f"mongodb+srv://{user}:{password}@cluster0.ggajmmx.mongodb.net/?retryWrites=true&w=majority"
    client = pymongo.MongoClient(url, tlsCAFile=certifi.where())

    return client

def load_data():
    client = get_client()

    # Loading data
    mydb = client["personalprojects"]
    mycol = mydb["parkingdata"]
    data = mycol.find()
    
    # Convert data to DataFrame
    imported_data = pd.DataFrame(list(data))
    del imported_data['_id']
    return imported_data

if __name__ == "__main__":
    data = load_data()
    # data = data.rename({'_id':'id'}, axis =1)
    st.write(data)
