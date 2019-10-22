"""Locator functions to interact with geographic data"""
import pandas as pd
import numpy as np
from functools import reduce
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
        self.get_lat_long_lst = []
        self.get_e_n_flood_prob_band = []
        if postcode_file != None:
            self.df_postcode_file = pd.read_csv("resources/" + postcode_file, header=1, names=["Postcode", "Lat", "Long"])
            # formatting the postcode column of postcodes file
            self.df_postcode_file.Postcode = self.df_postcode_file.Postcode.str.replace(' ',
                                                                                        '')  # delete space in postcodes strings
            self.df_postcode_file.Postcode = self.df_postcode_file.Postcode.str.strip()
            self.df_postcode_file.Postcode = self.df_postcode_file.Postcode.str.upper()

        if risk_file != None:
            self.df_risk_file = pd.read_csv("resources/" + risk_file)
        if values_file != None:
            self.df_values_file = pd.read_csv("resources/" + values_file)
            # formatting the postcode column of property file
            self.df_values_file.Postcode = self.df_values_file.Postcode.str.replace(' ',
                                                                                    '')  # delete space in postcodes strings
            self.df_values_file.Postcode = self.df_values_file.Postcode.str.strip()
            self.df_values_file.Postcode = self.df_values_file.Postcode.str.upper()

        # merge two
        # self.cat_pst_values = self.df_postcode_file.append(self.df_values_file, ignore_index=True, sort=False)

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
        """
                postcodes = [postcode.replace(' ', '').upper().strip() for postcode in postcodes]
                print(postcodes)
                print(self.df_postcode_file[self.df_postcode_file['Postcode'].isin(postcodes)])

                lst = reduce(pd.DataFrame.append, map(lambda i : self.df_postcode_file[self.df_postcode_file.Postcode == i],
                                                      postcodes))

                print(len(postcodes))

                if len(lst) == len(postcodes):
                    for i, r in lst.iterrows():
                        # self.get_lat_long_lst.append([lst.loc[i[0], 'Lat'], [lst.loc[i[0], 'Long']]])
                        self.get_lat_long_lst.append([r['Lat'], r['Long']])
                    return np.array(self.get_lat_long_lst)

                idx = 0
                if len(lst) == 0:
                    while idx != len(postcodes):
                        self.get_lat_long_lst.append([np.nan, np.nan])
                        idx += 1
                else:
                    for i, r in lst.iterrows():
                        while (r['Postcode']) != (postcodes[idx]):
                            self.get_lat_long_lst.append([np.nan, np.nan])
                            idx += 1
                            if idx == len(postcodes):
                                break
                        if idx == len(postcodes):
                            break
                        self.get_lat_long_lst.append([r['Lat'], r['Long']])
                        idx += 1
                    if idx != len(postcodes):
                        while idx != len(postcodes):
                            self.get_lat_long_lst.append([np.nan, np.nan])
                            idx += 1
                        #self.get_lat_long_lst.append([r['Lat'], r['Long']])

                print(self.get_lat_long_lst)
                print("get_lat_long OK")
                return np.array(self.get_lat_long_lst)
                """
        # get index in cat_pst_values that contains postcodes
        postcodes = [postcode.replace(' ', '').upper().strip() for postcode in postcodes]
        self.df_postcode_file.set_index('Postcode', inplace=True)
        indices = self.df_postcode_file.loc[postcodes]
        # indices = indices.drop(index, axis = 1)
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
        df = pd.read_csv("resources/flood_probability.csv",
                         header=1, names=["Del", "X", "Y", "prob_4band", "radius"])
        cor1x = np.array(df.drop(['Del', 'Y', 'prob_4band', 'radius'], axis=1))
        cor1y = np.array(df.drop(['Del', 'X', 'prob_4band', 'radius'], axis=1))
        pro = np.array(df.drop(['Del', 'X', 'Y', 'radius'], axis=1))
        r = np.array(df.drop(['Del', 'X', 'Y', 'prob_4band'], axis=1))
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

        # 000
        """lst = self.df_risk_file[self.df_risk_file['X'].isin(easting) & self.df_risk_file['Y'].isin(northing)]
        print(lst)
        lst = lst.index.tolist()

        for idx in lst:
            # add algorithm
            self.get_e_n_flood_prob_band.append([self.df_risk_file.loc[idx, 'prob_4band']])
        if len(lst) == 0:
            return ['Zero']
        return [self.df_risk_file.loc[lst[0], 'prob_4band']]"""




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
        probabilities = 1


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
        self.df_values_file.set_index('Postcode', inplace=True)
        indices = self.df_values_file.loc[postcodes, 'Total Value']
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
        raise NotImplementedError

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
        raise NotImplementedError
