# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 08:31:36 2018

@author: jpelda
"""
from matplotlib import rc

def plot_format():
    rc('text', usetex=True)
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