"""This module is used to analyze the rainfall data taken by all the stations in UK on Oct 6th"""


import json
import requests
import csv
import matplotlib.pyplot as plt
import pandas as pd
import urllib.request
import shutil
import numpy as np
from math import isclose


"""

this uses Environment Agency rainfall data from the real-time data API (Beta)

"""

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
        with open("file1.csv", 'wb') as f:
            shutil.copyfileobj(r.raw, f)
        print("Success")
    df=pd.read_csv("file1.csv")

    #clean the value column of the file
    df.value = df.value.astype(str)
    df.value = df.value.map(lambda p: p[(p.find('|')+1):])
    df.value = df.value.astype(float)
    maxValue=df.value.max(skipna=True)
    maxValueStationName=df.iloc[df.value.idxmax(skipna=True)]['stationReference']
    maxValueDateTime=df.iloc[df.value.idxmax(skipna=True)]['dateTime']
    print('The maximum value among all the measurements is %d mm. Taken by station %s at %s.'%(maxValue,maxValueStationName,maxValueDateTime))
    nbStation=len(df.stationReference.unique().tolist())
   
    print('number of dateTime that has measurements: %d'%len(df.dateTime.unique().tolist()))
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