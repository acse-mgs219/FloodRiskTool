import json
import requests
import csv
import matplotlib.pyplot as plt
import pandas as pd
import urllib.request
import shutil
import numpy as np
from math import isclose

#a=np.load(r'gb_coastline.npy')

"""
this uses Environment Agency rainfall data from the real-time data API (Beta)
"""

def get_lat(url):
    try:
        rjson=requests.get(url).json()
        lat=rjson['items']['lat']
        return lat
    except:
        return 390
    

def get_long(url):
    try:
        rjson=requests.get(url).json()
        longitude=rjson['items']['long']
        return longitude
    except:
        return 390

print(get_lat('https://environment.data.gov.uk/flood-monitoring/id/stations/3996'))
print(get_long('https://environment.data.gov.uk/flood-monitoring/id/stations/3996'))


def rainfall_date(date):
    urlbase = "http://environment.data.gov.uk/flood-monitoring/data/readings.csv?parameter=rainfall&parameter=rainfall&_view=full&date="
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
   
    #clean the value column of the file 
    
    df.value = df.value.astype(str)
    df.value = df.value.map(lambda p: p[(p.find('|')+1):])
    df.value = df.value.astype(float)


    maxValue=df.value.max(skipna=True)
    maxValueStationName=df.iloc[df.value.idxmax(skipna=True)]['stationReference']
    maxValueDateTime=df.iloc[df.value.idxmax(skipna=True)]['dateTime']
    print('The maximum value among all the measurements is %d mm. Taken by station %s at %s.'%(maxValue,maxValueStationName,maxValueDateTime))

    nbStation=len(df.stationReference.unique().tolist())
   #print(df.stationReference.value_counts())
    print('number of dateTime that has measurements: %d'%len(df.dateTime.unique().tolist()))
    print('Number of stations in total: %d'%(nbStation))
    #df.groupby('dateTime').hist(x='stationReference',y='value')

    dfgroup=df.groupby(['stationReference','station']).value.agg(['min','max','mean']).reset_index() #reset index
   

    #add new column (latitude,longtitude) to dfgroup
    dfgroup['lat']=dfgroup['station'].apply(get_lat)
    dfgroup['longitude']=dfgroup['station'].apply(get_long)
  
    print(dfgroup.head())

    #filter out invalid lat&long value (>360)

    dfgroup = dfgroup.drop(dfgroup[(dfgroup.lat > 360) | (dfgroup.longitude>360) ].index)
    fig, axes = plt.subplots(nrows=3, ncols=1)
    #plt.title('Maximum Rainfall')
    
    dfgroup.plot.scatter(x='longitude',y='lat',c='max',colormap='viridis',ax=axes[0])
    #plt.title('Mean Rainfall')
    dfgroup.plot.scatter(x='longitude',y='lat',c='mean',colormap='viridis',ax=axes[1])
    #plt.title('Minimum Rainfall')
    dfgroup.plot.scatter(x='longitude',y='lat',c='min',colormap='viridis',ax=axes[2])
    stationdf=df.sort_values(['stationReference','dateTime'],ascending=True).groupby('stationReference')
    station1=stationdf.get_group(name=maxValueStationName) #plot the rainfall variation of station named 'E7190'
   # plt.plot(x=station1.dateTime,y=station1.value,ax=axes[3])
    
    plt.show()
rainfall_date("2019-10-06") 






