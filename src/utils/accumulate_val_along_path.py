# -*- coding: utf-8 -*-
"""
Created on Wed May  2 14:27:46 2018

@author: jpelda
"""


def sum_wc(gdf):
    """Accumulates the paths' water flows that pass along each node to the
    node itself.

    ARGS:

    gdf: geopandas.GeoDataFrame()
        gdf['wc'], gdf['path_to_end_node']

    RETURNS:

    list_of_sum_wc: list(floats)
        List of floats is in order of gdf_nodes
    """

    arr = [0]*len(gdf)
    for i, row in enumerate(gdf.iterrows()):
        for key in row[1]['path_to_end_node']:
            arr[i] += gdf['wc'][key]

    return arr
