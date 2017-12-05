# Export long profiles of experimental channels
# ADW 2017.12.04

# PYTHON
import numpy as np
import os
# GRASS
from grass.pygrass.modules.shortcuts import general as g
from grass.pygrass.modules.shortcuts import raster as r
from grass.pygrass.modules.shortcuts import vector as v
from grass.pygrass.modules.shortcuts import miscellaneous as m
from grass.pygrass.gis import region
from grass.pygrass import vector
from grass.script import vector_db_select
from grass.pygrass.vector import Vector, VectorTopo
from grass.pygrass.raster import RasterRow
from grass.pygrass import utils
from grass import script as gscript

channels = sorted( gscript.parse_command('g.list', type='vector', pattern='channel_centerline_0*').keys() )
for channel in channels:
    channel_points = channel[:-7] + 'points_' + channel[-7:]
    v.to_points(input=channel, output=channel_points, type='line', dmax=0.002, overwrite=True)
    v.db_addcolumn(map=channel_points, layer=2, columns='x double precision, y double precision, z double precision')
    v.to_db(map=channel_points, option='coor', columns='x,y', layer=2)
    v.what_rast(map=channel_points, layer=2, raster='DEM_'+channel[-7:], column='z')
    v.db_select(map=channel_points, layer=2, separator=',', file=channel_points+'.csv', overwrite=True)

