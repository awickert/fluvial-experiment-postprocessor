#! /usr/bin/env python

# Process DEMs after they are already imported
# Run after workflow_April_2018.sh
# And then run longProfile_2018.py

# Clips DEM boundaries and adds a border for use to get long profiles

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
from grass.script import array as garray

# Characteristics of basin; these should be set externally
length_y = 2401
length_x = 3936

margin_top = 2110
margin_bottom = 410
margin_left = 300
margin_right = 3700

# Existing full-extent DEMs
DEMs_fullextent = gscript.parse_command('g.list', type='raster', pattern='DEM_fullextent_0??????').keys()
DEMs_fullextent = sorted(DEMs_fullextent)

# x and y values across basin and more
length_y_trimmed = margin_top - margin_bottom
length_x_trimmed = margin_right - margin_left

# Full-extent region: get x and y
g.region(raster=DEMs_fullextent[0])
try:
  r.mapcalc('x = x()')
  r.mapcalc('y = y()')
except:
  pass
g.region(flags='d')

# Set region to limited area 
g.region(n=margin_top/1000., s=margin_bottom/1000., w=margin_left/1000., e=margin_right/1000., res=0.001)
reg = gscript.region()

# Create DEM with limited extent
for DEM in DEMs_fullextent:
    mcstr = 'DEM_'+DEM.split('_')[-1]+' = '+DEM
    print mcstr
    r.mapcalc(mcstr, overwrite=True)

# Ready long profiles
g.region(w=reg['w']-2*reg['ewres'], e=reg['e']+2*reg['ewres'], s=reg['s']-2*reg['nsres'], n=reg['n']+2*reg['nsres'], save='with_boundaries', overwrite=True)

# CUSTOM COMMANDS HERE TO CREATE WALL BASED ON X AND Y POSITIONS
# THIS SHOULD ALSO BE PRE-DEFINED WHEN THIS IS FINISHED
# Keep right boundary open
mcstr = "boundaries = (x < "+str(margin_left/1000.)+") + "+ \
                     "(y < "+str(margin_bottom/1000.)+") + "+ \
                     "(y > "+str(margin_top/1000.)+")"
r.mapcalc(mcstr, overwrite=True)
r.mapcalc("boundaries = boundaries > 0", overwrite=True) # Logical 0/1
r.null(map='boundaries', setnull=0)

