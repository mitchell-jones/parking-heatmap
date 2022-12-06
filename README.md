# Parking Data
## Introduction
Scrapes data from ![UNC Charlotte's parking availability tracker](https://parkingavailability.charlotte.edu/) every 15 minutes and appends it to a table in MongoDB via a script running on my Raspberry Pi. Data is then ingested into Streamlit for exploration of my uptime statistics, as well as current availability and historical analysis.

You can access the Streamlit app ![here](https://mitchell-jones-parking-heatmap-main-page-v2u3cp.streamlit.app/) - also, if you're viewing this directly, and would like to connect with me, feel free to reach out via my ![LinkedIn](https://www.linkedin.com/in/mitchelljones49/)

## Data loading architecture & Workflow
Python script on raspberry pi writes to MongoDB -> MongoDB Atlas holds data in cloud -> Streamlit app accesses mongoDB directly

### General data loading workflow:
-> pi runs mongodb-insert-new-data.py
-> python script runs once a minute, checking to see if it is a time divisible by 15 (for a write in 15 minute intervals)
-> if yes, scrape the website & write the results to my MongoDB atlas instance
-> if no, sleep for another minute.

-> Streamlit app accesses MongoDB credentials through a .toml file
-> Authenticates with MongoDB and pull data into cache at the start of the app
-> Updates Web App immediately if new data is received on the quarter hour mark during use
 
## Future Development
Once the scraper has been running longer, I'd love to do more machine learning with this app. For example, we could separate out the observations for each parking deck and see if we could reliably predict outliers within the data, for better understanding of the student body but also double-checking that the automated sensors are functioning correctly.

Example of outlier in data due to bad sensors:
![Outliers](https://raw.githubusercontent.com/mitchell-jones/parking-heatmap/main/outlier.png)
