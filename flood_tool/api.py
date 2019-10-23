import json
import requests
import csv
import matplotlib as plt
import pandas as pd
import urllib.request
import shutil

"""
this uses Environment Agency rainfall data from the real-time data API (Beta)
"""

#url='http://environment.data.gov.uk/flood-monitoring/data/readings?parameter=rainfall&_limit=50'        #url link 

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

   # dfstation=df.groupby(['measure','dateTime'])
   # print(dfstation.head())
    df['station']='default'
    for i in range(nb_rows):
        urlregion=df.measure[i]
        df.station[i]=requests.get(urlregion).json()['items']['stationReference']
   # print(df.head())

    dfstation=df.groupby(['station','dateTime'])
    station_ref_list=dfstation['station']
    print(station_ref_list)
    #print(dfstation.region.unique())

rainfall_date("2018-09-29") 








