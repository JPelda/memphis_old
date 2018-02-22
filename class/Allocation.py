# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 15:54:23 2018

@author: adifischerson
"""


import pandas as pd
import shapefile
import pymysql


class Allocation:
    def __init__(self):
        pass

    def allocate_censusgrid_to_polygons(self, sql_query, engine):
        # merge censusgrid with geodata polygons
        pass

    def calculate_wastewaterflow(self, sql_query, engine):
        # TODO
        # multiply column 'Inhabitants' from db-Table "inhabitants" of DB
        # MEMPHIS_Output with newTable MEMPHIS_Input"wastewaterflow per Person"
        return wastewaterflow
        pass

    def allocate_centroids(self):
        # assign wwflow to centroids and allocate centr. to nearest Edge
            # -> comulate all wastewaterflows
        return sawageflow


if __name__ == "__main__":
    print('main')

else:
    print('else frm Allocation')
