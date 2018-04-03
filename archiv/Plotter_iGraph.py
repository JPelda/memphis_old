#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 16:46:46 2017

@author: johannes
"""

from igraph import Graph
from igraph import plot
import matplotlib.pyplot as plt
import matplotlib.colors as mcol
import matplotlib.cm as cm


class plot_DHS_as_iGraph():
    def __init__(self, edges, Q, m, elements_vs, colors_vs,
                 names_es=None, names_vs=None):
        '''
        edges = [(,)]
        Q = []
        m = []
        names_es = []
        names_vs = []
        elements_vs = []
        colors_vs = {elements_vs[i]:string}
        '''

        self.g = Graph(edges)
        self.g.es['Q'] = Q
        self.g.es['m'] = m
        self.g.es['name'] = names_es
        self.g.vs['name'] = names_vs
        self.g.vs['element'] = elements_vs
        self.vertexColor = colors_vs

        self.colorMap = self.color_map()
        self.visualStyle = self.visual_style()

    def visual_style(self):
        visualStyle = {}
        visualStyle['bbox'] = (300, 300)
#        visualStyle['scale'] = 2000
        visualStyle['label_size'] = 10
        visualStyle['label_dust'] = 2
        visualStyle["edge_width"] = [m / 100 for m in self.g.es['m']]
        visualStyle["edge_color"] = [self.colorMap.to_rgba(Q) for Q in
                                     self.g.es['Q']]
        visualStyle["edge_arrow_size"] = 1200
        visualStyle["edge_label"] = self.g.es['name']
        visualStyle["vertex_color"] = [self.vertexColor[element]
                                       for element in self.g.vs['element']]
        visualStyle["vertex_label"] = self.g.vs["name"]
        return visualStyle

    def color_map(self):
        # see at https://stackoverflow.com/questions/25748183/python-making
        # color-bar-that-runs-from-red-to-blue
        tim = range(min(self.g.es['Q']), max(self.g.es['Q']))
        # Make a user-defined colormap.
        cm1 = mcol.LinearSegmentedColormap.from_list("MyCmapName", ["r", "b"])
        # Make a normalizer that will map the time values from
        # [start_time,end_time+1] -> [0,1].
        cnorm = mcol.Normalize(vmin=min(tim), vmax=max(tim))

        # Turn these into an object that can be used to map time values to
        # colors and can be passed to plt.colorbar().
        cpick = cm.ScalarMappable(norm=cnorm, cmap=cm1)
        cpick.set_array([])
        return cpick

    def get_shortest_paths(self, start, end, weights=None):
        sp_vs = self.g.get_shortest_paths(start, end, weights=weights)
        return sp_vs

    def akkumulateAttralongPath_saveTovsAttr(self, attr, path):
        self.g.vs[attr] = 0
        i = 0
        while i < len(path) - 1:
            eid = self.g.get_eid(path[i], path[i+1])
            self.g.vs[path[i+1]][attr] = self.g.es[eid][attr] +\
                self.g.vs[path[i]][attr]

#            print('\r' + "akkumulate vertex" + str(self.g.vs[path[i+1]])
#            + ': ' + str(self.g.vs[path[i+1]][attr]), end='')
        # TODO take care that no edge is counted double!
            print("akkumulated " + attr + " of vertex " +
                  str(self.g.vs[path[i+1]]['name']) +
                  ': ' + str(self.g.vs[path[i+1]][attr]), end='\n')
            i = i + 1


if __name__ == "__main__":

    edges = [(0, 1), (0, 2), (2, 3), (3, 4),
             (4, 2), (2, 5), (5, 0), (6, 3), (5, 6)]
    Q = [1500, 1400, 2000, 3000, 2500, 4000, 5000, 6000, 5500]
    m = [100, 100, 1000, 250, 350, 200, 600, 600, 200]
    names_es = ['n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n7', 'n8', 'n9']
    names_vs = ['K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'K7', 'K8', 'K9']
    elements_vs = ['consumer']*4 + ['node']*5
    colors_vs = {'consumer': 'red', 'node': 'violet'}

    network = plot_DHS_as_iGraph(edges, Q, m, elements_vs, colors_vs,
                                 names_es=names_es, names_vs=names_vs)

    path = network.get_shortest_paths(0, 3, weights=m)[0]
    network.akkumulateAttralongPath_saveTovsAttr('Q', path)

    network.g.write_lgl('test_graph')
    F = plt.figure()

    fig = plot(network.g, **network.visualStyle, target="testGraph.pdf")
    fig.show()

else:
    pass
