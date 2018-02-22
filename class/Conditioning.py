# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 14:47:54 2018

@author: adifischerson
"""


import pandas as pd
import shapefile
import pymysql


class Conditioning:
    def __init__(self):
        pass

#    def read_polygon_from_shp(self, shapefile):
#        #TODO read buildingsshp(shapefile, fiona, or ogr)of bbox selection
#        pass

    def get_centroid(self, sql_query, engine):
        # TODO calculate centroid from polygon
        # gets polygons
        # returns centroids as df dataframe
        return centroid

    def save_centroid(self, sql, engine):
        # TODO save in centrois Points (x,y) in df

        pass  # hier oder in Main Bereich Output??

    def transform_coords(self, x, y, coord_system):
        # MYSQL_transf_coords py
        return x, y

    def best_way_calculation(self):
        # TODO wighted graph ways + nodes find shortest way (ask Script Pascal)
        pass


if __name__ == "__main__":
    print('main')

else:
    print('else frm Conditioning')
