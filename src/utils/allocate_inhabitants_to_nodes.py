# -*- coding: utf-8 -*-
"""
Created on Wed May  2 11:32:35 2018

@author: jpelda
"""
from osmnx import get_nearest_node

def allocate_inhabitants_to_nodes(gdf_raster, gdf_nodes, graph):
    """Allocates inhabitans to nodes. Nodes in same raster field will get
    raster's inhabitans divided by amout of nodes within raster. Raster fields
    without nodes are allocated to nearest node.
    
    ARGS:

    gdf_raster: geopandas.GeoDataFrame()
        gdf['SHAPE'], gdf['SHAPE_b'], gdf['inhabs']
    gdf_nodes: geopandas.GeoDataFrame()
        gdf['osmid'], gdf['geometry']
    graph: nx.Graph()

    RETURNS:

    list_of_inhabs: list(floats)
        List of floats is in order of gdf_nodes
    """

    p_within = [0]*len(gdf_raster['SHAPE'])
    gdf_nodes_osmid_geometry = {int(osmid): geo for osmid, geo in zip(
        gdf_nodes['osmid'], gdf_nodes['geometry'])}
    dic = {index: 0 for index, items in gdf_nodes.iterrows()}
    for i, (point, poly, inhab) in enumerate(zip(gdf_raster['SHAPE'],
                                                 gdf_raster['SHAPE_b'],
                                                 gdf_raster['inhabs'])):
        if inhab <= 0:
            continue
        else:
            p_within[i] = {osmid: inhab for osmid, p in
                           zip(gdf_nodes_osmid_geometry.keys(),
                               gdf_nodes_osmid_geometry.values()) if
                           p.within(poly)}
            if p_within[i] != {}:
                val = list(p_within[i].values())[0] / len(p_within[i])
                p_within[i] = dict.fromkeys(p_within[i], val)
                for key, val in p_within[i].items():
                    dic[key] += val
                    del gdf_nodes_osmid_geometry[key]
            else:
                key = get_nearest_node(graph, (point.y, point.x))
                dic[key] += inhab
    list_of_inhabs = [dic[key] for key, item in gdf_nodes.iterrows()]
    return list_of_inhabs
