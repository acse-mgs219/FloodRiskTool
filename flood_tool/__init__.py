from geo import *
from tool import *
from live import *

import pandas as pd


if __name__ == '__main__':
    t = Tool("postcodes.csv", "flood_probability.csv", "property_value.csv")
    t.get_lat_long(["CT147DB", "TN103PU"])