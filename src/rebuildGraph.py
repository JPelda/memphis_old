# -*- coding: utf-8 -*-
"""
Created on Mon May  7 10:57:25 2018

@author: jpelda
"""
import os
from Data_IO import Data_IO
import networkx as nx


Data = Data_IO(os.path.dirname(os.getcwd()) + os.sep + 'config' + os.sep + 'test_config.ini')
graph = Data.read_from_graphml('graph')

