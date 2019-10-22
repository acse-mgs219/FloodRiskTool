from .geo import *
from .tool import *
from .live import *

import pandas as pd


if __name__ == '__main__':
    t = Tool("postcodes.csv", "flood_probability.csv", "property_value.csv")
    t.get_lat_long(["TN27 0HP", "CT147PF", "CT9 3BN", "TN262HQ"])
    print(t.get_easting_northing_flood_probability_band([441107.576017082], [406879.053604562]))