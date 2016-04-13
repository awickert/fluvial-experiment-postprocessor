#! /usr/bin/env python

from Scientific.IO.NetCDF import NetCDFFile
import shutil
import os
import sys
import subprocess

# specify (existing) location and mapset
#location = "G12_NA"
gisdb    = "/data3/TerraceExperiment/grassdata"
location = "SAFL_Terraces_01"
mapset   = "PERMANENT"

# path to the GRASS GIS launch script
# MS Windows
grass7bin_win = r'C:\OSGeo4W\bin\grass71svn.bat'
# uncomment when using standalone WinGRASS installer
# grass7bin_win = r'C:\Program Files (x86)\GRASS GIS 7.0.0beta3\grass70.bat'
# Linux
grass7bin_lin = 'grass71'
# Mac OS X
# this is TODO
grass7bin_mac = '/Applications/GRASS/GRASS-7.1.app/'
 
# Location path
location_path = os.path.join(gisdb, location)
 
########### SOFTWARE
if sys.platform.startswith('linux'):
    # we assume that the GRASS GIS start script is available and in the PATH
    # query GRASS 7 itself for its GISBASE
    grass7bin = grass7bin_lin
elif sys.platform.startswith('win'):
    grass7bin = grass7bin_win
else:
    raise OSError('Platform not configured.')

if os.path.isdir(location_path):
  pass # Just do the below, shorter step.
