# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 16:15:52 2018

@author: jpelda
"""

import osmnx as ox
import igraph

G = ox.graph_from_place('Goettingen, Germany')
nodes = ox.graph_to_gdfs(G, edges=False)
print(len(nodes))

#visual_style = {}
#visual_style["vertex_size"] = 5
#visual_style["vertex_shape"] = "circle"
#visual_style["layout"] = 'lgl'
#visual_style["bbox"] = (1024, 1024)
#visual_style["margin"] = 10
#layout = G.layout('kk')
fig = igraph.plot(G, vertex_size=3)
fig.show()
print(nodes[['x', 'y']])