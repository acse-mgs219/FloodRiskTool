"""Live and historical flood monitoring data from the Environment Agency API"""

import pandas as pd
import requests
import numpy as np
import json
import csv
import matplotlib.pyplot as plt
import urllib.request
import shutil
from geo import *
from tool import *

__all__  = []

LIVE_URL = "http://environment.data.gov.uk/flood-monitoring/id/stations"
ARCHIVE_URL = "http://environment.data.gov.uk/flood-monitoring/archive/"

t = Tool("resources/postcodes.csv", "resources/flood_probability.csv", "resources/property_value.csv")
tests = pd.read_csv(r'resources/postcodes.csv')
postcodes = tests.loc[0:10,'Postcode']

def station_value(station_ref):
    url = "https://environment.data.gov.uk/flood-monitoring/id/stations/"+str(station_ref)+"/readings?today"
    read = pd.read_csv(requests.get(url).json()['meta']['hasFormat'][0])
    output = read.loc[:, ['value']].sum()
    return output

def get_close_station_ref(post_lat, post_lon, post_r = 10):
    url = "https://environment.data.gov.uk/flood-monitoring/id/stations?parameter=rainfall&lat="+str(post_lat)+"&long="+str(post_lon)+"&dist="+str(post_r)
    read = pd.read_csv(requests.get(url).json()['meta']['hasFormat'][0])
    return read.loc[:, ['stationReference']]

def get_close_station_value(post_lat, post_lon, post_r = 10):
    station_ref = get_close_station_ref(post_lat, post_lon, post_r)
    output = station_value(station_ref.values[0,0])
    return output

postcodes = [postcode.replace(' ', '').upper().strip() for postcode in postcodes]
print(postcodes)
"""for post in postcodes:
    post = [post]
    risk = t.get_sorted_annual_flood_risk(post)
    risk = risk.loc[post, 'Flood Risk']
    print(risk)
    post_lat_long = t.get_lat_long(post)
    print(post)
    rainfallvalue = get_close_station_value(post_lat_long[0,0], post_lat_long[0,1])
    print(rainfallvalue)"""

def rainfall_date(date):
    urlbase = "http://environment.data.gov.uk/flood-monitoring/data/readings.csv?date="
    url=urlbase+date
    r = requests.get(url, verify=False,stream=True)
    
    if r.status_code != 200:
        print("Failure!!")
        exit()
    else:
        r.raw.decode_content = True
        with open("file1.csv", 'wb') as f:
            shutil.copyfileobj(r.raw, f)
        print("Success")
    
    df=pd.read_csv("file1.csv")
    nb_rows=len(df.index)

    df['station']='default'
    for i in range(nb_rows):
        urlregion=df.measure[i]
        df.station[i]=requests.get(urlregion).json()['items']['stationReference']

    df.sort_values(['station','dateTime'],ascending=True).groupby('station').plot(x='dateTime',y='value',legend=True,title='station')
    plt.show()
rainfall_date("2018-09-29") 
