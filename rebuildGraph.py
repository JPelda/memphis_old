# -*- coding: utf-8 -*-
"""
Created on Mon May  7 10:57:25 2018

@author: jpelda
"""
import os
import sys
import networkx as nx
import osmnx
from shapely.geometry import Point, LineString, MultiLineString
from shapely.ops import split, linemerge
import matplotlib.pyplot as plt

sys.path.append(os.getcwd() + os.sep + 'src')
print(os.getcwd() + os.sep + 'class')
sys.path.append(os.getcwd() + os.sep + 'src' + os.sep + 'utils')
from Data_IO import Data_IO


def get_intersections(gdf_edges):

    intersec = [0] * len(gdf_edges.geometry)

    for i, line in enumerate(gdf_edges.geometry):
        print("\r{}".format(i), end='')
        dic = {}
        s_p = Point(line.xy[0][0], line.xy[1][0])
        e_p = Point(line.xy[0][-1], line.xy[1][-1])
        dic = {j: l.intersection(line) for j, l in
               zip(gdf_edges.index[i+1:], gdf_edges.geometry[i+1:]) if
               (l.intersects(line) != False and
               l.intersection(line) != s_p and
               l.intersection(line) != e_p)}

        intersec[i] = dic
    print()
    return intersec


Data = Data_IO('config' + os.sep + 'test_config.ini')
graph = Data.read_from_graphml('graph')
n, e = osmnx.save_load.graph_to_gdfs(graph)

isec = get_intersections(e[:])


for index, dic in enumerate(isec):
#    print("\rindex: {}".format(index), end="")

    for i, (key, val) in enumerate(dic.items()):

        node =  max(n.index)
        u_master = e.u[index]
        v_master = e.v[index]
        u_slave = e.u[key]
        v_slave = e.v[key]

        if type(val) == Point:
            print("\r{}".format(index))
            lines_master = split(e.geometry[index], e.geometry[key])
            lines_slave = split(e.geometry[key], e.geometry[index])

            G = graph
            G.add_nodes_from([(u_master, graph.nodes[u_master])])
            G.add_nodes_from([(v_master, graph.nodes[v_master])])
            G.add_nodes_from([(u_slave, graph.nodes[u_slave])])
            G.add_nodes_from([(v_slave, graph.nodes[v_slave])])

            v = node - len(lines_master) + 1
            u_m = u_master
            u_s = u_slave

            G.add_edges_from([(u_m, v,
                                  {'geometry': lines_master[0],
                                   'osmid': -1,
                                   'name': '',
                                   'highway': '',
                                   'access': '',
                                   'oneway': False,
                                   'length': lines_master[0].length})])
            G.add_edges_from([(u_s, v,
                                {'geometry': lines_slave[0],
                                   'osmid': -1,
                                   'name': '',
                                   'highway': '',
                                   'access': '',
                                   'oneway': False,
                                   'length': lines_slave[0].length})])
            u = v

            for line_m, line_s in zip(list(lines_master)[1:-1],
                                      list(lines_slave)[1:-1]):
                v += 1
                if line_m.length <= line_s.length:
                    line = line_m
                elif line_m.length > line_s.length:
                    line = line_s

                G.add_edges_from([(u, v,
                                  {'geometry': line,
                                   'osmid': -1,
                                   'name': '',
                                   'highway': '',
                                   'access': '',
                                   'oneway': False,
                                   'length': line.length})])
                u = v

            G.add_edges_from([(u, v_master,
                                  {'geometry': lines_master[-1],
                                   'osmid': -1,
                                   'name': '',
                                   'highway': '',
                                   'access': '',
                                   'oneway': False,
                                   'length': lines_master[-1].length})])

            G.add_edges_from([(u, v_slave,
                                  {'geometry': lines_slave[-1],
                                   'osmid': -1,
                                   'name': '',
                                   'highway': '',
                                   'access': '',
                                   'oneway': False,
                                   'length': lines_slave[-1].length})])

            edge_m = nx.shortest_path(G, u_master, v_master)
            edge_m_s = nx.shortest_path(G, u_master, v_slave)
            edge_s = nx.shortest_path(G, u_slave, v_slave)
            edge_s_m = nx.shortest_path(G, u_slave, v_master)
            graph = nx.compose(graph, G)

        elif type(val) == LineString or type(val) == MultiLineString:
            if type(val) == MultiLineString:
                val = linemerge(val)
            pass

        else:
            pass


n2, e2 = osmnx.save_load.graph_to_gdfs(graph)



fig, ax = plt.subplots()
#n[:].plot(ax = ax, color='black', markersize=15)
#e[:].plot(ax = ax, color='red', linewidth=4)

e2[:].plot(ax = ax, color='green')
n2[:].plot(ax = ax, color="green")


plt.show()

#G = nx.Graph()
#G.add_nodes_from([0, 1, 2, 3])
#G.add_edges_from([(0, 1), (2, 3)])
#
#G.nodes[0]['geometry'] = (0.5, 0)
#G.nodes[1]['geometry'] = (0,0.5)
#G.nodes[2]['geometry'] = (0, 0)
#G.nodes[3]['geometry'] = (1,1)
##G.nodes[4]['geometry'] = (2,2)
#folder = 'input'
#osmnx.save_graphml(graph2, 'goettingen.graphml', folder + os.sep)