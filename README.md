# Parking Data
Scrapes data from UNC Charlotte's parking availability tracker (https://parkingavailability.charlotte.edu/) every 15 minutes and appends it to a table in MongoDB via a script running on my Raspberry Pi.

Data to be used in interactive visualizations later and parking deck-level outlier detection! I'm also planning on utilizing streamlit.

### Data loading architecture:
Python script on raspberry pi writes to MongoDB -> MongoDB Atlas holds data in cloud -> Streamlit app accesses mongoDB directly

### General data loading workflow:
-> pi runs mongodb-insert-new-data.py
-> python script runs once a minute, checking to see if it is a time divisible by 15
-> if yes, scrape the website & write the results to my MongoDB atlas instance
-> if no, sleep for another minute.
 
