# -*- coding: utf-8 -*-
"""
Created on Wed May  2 17:42:14 2018

@author: jpelda
"""


def paths_to_dataframe(gdf_nodes, gdf_edges):
    """Brings all paths to dataframe with values of edges

    ARGS:

    gdf_nodes: geopandas.GeoDataFrame()
        gdf_nodes['path_to_end_node']
    gdf_edges: geopandas.GeoDataFrame()
        gdf_edges['u'], gdf_edges['v']

    RETURNS:

    gdf: geopandas.GeoDataFrame()
        gdf contains all information of gdf_edges and only edges according
        to gdf_nodes['path_to_end_node']
    """

    gdf = gdf_edges[:0]

    # Forms a list of tuple from odd or uneven list.
    uv = [(x, arr[i+1]) if i < len(arr) - 1 else () for arr in
          gdf_nodes['path_to_end_node'] for i, x in enumerate(arr)]

    # Deletes last empty () if existant.
    if uv[-1] == ():
        del uv[-1]

    gdf = gdf_edges[:0]
    for vec in uv:
        for index, item in gdf_edges.iterrows():
            if vec == (item['u'], item['v']) or vec == (item['v'], item['u']):
                gdf = gdf.append(item)

    return gdf
