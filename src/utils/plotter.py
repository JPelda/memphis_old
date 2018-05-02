# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 08:31:36 2018

@author: jpelda
"""
from matplotlib import rc

def plot_format():
    rc('text', usetex=False)
    rc('font', **{'family': 'Arial'})
    #        rc('font', serif='malgunbd')
    rc('ps', usedistiller='xpdf')
    rc('pdf', fonttype=42)
    rc('ps', fonttype=42)
    rc('figure', figsize = [4, 2.25])
    grid_linewidth = 0.3
    xyLabelsize=8
    labelsize = 8
    rc('lines', lw = 1.3, c='r', ls='-', dash_capstyle='round',
       solid_capstyle='round')
    rc('axes', grid=False, lw=grid_linewidth)
    rc('grid', ls='dotted', lw=grid_linewidth, alpha=1)
    rc('xtick', direction='in', labelsize=labelsize)
    rc('xtick.major', width=grid_linewidth, size=5)
    rc('xtick.minor', width=grid_linewidth, size=4)
    rc('xtick', labelsize=xyLabelsize)
    rc('ytick', direction='in', labelsize=labelsize)
    rc('ytick.major', width=grid_linewidth, size=5)
    rc('ytick.minor', width=grid_linewidth, size=4)
    rc('ytick', labelsize=xyLabelsize)
    rc('legend', fontsize='small')


def color_map():
    '''From https://matplotlib.org/examples/pylab_examples/custom_cmap.html '''
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    cdict3 = {'red': ((0.0, 0.0, 1),
#                      (0.25, 0.0, 1),
#                      (0.5, 0.0, 0.0),
#                      (0.75, 0.75, 0.75),
                      (1.0, 1.0, 1.0)),

              'green': ((0.0, 0.0, 1),
#                        (0.25, 0.0, 1),
#                        (0.5, 0.0, 0.0),
#                        (0.75, 0.0, 0.0),
                        (1.0, 0.0, 0.0)),

              'blue': ((0.0, 0.0, 1),
#                       (0.25, 0.0, 1),
#                       (0.5, 0.0, 0.0),
#                       (0.75, 0.0, 0.0),
                       (1.0, 0.0, 0.0))}

    # Make a modified version of cdict3 with some transparency
    # in the middle of the range.
    cdict4 = cdict3.copy()
    cdict4['alpha'] = ((0.0, 1.0, 1.0),
                    #   (0.25,1.0, 1.0),
                       (0.5, 0.3, 0.3),
                    #   (0.75,1.0, 1.0),
                       (1.0, 1.0, 1.0))
    # Now we will use this example to illustrate 3 ways of
    # handling custom colormaps.

    # Third, for LinearSegmentedColormap only,
    # leave everything to register_cmap:

    plt.register_cmap(name='WhiteRed', data=cdict3)  # optional lut kwarg
#    plt.register_cmap(name='BlueRedAlpha', data=cdict4)
