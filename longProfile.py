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

# Get LP with only a main channel (no trib channel)
DEMs = gscript.parse_command('g.list', type='raster', pattern='*__DEM__*').keys()
DEMs = sorted(DEMs)
for DEM in DEMs:
  print DEM
  r.patch(input='boundaries,'+DEM, output='tmp', overwrite=True)
  drainarray.read('tmp')
  scanName = DEM.split('__DEM__')[0]
  mainThalweg = scanName + '__main_thalweg__'
  tribThalweg = scanName + '__trib_thalweg__'
  # Main channel
  start_x = margin_left/1000. + .1
  start_y = _y[:,1][drainarray[:,1] == np.min(drainarray[:,1])]
  flowIn = garray.array()
  flowIn[:] = ( (_x <= (margin_left/1000. + .01)) * (_x > _x[0,1]) ) * (_y >= 1.28) * (_y <= 1.30)
  flowIn.write('tmpFlowIn', overwrite=True)
  # Must fix here: some cells on wall at boundary
  r.watershed(elevation='tmp', flow='tmpFlowIn', threshold=np.sum(flowIn), stream='tmpStream', accumulation='tmpAccum', flags='s', quiet=True, overwrite=True)
  r.mapcalc('tmpStreamZ = (tmpStream * 0 + 1) * tmp', quiet=True, overwrite=True)
  r.to_vect(input='tmpStreamZ', output='Line__'+DEM, type='line', quiet=True, overwrite=True)
  r.to_vect(input='tmpStreamZ', output='Points__'+DEM, type='point', column='z', quiet=True, overwrite=True)
  v.db_addcolumn(map='Points__'+DEM, columns='x double precision, y double precision', quiet=True)
  v.to_db(map='Points__'+DEM, option='coor', columns='x,y',  quiet=True)

channels = sorted( gscript.parse_command('g.list', type='vector', pattern='channel_centerline_0*').keys() )
for channel in channels:
    channel_points = channel[:-7] + 'points_' + channel[-7:]
    v.to_points(input=channel, output=channel_points, type='line', dmax=0.002, overwrite=True)
    v.db_addcolumn(map=channel_points, layer=2, columns='x double precision, y double precision, z double precision')
    v.to_db(map=channel_points, option='coor', columns='x,y', layer=2)
    v.what_rast(map=channel_points, layer=2, raster='DEM_'+channel[-7:], column='z')
    v.db_select(map=channel_points, layer=2, separator=',', file=channel_points+'.csv', overwrite=True)

