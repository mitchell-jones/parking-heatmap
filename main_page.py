import matplotlib.pyplot as plt
import altair as at
import pandas as pd
import seaborn as sns
import streamlit as st
import pymongo
import certifi
from datetime import timedelta

def get_client():
    # Get user, pass
    user = st.secrets.auth.user
    password = st.secrets.auth.password

    # MongoDB Auth
    url = f"mongodb+srv://{user}:{password}@cluster0.ggajmmx.mongodb.net/?retryWrites=true&w=majority"
    client = pymongo.MongoClient(url, tlsCAFile=certifi.where())

    return client

@st.cache
def load_data():
    client = get_client()

    # Loading data
    mydb = client["personalprojects"]
    mycol = mydb["parkingdata"]
    data = mycol.find()
    
    # Convert data to DataFrame
    imported_data = pd.DataFrame(list(data))
    del imported_data['_id']
    imported_data.datetime = pd.to_datetime(imported_data['datetime'])
    imported_data.date = imported_data.datetime.dt.date
    return imported_data

data = load_data()

def main_page():
    st.markdown("# About")
    st.sidebar.markdown("# Uptime Statistics")
    st.markdown("""This personal project web-scrapes UNC Charlotte's parking availability page via a scheduled task on a Raspberry Pi. 
    From there, the Pi uploads the data into MongoDB, which is directly accessed by this Streamlit App, providing an interactive front-end for EDA.""")
    st.markdown("Interested in connecting with me after seeing this? You can contact me via my [LinkedIn](https://www.linkedin.com/in/mitchelljones49/).")
    st.markdown("# Uptime Statistics")
    st.markdown("""This page shows statistics on uptime - we can determine these statistics by aggregating and examining the number of and times of the "writes" to the MongoDB.""")

    st.markdown("### Total Number of Writes over Time")
    min_date = data.date.min() - timedelta(1)
    max_date = data.date.max() + timedelta(1)

    col1, col2 =  st.columns(2)
    with col1:
        begin_date = st.date_input('Select the beginning of the date range.', value = min_date, 
        min_value = min_date, max_value = max_date)
    with col2:
        end_date = st.date_input('Select the end of the date range.', value = max_date, 
        min_value = min_date, max_value = max_date)

    filtered = data[(data.date > begin_date) & (data.date < end_date)]
    
    grouped_counts = filtered.groupby('date').count()
    sns.set_palette(sns.dark_palette("seagreen"))
    fig = plt.figure()
    ax = sns.lineplot(data = grouped_counts, x = 'date', y = 'percentAvailable')
    ax.set(ylabel = 'Number of Records')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
    st.pyplot(fig)

    metric_dict = filtered.groupby('name').count().to_dict()['percentAvailable']
    average_avail = filtered.groupby('name')['percentAvailable'].count().mean()

    st.header("")
    st.markdown("""### Number of Writes per Deck
    Small number is difference from the average, {}.""".format(average_avail))
    col1, col2 = st.columns(2)
    i = 0

    def render_metric(name):
            dif = metric_dict[name] - average_avail
            if dif != 0:
                st.metric(label = name, value = metric_dict[name], delta = dif)
            else:
                st.metric(label = name, value = metric_dict[name], delta = dif, delta_color = 'off')

    for name in filtered.name.unique():
        if i % 2 == 0:
            with col1:
                render_metric(name)
        else:
            with col2:
                render_metric(name)
        i += 1

    st.markdown("### Data Sample")
    st.write(filtered.head(5))

def page2():
    st.markdown("# Historical Analysis")
    st.sidebar.markdown("# Historical Analysis")

def page3():
    st.markdown("# Latest Availability")
    st.sidebar.markdown("# Latest Availability")

page_names_to_funcs = {
    "Uptime Statistics & About": main_page,
    "Historical Analysis": page2,
    "Latest Availability": page3,
}

selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()