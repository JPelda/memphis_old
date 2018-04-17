# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 15:54:23 2018

@author: adifischerson
"""


import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import pymysql


class Allocation:
    def __init__(self):
        pass

    def allocate_censusgrid_to_polygons(self, polygons, census):
        '''
        input:   polygons as np.array([Polygon(coords), area])
                 census as np.array([Polygon(x0, y0, x1, y1]))
        All innputs must be in same coordinate system. Output is the input's
        coordinate system
        
        output:  ('polygons', inhab)
        Order of output array of polygons is same like input array of polygons.
        '''
        intersections = polygons.overlay(polygons, census, how="intersection")
        '''
        res_intersection = gpd.overlay(df1, df2, how='intersection')
        
        res_intersection
           df1  df2                             geometry
        0    1    1  POLYGON ((2 1, 1 1, 1 2, 2 2, 2 1))
        1    2    1  POLYGON ((3 3, 3 2, 2 2, 2 3, 3 3))
        2    2    2  POLYGON ((3 4, 4 4, 4 3, 3 3, 3 4))
        '''
        polys = gpd.overlay(polygons, census, how="intersection")
        # TODO Do something with polys, see docs for gpd.overlay()

        return x, y, inhab

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
    pass
