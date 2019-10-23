from geo import *
from tool import *
from live import *

import pandas as pd


if __name__ == '__main__':
    t = Tool("./resources/postcodes.csv", "./resources/flood_probability.csv", "./resources/property_value.csv")
    """print(t.get_lat_long(["TN27 0HP", "CT147PF", "CT9 3BN", "TN262HQ"]))
    print(t.get_flood_cost(["anything"]))
    postcodes = pd.read_csv("./tests/test_data.csv").loc[:,'Postcode'].values
    print(postcodes)
    postcodes = [postcode.replace(' ', '').upper().strip() for postcode in postcodes]
    probstest = pd.read_csv("./tests/test_data.csv").loc[:,'Probability Band'].values
    latLongs = t.get_lat_long(postcodes)
    eastNorths = get_easting_northing_from_lat_long(latLongs[:,0], latLongs[:,1])
    probs = t.get_easting_northing_flood_probability(eastNorths[0], eastNorths[1])
    print(probs == probstest) 
    print(t.get_easting_northing_flood_probability([135549.2, 135559.9, 00, 135549.2], [32648.97, 32208.58779, 00, 32648.97]))
    sortProbs = t.get_sorted_flood_probability(postcodes)
    print(sortProbs)"""
    postcodes = pd.read_csv("./resources/postcodes.csv").loc[:,'Postcode'].values
    latLongs = t.get_lat_long(postcodes)
    eastNorths = get_easting_northing_from_lat_long(latLongs[:,0], latLongs[:,1])
    probs = t.get_easting_northing_flood_probability(eastNorths[0], eastNorths[1])