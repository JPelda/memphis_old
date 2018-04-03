# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 14:47:54 2018

@author: adifischerson
"""


import pandas as pd



class Conditioning:
    def __init__(self):
        pass

#    def read_polygon_from_shp(self, shapefile):
#        #TODO read buildingsshp(shapefile, fiona, or ogr)of bbox selection
#        pass

    def get_centroid(self, df):
        # TODO calculate centroid from polygon
        # gets polygons
        # returns centroids as df dataframe
        return df



    def transform_coords(self, x, y, from_coord, into_coord):
        '''
        input:  x as []
                y as []
                from_coord as string
                into_coord as string
        out:    x as []
                y as []
        '''
        xy = transform(Proj(init=from_coord), Proj(init=into_coord), x, y)
        return xy[0], xy[1]

    def best_way_calculation(self):
        # TODO wighted graph ways + nodes find shortest way (ask Script Pascal)
        pass


if __name__ == "__main__":
    print('main')

else:
    print('else frm Conditioning')
