import json
import urllib.request

#locu_api=   #key
url='http://environment.data.gov.uk/flood-monitoring/data/readings?parameter=rainfall&_limit=50'        #url link 
json_obj=urllib.request.urlopen(url)

data=json.load(json_obj)

for item in data['items']:  
    print (item['@id'])
    print (item['value'])