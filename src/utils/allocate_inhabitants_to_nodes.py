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

    gdf_nodes_spatial_index = gdf_nodes.sindex
    dic = {key: 0 for key in gdf_nodes.index}
    for i, (geo, poly, inhab) in enumerate(
                                        zip(gdf_raster['SHAPE'],
                                            gdf_raster['SHAPE_b'],
                                            gdf_raster['inhabs'])):
        if inhab <= 0:
            continue
        else:
            possible_matches_index = list(
                            gdf_nodes_spatial_index.intersection(geo.bounds))

            if possible_matches_index != []:
                val = inhab / len(possible_matches_index)
                for key in possible_matches_index:
                    dic[key] += val
            else:
                key = get_nearest_node(graph, (geo.y, geo.x))
                dic[key] += inhab

    list_of_inhabs = [dic[key] for key, item in gdf_nodes.iterrows()]
    return list_of_inhabs
