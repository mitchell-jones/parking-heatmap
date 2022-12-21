import matplotlib.pyplot as plt
import altair as at
import pandas as pd
import seaborn as sns
import streamlit as st
import pymongo
import certifi
from datetime import timedelta
import numpy as np
import matplotlib.ticker as ticker
import time
from datetime import datetime

replace_array = [0,15,30,45]

st.set_page_config(page_title="Streamlit UNCC Parking", layout="wide")
timenow = datetime.now()
replace_time = replace_array[timenow.minute // 15]
timenow = timenow.replace(minute = replace_time, second = 0, microsecond = 0)

def get_client():
    # Get user, pass
    user = st.secrets.auth.user
    password = st.secrets.auth.password

    # MongoDB Auth
    url = f"mongodb+srv://{user}:{password}@cluster0.ggajmmx.mongodb.net/?retryWrites=true&w=majority"
    client = pymongo.MongoClient(url, tlsCAFile=certifi.where())

    return client

@st.cache(allow_output_mutation = True)
def load_data(timenow):
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

data = load_data(timenow)

def main_page():
    st.markdown("# About")
    st.markdown("""This personal project web-scrapes UNC Charlotte's parking availability page via a scheduled task on a Raspberry Pi. 
    From there, the Pi uploads the data into MongoDB, which is directly accessed by this Streamlit App, providing an interactive front-end for EDA.""")
    st.markdown("Interested in connecting with me after seeing this? You can contact me via my [LinkedIn](https://www.linkedin.com/in/mitchelljones49/), or view the source code on [GitHub](https://github.com/mitchell-jones/parking-heatmap).")
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
    fig = plt.figure(figsize = (11.7,7))
    ax = sns.lineplot(data = grouped_counts, x = 'date', y = 'percentAvailable')
    ax.set(ylabel = 'Number of Records')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
    st.pyplot(fig)

    metric_dict = filtered.groupby('name').count().to_dict()['percentAvailable']
    average_avail = filtered.groupby('name')['percentAvailable'].count().mean()

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
    st.sidebar.markdown('# Filters')
    st.markdown("# Historical Analysis")
    st.markdown("This page shows analysis on the historical trends of each of the parking deck - allowing you to visualize the parking deck availability levels over time, as well as a heatmap of the busiest hours per week")
    st.markdown("For especially interesting insights, observe how South Village Deck acts differently than Union Deck Lower, since South Village Deck is primarily a deck for resident's cars, while Union Deck Lower is for commuters and main campus access. Over the period of November 27-29th, South Village Deck fills up sooner as students return to campus (filling up residential decks) before commuters, who fill up commuter decks like Union Deck Lower.")
    with st.sidebar:
        if not st.checkbox('Display All Decks'):
            selected_opts = st.multiselect("Select Decks to Include in Graph", options = data.name.unique(), default=['Union Deck Lower', 'South Village Deck'])
            filtered = data[data['name'].isin(selected_opts)]
        else:
            filtered = data.copy()

    min_date = data.date.min() - timedelta(1)
    max_date = data.date.max() + timedelta(1)

    col1, col2 =  st.columns(2)
    with col1:
        begin_date = st.date_input('Select the beginning of the date range.', value = min_date, 
        min_value = min_date, max_value = max_date)
    with col2:
        end_date = st.date_input('Select the end of the date range.', value = max_date, 
        min_value = min_date, max_value = max_date)

    filtered = filtered[(filtered.date > begin_date) & (filtered.date < end_date)]
    if len(filtered) != 0:
        sns.set_theme(style="darkgrid")
        fig = plt.figure(figsize = (11.7,7))
        plot = sns.lineplot(data = filtered, x = filtered.datetime, y = 'percentAvailable', hue = 'name')
        plot.set(xlabel='Time', ylabel='Percent Available', title = 'Deck Availability by Time')
        plot.xaxis.set_major_locator(ticker.MultipleLocator(1))
        plot.set_xticklabels(plot.get_xticklabels(), rotation=40, ha="right")
        st.pyplot(fig)
    else:
        st.write('Select one or more decks to see the heatmap and graph, here.')
    try:
        fig = plt.figure(figsize = (11.7,7))
        filtered['hour'] = filtered.datetime.dt.hour
        filtered['dayofweek'] = filtered.datetime.dt.day_name()
        heat = filtered.pivot_table('percentAvailable', ['dayofweek'], 'hour')
        heat = heat.reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], axis = 0)
        plot = sns.heatmap(heat)
        plot.set_yticklabels(plot.get_yticklabels(), rotation=0, ha="right")
        plot.set(ylabel = 'Day of Week', xlabel = 'Hour', title = 'Heatmap of Average Availability')
        st.pyplot(fig)
    except ValueError:
        pass

def page3():
    st.markdown("# Latest Availability")

    newest_write = data.datetime.max()
    st.markdown("This page shows the parking deck availability by deck, as of {}.".format(newest_write))

    most_current = data[data.datetime == newest_write].sort_values('percentAvailable', ascending = False)

    def colors_from_values(values, palette_name):
        # normalize the values to range [0, 1]
        normalized = (values - min(values)) / (max(values) - min(values))
        # convert to indices
        indices = np.round(normalized * (len(values) - 1)).astype(np.int32)
        # use the indices to get the colors
        palette = sns.dark_palette('seagreen', len(values))
        return np.array(palette).take(indices, axis=0)

    fig = plt.figure(figsize = (11.7,7))
    ax = sns.barplot(data = most_current, y = 'name', x = 'percentAvailable', 
        palette = colors_from_values(most_current['percentAvailable'], None)).set(ylabel = 'Deck', title = 'Percent Available by Deck', xlabel = 'Percent Available')
    st.pyplot(fig)

    most_current.index = most_current.name
    metric_dict = most_current.to_dict()['percentAvailable']
    average_avail = most_current.percentAvailable.mean()

    st.markdown("""### Availability per Deck
    Small number is difference from the average, {}.""".format(round(average_avail, 3)))
    col1, col2 = st.columns(2)
    i = 0

    def render_metric(name):
            dif = metric_dict[name] - average_avail
            if dif != 0:
                st.metric(label = name, value = round(metric_dict[name], 3), delta = round(dif,3))
            else:
                st.metric(label = name, value = round(metric_dict[name], 3), delta = round(dif, 3), delta_color = 'off')

    for name in most_current.name.unique():
        if i % 2 == 0:
            with col1:
                render_metric(name)
        else:
            with col2:
                render_metric(name)
        i += 1



page_names_to_funcs = {
    "Uptime Statistics & About": main_page,
    "Historical Analysis": page2,
    "Latest Availability": page3,
}

st.sidebar.markdown('# Page Selection')
selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()
