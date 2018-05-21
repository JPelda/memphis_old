# -*- coding: utf-8 -*-
"""
Created on Thu May 17 10:16:32 2018

@author: jpelda
"""
import sys
import os

import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.lines as mlines

sys.path.append(os.getcwd() + os.sep + 'src')
sys.path.append(os.getcwd() + os.sep + 'src' + os.sep + 'utils')
from plotter import plot_format, color_map

G = nx.Graph()
G.add_nodes_from([0, 1, 2, 3, 4, 5])
G.add_edges_from([(0, 1, {'length': 1}),
                  (1, 2, {'length': 1}),
                  (2, 5, {'length': 3}),
                  (1, 5, {'length': 5}),
                  (5, 3, {'length': 2}),
                  (5, 4, {'length': 1})])


G.nodes[0]['geometry'] = (3, 0)
G.nodes[1]['geometry'] = (2, 2)
G.nodes[2]['geometry'] = (2, 5)
G.nodes[3]['geometry'] = (4, 6)
G.nodes[4]['geometry'] = (5.5, 3.5)
G.nodes[5]['geometry'] = (5, 3)

G.nodes[0]['inhab'] = 'inhabitants: 20'
G.nodes[1]['inhab'] = 'inhabitants: 25'
G.nodes[2]['inhab'] = 'inhabitants: 40'
G.nodes[3]['inhab'] = 'inhabitants: 15'
G.nodes[4]['inhab'] = 'inhabitants: 10'
G.nodes[5]['inhab'] = 'inhabitants: 8'

plot_format()
pos = nx.spring_layout(G)

fig, ax = plt.subplots()
plt.axis('off')
shortest_path = []
shortest_path.append(nx.shortest_path(G, source= 3, target=0, weight='length'))
shortest_path.append(nx.shortest_path(G, source= 4, target=0, weight='length'))

edges = []
for item in shortest_path:
    i = 0
    for i, x in enumerate(item):
        if i + 1 < len(item):
            xy = (x, item[i + 1])
        else:
            break
        edges.append(xy)

nx.draw_networkx(G, pos=pos, ax=ax, node_color='#6D89CB')

#nx.draw_networkx_labels(G, pos=pos, labels=nx.get_node_attributes(G, 'inhab')) 
nx.draw_networkx_edge_labels(G, pos=pos, edge_color='black',
                        ax=ax, edge_labels=nx.get_edge_attributes(G, 'length'),
                        font_family='cmb', font_size=10)
nx.draw_networkx(G, pos=pos, ax=ax, edgelist=edges, node_color='#6D89CB',
                 edge_color='tomato', width=2)

x = [xy[0] for xy in pos.values()]
y = [xy[1] for xy in pos.values()]
for xy, lab in zip(pos.values(), nx.get_node_attributes(G, 'inhab').values()):
    plt.text(xy[0], xy[1]-0.2, s=lab)
    
shortest_path = mlines.Line2D([], [], color='tomato', linestyle='-',
                              label='Shortest paths')
nodes = mlines.Line2D([], [], color='#6D89CB', marker='o', linestyle='',
                    markersize=15,label="Nodes, with node's number")
edges = mlines.Line2D([], [], color='black', linestyle='-',
                      label="Edges, with edge's geologic length")
                      
handles= [shortest_path] + [nodes] + [edges]
ax.legend(handles=handles, loc='upper right', ncol=1, mode='')

plt.show()