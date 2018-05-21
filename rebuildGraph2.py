# -*- coding: utf-8 -*-
"""
Created on Fri May 11 10:34:51 2018

@author: jpelda
"""

import os

import osmnx
import networkx as nx
from shapely.ops import split, linemerge

from Data_IO import Data_IO



Data = Data_IO('config' + os.sep + 'test_config.ini')

# gis = Data.read_from_sqlServer('gis_roads')
# gdf_gis = gpd.GeoDataFrame(gis_roads, crs=Data.coord_system, geometry='SHAPE')
wc = Data.read_from_sqlServer('wc_per_inhab')
# Reads graph from file, shp import makes problems.
graph = Data.read_from_graphml('graph')
gdf_nodes, gdf_edges = osmnx.save_load.graph_to_gdfs(graph, nodes=True,
                                                     edges=True,
                                                     node_geometry=True,
                                                     fill_edge_geometry=True)

endpts= [[pt, u, v] for pt, u, v in zip(gdf_edges.geometry,
         gdf_edges.u, gdf_edges.v)]

import itertools
from shapely.geometry import Point, MultiPoint

nodes_id = int(max(gdf_nodes.osmid))
inters_ed = []
inters_nd = []
lines = [(geo, u, v) for geo, u, v in zip(gdf_edges.geometry,
                                          gdf_edges.u,
                                          gdf_edges.v)]

for line1, line2 in itertools.combinations(lines, 2):
    nodes_id += 1

    if  line1[0].intersects(line2[0]):

        inter = (line1[0].intersection(line2[0]), line1[1], line1[2],
                 line2[1], line2[2])

        if "Point" == inter[0].type:

            lines_parent = split(line1[0], line2[0])
            lines_child = split(line2[0], line1[0])

            if len(lines_parent) > 1:

                inters_nd += [(nodes_id, {'osmid': nodes_id,
                                          'x': inter[0].x,
                                          'y': inter[0].y})]
                inters_ed += [(inter[1], nodes_id,
                               {'geometry': lines_parent[0]}),
                              (nodes_id, inter[2],
                               {'geometry': lines_parent[1]}),
                              (inter[3], nodes_id,
                               {'geometry': lines_child[0]}),
                              (nodes_id, inter[4],
                               {'geometry': lines_child[1]})]
            else:
                pass

        elif "MultiPoint" == inter[0].type:
            '''
            g = LineString(((0,1),(2,1),(2,-1)))
            f = LineString(((1,2),(1,0),(3,0),(3,-1)))
            inter = g.intersection(f)
            print(inter)
            MULTIPOINT (1 1, 2 0)
            '''

            lines_parent = split(line1[0], inter[0])
            lines_child = split(line2[0], inter[0])

            inters_nd += [(nodes_id, {'osmid': nodes_id,
                                          'x': inter[0][0].x,
                                          'y': inter[0][0].y})]
            inters_ed += [(inter[1], nodes_id, {'geometry': lines_parent[0]}),
                          (inter[3], nodes_id, {'geometry': lines_child[0]})]

            for l_p, l_c in zip(list(lines_parent)[1:-1],
                                list(lines_child)[1:-1]):
                v = nodes_id + 1

                if l_p.length <= l_c.length:
                    line = l_p
                else:
                    line = l_c

                inters_nd += [(v, {'osmid': v,
                                   'x': line.coords[1][0],
                                   'y': line.coords[1][1]})]
                inters_ed += [(nodes_id, v, {'geometry': line})]

                nodes_id = v

            inters_ed += [(nodes_id, inter[2], {'geometry': lines_parent[-1]}),
                          (nodes_id, inter[4], {'geometry': lines_child[-1]})]

        elif "MultiLineString" == inter[0].type:

            pts = [(Point(line.coords[0]), Point(line.coords[-1]))
                   for line in inter[0]]

            pts = [x for sublist in pts for x in sublist]
            pts = MultiPoint(pts)

            lines_parent = split(line1[0], pts)
            lines_child = split(line2[0], pts)

            inters_nd += [(nodes_id, {'osmid': nodes_id,
                                      'x': pts[0].x,
                                      'y': pts[0].y})]
            inters_ed += [(inter[1], nodes_id, {'geometry': lines_parent[0]}),
                          (inter[3], nodes_id, {'geometry': lines_child[0]})]

            for l_p, l_c in zip(list(lines_parent)[1:-1],
                                list(lines_child)[1:-1]):
                v = nodes_id + 1

                if l_p.length <= l_c.length:
                    line = l_p
                else:
                    line = l_c

                inters_nd += [(v, {'osmid': v,
                                   'x': line.coords[1][0],
                                   'y': line.coords[1][1]})]
                inters_ed += [(nodes_id, v, {'geometry': line})]

                nodes_id = v

            inters_ed += [(nodes_id, inter[2], {'geometry': lines_parent[-1]}),
                          (nodes_id, inter[4], {'geometry': lines_child[-1]})]

        elif "GeometryCollection" == inter[0].type:

            pts = []

            for geom in inter[0]:

                if "Point" == geom.type:
                    pts.append(geom)

                elif "MultiPoint" == geom.type:
                    pts.extend([pt for pt in geom])

                elif "MultiLineString" == geom.type:
                    p = [(Point(line.coords[0]), Point(line.coords[-1]))
                            for line in geom]
                    p = [x for sublist in p for x in sublist]

            pts = MultiPoint(pts)
            lines_parent = split(line1[0], pts)
            lines_child = split(line2[0], pts)

            inters_nd += [(nodes_id, {'osmid': nodes_id,
                                          'x': pts[0].x,
                                          'y': pts[0].y})]
            inters_ed += [(inter[1], nodes_id, {'geometry': lines_parent[0]}),
                          (inter[3], nodes_id, {'geometry': lines_child[0]})]

            for l_p, l_c in zip(list(lines_parent)[1:-1],
                                list(lines_child)[1:-1]):
                v = nodes_id + 1

                if l_p.length <= l_c.length:
                    line = l_p
                else:
                    line = l_c

                inters_nd += [(v, {'osmid': v,
                                   'x': line.coords[1][0],
                                   'y': line.coords[1][1]})]
                inters_ed += [(nodes_id, v, {'geometry': line})]

                nodes_id = v

            inters_ed += [(nodes_id, inter[2], {'geometry': lines_parent[-1]}),
                          (nodes_id, inter[4], {'geometry': lines_child[-1]})]
for item in inters_ed:
    item[2].update({'osmid': -1, 'highway': -1, 'service': '', 'oneway': False,
        'length': item[2]['geometry'].length})

graph.add_nodes_from(inters_nd)
graph.add_edges_from(inters_ed)

#osmnx.plot_graph(graph)