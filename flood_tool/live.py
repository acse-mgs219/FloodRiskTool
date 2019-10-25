"""Live and historical flood monitoring data from the Environment Agency API"""

import pandas as pd
import requests
import numpy as np
import json
import csv
import matplotlib.pyplot as plt
import urllib.request
import shutil
from .geo import *
from .tool import *

__all__  = []

LIVE_URL = "http://environment.data.gov.uk/flood-monitoring/id/stations"
ARCHIVE_URL = "http://environment.data.gov.uk/flood-monitoring/archive/"

#t = Tool("resources/postcodes.csv", "resources/flood_probability.csv", "resources/property_value.csv")
#tests = pd.read_csv(r'resources/postcodes.csv')
#postcodes = tests.loc[0:10,'Postcode']

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

#postcodes = [postcode.replace(' ', '').upper().strip() for postcode in postcodes]
#print(postcodes)
"""for post in postcodes:
    post = [post]
    risk = t.get_sorted_annual_flood_risk(post)
    risk = risk.loc[post, 'Flood Risk']
    print(risk)
    post_lat_long = t.get_lat_long(post)
    print(post)
    rainfallvalue = get_close_station_value(post_lat_long[0,0], post_lat_long[0,1])
    print(rainfallvalue)"""

def get_lat(url):
    """Get the latitude from url.
    
    Parameters
    ----------
    url: str
    Return
    ------
    lat: float
    """
    try:
        rjson=requests.get(url).json()
        lat=rjson['items']['lat']
        return lat
    except:
        return 390

def get_long(url):
    """Get the longitude from url.
    
    Parameters
    ----------
    url: str
    Return
    ------
    longitude: float
    """
    try:
        rjson=requests.get(url).json()
        longitude=rjson['items']['long']
        return longitude
    except:
        return 390


def rainfall_date(date):
    """Analysis the rainfall of a specific date.
    
    Parameters
    ----------
    date: str
    """
    urlbase = "http://environment.data.gov.uk/flood-monitoring/data/readings.csv?parameter=rainfall&parameter=rainfall&_view=full&date="
    url=urlbase+date
    r = requests.get(url, verify=False,stream=True)

    ##download the required csv file for analysis
    if r.status_code != 200:
        print("Failure!!")
        exit()
    else:
        r.raw.decode_content = True
        with open("rain_on_day.csv", 'wb') as f:
            shutil.copyfileobj(r.raw, f)
        print("Success")
    df=pd.read_csv("rain_on_day.csv")

    #clean the value column of the file
    df.value = df.value.astype(str)
    df.value = df.value.map(lambda p: p[(p.find('|')+1):])
    df.value = df.value.astype(float)
    maxValue=df.value.max(skipna=True)
    maxValueStationName=df.iloc[df.value.idxmax(skipna=True)]['stationReference']
    maxValueDateTime=df.iloc[df.value.idxmax(skipna=True)]['dateTime']
    print('The maximum value among all the measurements is %d mm. Taken by station %s at %s.'%(maxValue,maxValueStationName,maxValueDateTime))
    nbStation=len(df.stationReference.unique().tolist())
   
    print('Number of dateTime that has measurements: %d'%len(df.dateTime.unique().tolist()))
    print('Number of stations in total: %d'%(nbStation))
    
    dfgroup=df.groupby(['stationReference','station']).value.agg(['min','max','mean']).reset_index() #reset index

    #add new column (latitude,longtitude) to dfgroup
    dfgroup['lat']=dfgroup['station'].apply(get_lat)
    dfgroup['longitude']=dfgroup['station'].apply(get_long)
    
    #filter out invalid lat&long value (>360)
    dfgroup = dfgroup.drop(dfgroup[(dfgroup.lat > 360) | (dfgroup.longitude>360) ].index)
    fig, axes = plt.subplots(1, 3)
    axes[0].set_title('Max')
    axes[0].set_xlabel('rainfall (mm)')
    fig.suptitle('Rainfall on 6 October', fontsize=16)

    axes[1].set_xlabel('rainfall (mm)')
    axes[1].set_title('Mean')
    axes[2].set_xlabel('rainfall (mm)')
    axes[2].set_title('Min')
   
    dfgroup=dfgroup.sort_values(['max'],ascending=True)
    dfgroup.plot.scatter(x='longitude',y='lat',c='max',colormap='viridis',ax=axes[0])
    
    dfgroup=dfgroup.sort_values(['mean'],ascending=True)
    dfgroup.plot.scatter(x='longitude',y='lat',c='mean',colormap='viridis',ax=axes[1])
    
    dfgroup=dfgroup.sort_values(['min'],ascending=True)
    dfgroup.plot.scatter(x='longitude',y='lat',c='min',colormap='viridis',ax=axes[2])
   
    plt.show()


rainfall_date("2019-10-06") 
