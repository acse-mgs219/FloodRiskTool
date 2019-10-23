"""Locator functions to interact with geographic data"""
import pandas as pd
import numpy as np
from .geo import *
# import .geo

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
        # self.get_lat_long_lst = []
        # self.get_e_n_flood_prob_band = []
        # self.flood_risk = []

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
        # self.cat_pst_values = self.df_postcode_file.append(self.df_values_file, ignore_index=True, sort=False)
        self.cat_pst_values = self.df_postcode_file.set_index('Postcode').join(self.df_values_file.set_index('Postcode'))
        del self.cat_pst_values['Lat']
        del self.cat_pst_values['Long']
        self.cat_pst_values = self.cat_pst_values.fillna(0)

        print(self.cat_pst_values)
        print(self.df_postcode_file.head(n=14))
        print(self.df_risk_file.head())
        print(self.df_values_file.head())
        print("read 3 file successfully")

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

        # get index in cat_pst_values that contains postcodes
        postcodes = [postcode.replace(' ', '').upper().strip() for postcode in postcodes]
        # self.df_postcode_file.set_index('Postcode', inplace=True)
        indices = self.cat_pst_values.loc[postcodes, ['Latitude', 'Longitude']]
        return indices.values





    def get_easting_northing_flood_probability_band(self, easting, northing):

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
        cor1x = np.array(df.drop(['Y', 'prob_4band', 'radius'], axis=1))
        cor1y = np.array(df.drop(['X', 'prob_4band', 'radius'], axis=1))
        pro = np.array(df.drop(['X', 'Y', 'radius'], axis=1))
        r = np.array(df.drop(['X', 'Y', 'prob_4band'], axis=1))
        outputpro = []
        # normalize
        pro[pro == "High"] = 4
        pro[pro == "Medium"] = 3
        pro[pro == "Low"] = 2
        pro[pro == "Very Low"] = 1
        for m, n in zip(easting, northing):
            r_relative = np.sqrt((cor1x - m) ** 2 + (cor1y - n) ** 2)
            judge = r_relative < r
            highpro = 0
            for i in range(pro[judge].shape[0]):
                if pro[judge][i] > highpro:
                    highpro = pro[judge][i]
            outputpro.append(highpro)
        outputpro = np.array(outputpro, dtype=object)
        outputpro[outputpro == 4] = "High"
        outputpro[outputpro == 3] = "Medium"
        outputpro[outputpro == 2] = "Low"
        outputpro[outputpro == 1] = "Very Low"
        outputpro[outputpro == 0] = "Zero"

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
        postcodes = [postcode.replace(' ', '').upper().strip() for postcode in postcodes]
        postcodes = self.cat_pst_values.loc[postcodes].dropna().index
        print(postcodes)
        latLongs = self.get_lat_long(postcodes)
        print(latLongs)
        eastNorths = geo.get_easting_northing_from_lat_long(latLongs[:, 0], latLongs[:, 1])
        print(eastNorths)
        probs = self.get_easting_northing_flood_probability_band(eastNorths[0], eastNorths[1])
        print(probs)
        probsSort = pd.DataFrame({'Postcode': postcodes, 'Probability Band': probs})
        probsSort.set_index('Postcode', inplace=True)
        probsSort['Probability Band'] = pd.Categorical(probsSort['Probability Band'],
                                                       ["High", "Medium", "Low", "Very Low", "Zero"])
        probsSort = probsSort.sort_values(by=['Probability Band', 'Postcode'])
        # print(list(self.flood_risk.columns))
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
        postcodes = [postcode.replace(' ', '').upper().strip() for postcode in postcodes]
        # self.df_values_file.set_index('Postcode', inplace=True)
        indices = self.cat_pst_values.loc[postcodes, 'Total Value']
        indices = indices.div(20)
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
        for i in range(len(postcodes)):
            if postcodes[i] in self.cat_pst_values.index:
                flood_risk.append(self.cat_pst_values.loc[postcodes[i], 'Total Value'].tolist())
                if probability_bands[i] == 'High':
                    flood_risk[i] = flood_risk[i] * reduce_cost * 1 / 10
                elif probability_bands[i] == 'Medium':
                    flood_risk[i] = flood_risk[i] * reduce_cost * 1 / 50
                elif probability_bands[i] == 'Low':
                    flood_risk[i] = flood_risk[i] * reduce_cost * 1 / 100
                elif probability_bands[i] == 'Very Low':
                    flood_risk[i] = flood_risk[i] * reduce_cost * 1 / 1000
                else:
                    flood_risk[i] = 0.
            else:
                flood_risk.append(np.nan)
        print("get_annual_flood_risk")
        return np.array(flood_risk)

        """
        flood_risk = []
        reduce_cost = 0.05
        postcodes = [postcode.replace(' ', '').upper().strip() for postcode in postcodes]
        pro = np.array(probability_bands)
        pro[pro == "High"] = 1 / 10
        pro[pro == "Medium"] = 1 / 50
        pro[pro == "Low"] = 1 / 100
        pro[pro == "Very Low"] = 1 / 1000
        pro[pro == "Zero"] = 0
        flood_risk = self.cat_pst_values.loc[postcodes, 'Total Value'] * pro * reduce_cost
        print(flood_risk)
        return np.array(flood_risk)
        """

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
        eastNorths = geo.get_easting_northing_from_lat_long(latLongs[:, 0], latLongs[:, 1])
        probs = self.get_easting_northing_flood_probability_band(eastNorths[0], eastNorths[1])
        reduce_cost = 0.05
        postcodes = [postcode.replace(' ', '').upper().strip() for postcode in postcodes]
        pro = np.array(probs)
        pro[pro == "High"] = 0.1
        pro[pro == "Medium"] = 0.02
        pro[pro == "Low"] = 0.01
        pro[pro == "Very Low"] = 0.001
        pro[pro == "Zero"] = 0
        self.flood_risk = self.cat_pst_values.loc[postcodes, 'Total Value'] * pro * reduce_cost
        self.flood_risk = self.flood_risk.to_frame()
        print(self.flood_risk)
        self.flood_risk = self.flood_risk.sort_values(by=['Total Value', 'Postcode'], ascending=[False, True])
        # print(list(self.flood_risk.columns))
        self.flood_risk = self.flood_risk[~self.flood_risk.index.duplicated(keep='first')].dropna()
        # self.flood_risk.drop_duplicates(subset="", inplace=True)
        return self.flood_risk