else: 
  # Create new location (we assume that grass7bin is in the PATH)
  #  from EPSG code:
  startcmd = grass7bin+' -c '+location_path+' -e\n'
   
  print startcmd
  p = subprocess.Popen(startcmd, shell=True, \
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = p.communicate()
  if p.returncode != 0:
      print >>sys.stderr, 'ERROR: %s' % err
      print >>sys.stderr, 'ERROR: Cannot generate location (%s)' % startcmd
      sys.exit(-1)
  else:
      print 'Created location %s' % location_path
  # Now the location with PERMANENT mapset exists.
# Once mapset definitely exists
# query GRASS 7 itself for its GISBASE
startcmd = [grass7bin, '--config', 'path']

p = subprocess.Popen(startcmd, shell=False, \
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate()
if p.returncode != 0:
    print >>sys.stderr, "ERROR: Cannot find GRASS GIS 7 start script (%s)" % startcmd
    sys.exit(-1)

gisbase = out.strip('\n\r')

# Set GISBASE environment variable
os.environ['GISBASE'] = gisbase
# the following not needed with trunk
os.environ['PATH'] += os.pathsep + os.path.join(gisbase, 'extrabin')
# add path to GRASS addons
home = os.path.expanduser("~")
os.environ['PATH'] += os.pathsep + os.path.join(home, '.grass7', 'addons', 'scripts')
 
# define GRASS-Python environment
gpydir = os.path.join(gisbase, "etc", "python")
sys.path.append(gpydir)

########### DATA
# Set GISDBASE environment variable
os.environ['GISDBASE'] = gisdb
 
# import GRASS Python bindings (see also pygrass)
import grass.script as gscript
import grass.script.setup as gsetup

###########
# launch session
gsetup.init(gisbase, gisdb, location, mapset)
 
gscript.message('Current GRASS GIS 7 environment:')
print gscript.gisenv()


# -------------




import numpy as np
from matplotlib import pyplot as plt
#from pyevtk.hl import gridToVTK
from grass import script as gscript
from grass.script import array as garray
import os
import tempfile
from grass.pygrass.modules.shortcuts import general as g
from grass.pygrass.modules.shortcuts import raster as r
from grass.pygrass.modules.shortcuts import vector as v
from grass.pygrass.modules import Module
from grass.pygrass.vector import VectorTopo
import glob

# Characteristics of basin; these should be set externally
length_y = 2401
length_x = 3936

margin_top = 2110
margin_bottom = 410
margin_left = 300
margin_right = 3700

# x and y values across basin and more

#sourcedir = '/media/awickert/Elements/Fluvial 2015/151109_MC_IW_01/Processed/'
#sourcedir = '/media/awickert/data3/TerraceExperiment/Fluvial 2015/151109_MC_IW_01/Processed/'
#sourcedirs = sorted(next(os.walk('/media/awickert/data3/TerraceExperiment/Fluvial 2015/'))[1])
#sourcedirs = sorted(glob.glob('/data3/TerraceExperiment/Forgotten/*/Processed/'))
sourcedirs = sorted(glob.glob('/data3/TerraceExperiment/Fluvial 2015/*/Processed/'))

length_y_trimmed = margin_top - margin_bottom
length_x_trimmed = margin_right - margin_left

g.region(w=margin_left/1000., e=margin_right/1000., s=margin_bottom/1000., n=margin_top/1000., res=0.001, flags='s')

# Maps of x and y
g.region(w=0, s=0, e=int(np.floor(margin_right*1.5))/1000., n=int(np.floor(margin_top*1.5))/1000.)
try:
  r.mapcalc('x = x()')
  r.mapcalc('y = y()')
except:
  pass
g.region(flags='d')

errordirs = []
errorfiles = []
for sourcedir in sourcedirs:
  DATpaths = sorted(glob.glob(sourcedir+'*.DAT'))
  for DATpath in DATpaths:
    # Name
    DATfile = os.path.split(DATpath)[-1]
    scanName, scanNumber = DATfile.split('_Composite')[0].split('_Scan')
    scanNameDEM_fullsize = scanName+'__DEM_full__'+scanNumber
    scanNameDEM = scanName+'__DEM__'+scanNumber
    scanNameNULL = scanName+'__NULL__'+scanNumber
    scanNameShaded = scanName+'__shaded__'+scanNumber
    exists = bool(len(gscript.parse_command('g.list', type='raster', pattern=scanNameShaded)))
    if exists is False:
      # Print status
      print ""
      print "***"
      print scanName
      print "***"
      print ""
      # DEM processing
      dem = np.fromfile(DATpath, dtype=np.float32)
      dem = dem.reshape(length_y, length_x)
      dem[dem == -9999] = np.nan
      dem /= 1000. # MM TO M
      # THIS SHOULD BE EXTERNALLY SET: MAX HEIGHT
      #dem[dem > 480] = np.nan # Trim off the tops of the input devices
      demFull = np.flipud(dem)
      dem = dem[margin_bottom:margin_top, margin_left:margin_right]
      dem = np.flipud(dem)
      # DEM import into GRASS GIS
      #try:
      DEMarray = garray.array()
      DEMarray[...] = dem
      DEMarray.write('tmp', overwrite=True)
      # Compute map of null areas
      r.mapcalc(scanNameNULL+' = isnull(tmp)', overwrite=True)
      # DEM null filling
      try:
        r.fillnulls(input='tmp', output=scanNameDEM, method='bilinear', overwrite=False)
      except:
        pass
      r.colors(map=scanNameDEM, color='wave')
      # Shaded relief map
      try:
        r.relief(input=scanNameDEM, output=scanNameShaded, overwrite=False)
      except:
        pass
    else:
      print "Processing already complete for", scanName
    #  errorfiles.append(DATfile)


# EXPORT STEP -- DO IT LATER
"""
for sourcedir in sourcedirs:
  DATpaths = sorted(glob.glob(sourcedir+'*.DAT'))
  for DATpath in DATpaths:
    # Name
    DATfile = os.path.split(DATpath)[-1]
    scanName, scanNumber = DATfile.split('_Composite')[0].split('_Scan')
    scanNameDEM = scanName+'__DEM__'+scanNumber
    scanNameNULL = scanName+'__NULL__'+scanNumber
    scanNameShaded = scanName+'__shaded__'+scanNumber
    try:
    r.out_gdal(input=scanNameDEM, output=scanNameDEM+'.tif', format='GTiff', overwrite=False)
"""

# Problem with duplicates
DEMs = gscript.parse_command('g.list', type='raster', pattern='*__DEM__*').keys()
DEMs = sorted(DEMs)
for DEM in DEMs:
  outname = DEM+'.tif'
  if os.path.isfile(outname):
    print "Not overwriting", outname
  else:
    print DEM
    r.out_gdal(input=DEM, output=outname, format='GTiff', overwrite=False)


maps = gscript.parse_command('g.list', type='raster', pattern='*__shaded__*').keys()
maps = sorted(maps)
for mapi in maps:
  outname = mapi+'.tif'
  if os.path.isfile(outname):
    print "Not overwriting", outname
  else:
    print DEM
    r.out_gdal(input=mapi, output=outname, format='GTiff', overwrite=False)


# Placeholder to make these into future functions
def outputByType(self):
  pass




# Start in the lowest cell along the left-hand side of the experiment
# May want to make this a user-defined region in the future.
# And may want to define boundaries as closed or open -- for this,
# just r.patch a wall around everything except the end of the flume on the RHS.

reg = gscript.region()
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

_x = garray.array()
_x.read('x')
_y = garray.array()
_y.read('y')

drainarray = garray.array()

# Much of this will depend on experiment
DEMs = gscript.parse_command('g.list', type='raster', pattern='*__DEM__*').keys()
DEMs = sorted(DEMs)
for DEM in DEMs:
  r.patch(input='boundaries,'+DEM, output='tmp', overwrite=True)
  drainarray.read('tmp')
  scanName = DEM.split('__DEM__')[0]
  mainThalweg = scanName + '__main_thalweg__'
  tribThalweg = scanName + '__trib_thalweg__'
  # Main channel
  #start_x = margin_left/1000.
  #start_y = _y[:,1][drainarray[:,1] == np.min(drainarray[:,1])]
  flowIn = garray.array()
  flowIn[:,2][drainarray[:,2] < (np.min(drainarray[:,2])+.01)] = 1
  flowIn.write('tmpFlowIn', overwrite=True)
  r.watershed(elevation='tmp', flow='tmpFlowIn', threshold=np.sum(flowIn), stream='tmpStream', accumulation='tmpAccum', flags='s', overwrite=True)
  r.mapcalc('tmpStreamZ = (tmpStream * 0 + 1) * tmp', overwrite=True)
  r.to_vect(input='tmpStreamZ', output='tmpStreamLine', type='line', overwrite=True)
  r.to_vect(input='tmpStreamZ', output='tmpStreamPoints', type='point', column='z', overwrite=True)
  v.db_addcolumn(map='tmpStreamPoints', columns='x double precision, y double precision')
  v.to_db(map='tmpStreamPoints', option='coor', columns='x,y')
  """
  # Tributary channel
  start_x = _x[drainarray[-2,:] == np.min(drainarray[-2,:])] # CHECK INDEXING (TOP/BOTTOM)
  if len(start_x) > 0:
    start_x = start_x[0] # ARBITRARY, SHOULD FIX SOMETIME, PROBABLY NOT IMPORTANT THOUGH.
  startpoint = str(start_x)+','+str(margin_bottom)/1000.
  r.drain(input='tmp', drain=tribThalweg, start_coordinates=startpoint)
  """



# Try r.sim.water


"""
# Old method with r.drain -- doesn't work well. Using r.watershed instead.
DEMs = gscript.parse_command('g.list', type='raster', pattern='*__DEM__*').keys()
DEMs = sorted(DEMs)
for DEM in DEMs:
  r.patch(input='boundaries,'+DEM, output='tmp', overwrite=True)
  drainarray.read('tmp')
  scanName = DEM.split('__DEM__')[0]
  mainThalweg = scanName + '__main_thalweg__'
  tribThalweg = scanName + '__trib_thalweg__'
  # THIS SHOULD ALSO BE INPUT AT THE START
  # Main channel
  start_y = _y[:,1][drainarray[:,1] == np.min(drainarray[:,1])]
  if len(start_y) > 0:
    start_y = start_y[0] # ARBITRARY, SHOULD FIX SOMETIME, PROBABLY NOT IMPORTANT THOUGH; COULD JUST TAKE [0], ABOVE
  start_x = margin_left/1000.
  startpoint = str(start_x)+','+str(start_y)
  r.drain(input='tmp', drain=mainThalweg, start_coordinates=startpoint)
  # Tributary channel
  start_x = _x[drainarray[-2,:] == np.min(drainarray[-2,:])] # CHECK INDEXING (TOP/BOTTOM)
  if len(start_x) > 0:
    start_x = start_x[0] # ARBITRARY, SHOULD FIX SOMETIME, PROBABLY NOT IMPORTANT THOUGH.
  startpoint = str(start_x)+','+str(margin_bottom)/1000.
  r.drain(input='tmp', drain=tribThalweg, start_coordinates=startpoint)
"""









"""
try:
  r.out_vtk(input='dem_151117_T_DW_IW_01_Scan0014', output='dem_151117_T_DW_IW_01_Scan0014.vtk', elevation='dem_151117_T_DW_IW_01_Scan0014', precision=4, overwrite=False)
except:
  pass
  
#r.fillnulls(input='tmp', output='terrace_151124_MC_DW_IW_01_Scan0016', method='bicubic', overwrite=True)
"""







# OLD VERSION, I THINK...
"""
NumPy_data_shape = NumPy_data.shape
VTK_data = numpy_support.numpy_to_vtk(num_array=dem.ravel(), deep=True, array_type=vtk.VTK_FLOAT)
"""








# ALSO AN OLD VERSION
"""
dem = dem[:5,:5]


x = np.arange(0, length_x)
y = np.arange(0, length_y)

X, Y = np.meshgrid(x,y)

x = y = np.arange(0, 5)
z = dem.ravel()

xyz = np.vstack((np.ravel(X), np.ravel(Y), z)).transpose()
np.savetxt('xyz_output.csv', xyz, delimiter=',')



dem = np.expand_dims(dem, 2)

gridToVTK("./dem_output", x, y, z, cellData = {'DEM': dem})
"""














