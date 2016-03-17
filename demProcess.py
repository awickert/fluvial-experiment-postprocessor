from Scientific.IO.NetCDF import NetCDFFile
import numpy as np
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
 
# DATA
# define GRASS DATABASE
# add your path to grassdata (GRASS GIS database) directory
#gisdb = os.path.join(os.path.expanduser("~"), "grassdata")
# the following path is the default path on MS Windows
# gisdb = os.path.join(os.path.expanduser("~"), "Documents/grassdata") 
 
########### SOFTWARE
if sys.platform.startswith('linux'):
    # we assume that the GRASS GIS start script is available and in the PATH
    # query GRASS 7 itself for its GISBASE
    grass7bin = grass7bin_lin
elif sys.platform.startswith('win'):
    grass7bin = grass7bin_win
else:
    raise OSError('Platform not configured.')
 
# query GRASS 7 itself for its GISBASE
startcmd = [grass7bin, '--config', 'path']
 
p = subprocess.Popen(startcmd, shell=False,
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
gsetup.init(gisbase,
            gisdb, location, mapset)
 
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
from grass.pygrass.modules import Module
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
sourcedirs = sorted(glob.glob('/data3/TerraceExperiment/Forgotten/*/Processed/'))

length_y_trimmed = margin_top - margin_bottom
length_x_trimmed = margin_right - margin_left

g.region(w=margin_left/1000., e=margin_right/1000., s=margin_bottom/1000., n=margin_top/1000., res=0.001)

errordirs = []
errorfiles = []
for sourcedir in sourcedirs:
  DATpaths = sorted(glob.glob(sourcedir+'*.DAT'))
  for DATpath in DATpaths:
    # Name
    DATfile = os.path.split(DATpath)[-1]
    scanName, scanNumber = DATfile.split('_Composite')[0].split('_Scan')
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
      dem = dem[margin_bottom:margin_top, margin_left:margin_right]
      dem = np.flipud(dem)
      dem[dem > 480] = np.nan # Trim off the tops of the input devices
      dem[dem == -9999] = np.nan
      dem /= 1000.
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

r.mapcalc














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













