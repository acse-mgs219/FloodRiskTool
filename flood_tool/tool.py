"""Locator functions to interact with geographic data"""
import pandas as pd
import numpy as np
from .geo import *


__all__ = ['Tool']

class Tool(object):
    """Class to interact with a postcode database file."""

    def __init__(self, postcode_file=None, risk_file=None, values_file=None):
        """

        Reads postcode and flood risk files and provides a postcode locator service.

        Parameters
        ---------

        postcode_file : str, optional
            Filename of a .csv file containing geographic location data for postcodes.
        risk_file : str, optional
            Filename of a .csv file containing flood risk data.
        postcode_file : str, optional
            Filename of a .csv file containing property value data for postcodes.
        """
        # read postcodes.csv
        if postcode_file == None:
            self.df_postcode_file = pd.read_csv("./resources/postcodes.csv")
        else:
            self.df_postcode_file = pd.read_csv(postcode_file)
        # formatting the postcode column of postcodes file
        self.df_postcode_file.Postcode = self.df_postcode_file.Postcode.str.replace(' ',
                                                                                    '')  # delete space in postcodes strings
        self.df_postcode_file.Postcode = self.df_postcode_file.Postcode.str.strip()
        self.df_postcode_file.Postcode = self.df_postcode_file.Postcode.str.upper()
        # self.df_postcode_file = self.df_postcode_file.set_index('Postcode')

        # read flood_probability.csv
        if risk_file == None:
            self.df_risk_file = pd.read_csv("./resources/flood_probability.csv")
        else:
            self.df_risk_file = pd.read_csv(risk_file)
        del self.df_risk_file['Unnamed: 0']

        # read property_value.csv
        if values_file == None:
            self.df_values_file = pd.read_csv("./resources/property_value.csv")
        else:
            self.df_values_file = pd.read_csv(values_file)
        # formatting the postcode column of property file
        self.df_values_file.Postcode = self.df_values_file.Postcode.str.replace(' ',
                                                                                '')  # delete space in postcodes strings
        self.df_values_file.Postcode = self.df_values_file.Postcode.str.strip()
        self.df_values_file.Postcode = self.df_values_file.Postcode.str.upper()

        # merge two
        self.cat_pst_values = self.df_postcode_file.set_index('Postcode').join(self.df_values_file.set_index('Postcode'))
        del self.cat_pst_values['Lat']
        del self.cat_pst_values['Long']
        self.cat_pst_values = self.cat_pst_values.fillna(0)


    def get_lat_long(self, postcodes):
        """Get an array of WGS84 (latitude, longitude) pairs from a list of postcodes.

        Parameters
        ----------

        postcodes: sequence of strs
            Ordered sequence of N postcode strings

        Returns
        -------

        ndarray
            Array of Nx2 (latitude, longitdue) pairs for the input postcodes.
            Invalid postcodes return [`numpy.nan`, `numpy.nan`].
        """
        postcodes = [postcode.replace(' ', '').upper().strip() for postcode in postcodes]
        indices = self.cat_pst_values.loc[postcodes, ['Latitude', 'Longitude']]
        return indices.values


    def get_easting_northing_flood_probability(self, easting, northing):

        """Get an array of flood risk probabilities from arrays of eastings and northings.

        Flood risk data is extracted from the Tool flood risk file. Locations
        not in a risk band circle return `Zero`, otherwise returns the name of the
        highest band it sits in.

        Parameters
        ----------

        easting: numpy.ndarray of floats
            OS Eastings of locations of interest
        northing: numpy.ndarray of floats
            Ordered sequence of postcodes

        Returns
        -------

        numpy.ndarray of strs
            numpy array of flood probability bands corresponding to input locations.
        """

        # cor1x: nparray of all points' x value
        # cor1y: nparray of all points' y value
        # r: nparray of radius
        # pro： nparray of probability
        # inputcor: nparray of input points' coordinates
        # outputcor: nparray
        df = self.df_risk_file
        df['prob_4band'] = pd.Categorical(df['prob_4band'], ["High", "Medium", "Low",
                                                             "Very Low", "Zero"])
        df = df.sort_values(by=['prob_4band'])
        cor1x = np.array(df.drop(['Y', 'prob_4band', 'radius'], axis=1))
        cor1y = np.array(df.drop(['X', 'prob_4band', 'radius'], axis=1))
        pro = np.array(df.drop(['X', 'Y', 'radius'], axis=1))
        r = np.array(df.drop(['X', 'Y', 'prob_4band'], axis=1))
        outputpro = []
        for m, n in zip(easting, northing):
            r_relative = np.sqrt((cor1x - m) ** 2 + (cor1y - n) ** 2)
            judge = r_relative < r
            if (len(pro[judge]) == 0):
                outputpro.append("Zero")
            else:
                outputpro.append(pro[judge][0])
        return outputpro





    def get_sorted_flood_probability(self, postcodes):
        """Get an array of flood risk probabilities from a sequence of postcodes.

        Probability is ordered High>Medium>Low>Very low>Zero.
        Flood risk data is extracted from the `Tool` flood risk file.

        Parameters
        ----------

        postcodes: sequence of strs
            Ordered sequence of postcodes

        Returns
        -------

        pandas.DataFrame
            Dataframe of flood probabilities indexed by postcode and ordered from `High` to `Zero`,
            then by lexagraphic (dictionary) order on postcode. The index is named `Postcode`, the
            data column is named `Probability Band`. Invalid postcodes and duplicates
            are removed.
        """
        latLongs = self.get_lat_long(postcodes)
        eastNorths = get_easting_northing_from_lat_long(latLongs[:, 0], latLongs[:, 1])
        probs = self.get_easting_northing_flood_probability(eastNorths[0], eastNorths[1])
        probsSort = pd.DataFrame({'Postcode': postcodes, 'Probability Band': probs})
        probsSort.set_index('Postcode', inplace=True)
        probsSort['Probability Band'] = pd.Categorical(probsSort['Probability Band'],
                                                       ["High", "Medium", "Low", "Very Low", "No Risk"])
        probsSort = probsSort.sort_values(by=['Probability Band', 'Postcode'])
        probsSort = probsSort[~probsSort.index.duplicated(keep='first')].dropna()
        return probsSort


    def get_flood_cost(self, postcodes):
        """Get an array of estimated cost of a flood event from a sequence of postcodes.
        Parameters
        ----------

        postcodes: sequence of strs
            Ordered collection of postcodes
        probability_bands: sequence of strs
            Ordered collection of flood probability bands

        Returns
        -------

        numpy.ndarray of floats
            array of floats for the pound sterling cost for the input postcodes.
            Invalid postcodes return `numpy.nan`.
        """
        flood_cost = []
        postcodes = [postcode.replace(' ', '').upper().strip() for postcode in postcodes]
        indices = self.cat_pst_values.loc[postcodes, 'Total Value']
        return np.array(indices.values)


    def get_annual_flood_risk(self, postcodes, probability_bands):
        """Get an array of estimated annual flood risk in pounds sterling per year of a flood
        event from a sequence of postcodes and flood probabilities.

        Parameters
        ----------

        postcodes: sequence of strs
            Ordered collection of postcodes
        probability_bands: sequence of strs
            Ordered collection of flood probabilities

        Returns
        -------

        numpy.ndarray
            array of floats for the annual flood risk in pounds sterling for the input postcodes.
            Invalid postcodes return `numpy.nan`.
        """
        flood_risk = []
        reduce_cost = 0.05
        postcodes = [postcode.replace(' ', '').upper().strip() for postcode in postcodes]
        pro = np.array(probability_bands)
        pro[pro == "High"] = 1 / 10
        pro[pro == "Medium"] = 1 / 50
        pro[pro == "Low"] = 1 / 100
        pro[pro == "Very Low"] = 1 / 1000
        pro[pro == "No Risk"] = 0.0
        flood_risk = self.cat_pst_values.loc[postcodes, 'Total Value'].values * pro.astype(float) * reduce_cost
        return np.array(flood_risk)


    def get_sorted_annual_flood_risk(self, postcodes):
        """Get a sorted pandas DataFrame of flood risks.

        Parameters
        ----------

        postcodes: sequence of strs
            Ordered sequence of postcodes

        Returns
        -------

        pandas.DataFrame
            Dataframe of flood risks indexed by (normalized) postcode and ordered by risk,
            then by lexagraphic (dictionary) order on the postcode. The index is named
            `Postcode` and the data column `Flood Risk`.
            Invalid postcodes and duplicates are removed.
        """
        latLongs = self.get_lat_long(postcodes)
        eastNorths = get_easting_northing_from_lat_long(latLongs[:, 0], latLongs[:, 1])
        probs = self.get_easting_northing_flood_probability(eastNorths[0], eastNorths[1])
        flood_risk = self.get_annual_flood_risk(postcodes, probs)
        probsSort = pd.DataFrame({'Postcode': postcodes, 'Flood Risk': flood_risk})
        annual_flood_risk = probsSort.sort_values(by=['Flood Risk', 'Postcode'], ascending=[False, True])
        annual_flood_risk.set_index('Postcode', inplace=True)
        annual_flood_risk = annual_flood_risk[~annual_flood_risk.index.duplicated(keep='first')].dropna()
        return annual_flood_risk