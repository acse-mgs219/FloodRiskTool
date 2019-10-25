"""Live and historical flood monitoring data from the Environment Agency API"""

import pandas as pd
import requests
import numpy as np
import folium
from .geo import *
from .tool import *

__all__  = []

LIVE_URL = "http://environment.data.gov.uk/flood-monitoring/id/stations"
ARCHIVE_URL = "http://environment.data.gov.uk/flood-monitoring/archive/"

t = Tool("resources/postcodes.csv", "resources/flood_probability.csv", "resources/property_value.csv")
tests = pd.read_csv(r'../score/test_data.csv')
postcodes = tests['Postcode']
tests = t.get_sorted_annual_flood_risk(postcodes)
tests = tests.iloc[0:10, :]
postcodes = tests.index.tolist()

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

Latitude = []
Longitude = []
risks = []
rainfall = []
for post in postcodes:
    post = [post]
    risk = t.get_sorted_annual_flood_risk(post)
    risk = risk.loc[:, 'Flood Risk']   
    risks.append(risk.values)	
    post_lat_long = t.get_lat_long(post)
    Latitude.append(post_lat_long[0,0])
    Longitude.append(post_lat_long[0,1])
    rainfallvalue = get_close_station_value(post_lat_long[0,0], post_lat_long[0,1])
    rainfall.append(rainfallvalue.values)

tests['Latitude'] = Latitude
tests['Longitude'] = Longitude
tests['Risks'] = risks
tests['Rain'] = rainfall

print(tests)

alerts = tests[(tests['Risks'] > 0) & (tests['Rain'] > 0.6)]
print(alerts)

m = folium.Map(location=[51.5074, 0.1278])
for i in range(len(alerts.index)):
    folium.Marker(
        location=[alerts.iloc[i,0], alerts.iloc[i,1]],
        popup='Flood Risk! Alert!',
        icon=folium.Icon(icon='cloud')
    ).add_to(m)
