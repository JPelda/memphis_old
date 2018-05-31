# -*- coding: utf-8 -*-
"""
Created on Thu May 31 11:46:47 2018

@author: jpelda
"""
import numpy as np


class Clustering():

    def __init__(self):
        pass

    def count_val_over_key(self, gdf, keys, keys_name='inhabs'):
        '''Clusters points to -1, 0, 5, 10, 15... by its inhabs as
            gdf,keys()

        ARGS:
        -----
        gdf: geopandas.DataFrame()
            Data that are clustered by keys
        keys: set
            Are the keys the gdf is clustered by.

        KWARGS:
        ------
        keys_name: str
            The name of values of keys. Must also be given as col name in gdf.

        RETURNS:
        --------
        rang: dict
            dict.keys == cluster_keys, dict.values == len(items of gdfs) per
            cluter_key
        '''

        rang = np.arange(0, np.around(max(keys), decimals=-1) + 5, 5)
        rang = np.insert(rang, 0, -1)
        rang = {key: 0 for key in rang}

        cluster = {key: gdf[gdf[keys_name] == key] for key in keys}

        for key, obj in cluster.items():
            val = len(obj[keys_name])
            if key == -1:
                rang[key] += val
            else:
                rang[int((np.around(key / 5, decimals=0) * 5))] += val
        return rang

    def V_of_best_pts_within_overlay_pts(self, gdf, gdf_orig, buffer):
        '''Selects pts in gdf, that match to pts in gdf_orig,
        clustered to 0.25, 0.5, 0.75, 1....

        ARGS:
        -----
        gdf: geopandas.DataFrame()
            gdf with col 'geometry' that is matched with gdf_orig.
        gdf_orig: geopandas.DataFrame()
            gdf with col 'geometry' gdf is matched to.
        buffer: float
            Buffer around gdf_orig['geometry'] in [m].

        RETURNS:
        rang: gdf
        '''
        # TODO mark keys, where no V of sewage system exists.
        keys = set(gdf_orig.V)
        rang = np.arange(0, np.around(max(keys), decimals=3), 0.25)
        rang = np.insert(rang, 0, -1)
        rang = {key: [] for key in rang}

        gdf_o = gdf_orig[gdf_orig['inhabs'] >= 0]
        gdf_ = gdf[gdf['inhabs'] >= 0]

        geos = gdf_o['geometry'].buffer(buffer)

        sindex = gdf_.sindex

        for i, (geo, V) in enumerate(zip(geos, gdf_o['V'])):
            print("\rLeft:{:>10}".format(len(geos) - i), end='')

            if isinstance(V, (float, int)) and V != np.nan:
                poss_matches_i = list(sindex.intersection(geo.bounds))

                if poss_matches_i != []:
                    poss_matches = gdf_.iloc[poss_matches_i]
                    idx = np.abs(poss_matches.V - V).values.argmin()
                    rang[np.around(V / 0.25, decimals=0) * 0.25].append(
                                poss_matches.iloc[idx].V)

        return rang
