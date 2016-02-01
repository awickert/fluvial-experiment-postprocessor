import numpy as np
from matplotlib import pyplot as plt
from pyevtk.hl import gridToVTK
from grass import script as gscript
from grass.script import array as garray
import os
import tempfile
from grass.pygrass.modules.shortcuts import general as g
from grass.pygrass.modules.shortcuts import raster as r
from grass.pygrass.modules import Module
import glob

length_y = 2401
length_x = 3936

margin_top = 2110
margin_bottom = 410
margin_left = 300
margin_right = 3700

sourcedir = '/media/awickert/Elements/Fluvial 2015/151109_MC_IW_01/Processed/'

length_y_trimmed = margin_top - margin_bottom
length_x_trimmed = margin_right - margin_left

g.region(w=margin_left/1000., e=margin_right/1000., s=margin_bottom/1000., n=margin_top/1000., res=0.001)

DATpaths = glob.glob(sourcedir+'*.DAT')

for DATpath in DATpaths:
  # Name
  DATfile = os.path.split(DATpath)[-1]
  scanName, scanNumber = DATfile.split('_Composite')[0].split('_Scan')
  scanNameDEM = scanName+'__DEM__'+scanNumber
  scanNameNULL = scanName+'__NULL__'+scanNumber
  scanNameShaded = scanName+'__shaded__'+scanNumber
  # Print status
  print ""
  print "***"
  print DATfile
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
  DEMarray = garray.array()
  DEMarray[...] = dem
  DEMarray.write('tmp', overwrite=True)
  # Compute map of null areas
  r.mapcalc(scanNameNULL+' = isnull(tmp)')
  # DEM null filling
  r.fillnulls(input='tmp', output=scanNameDEM, method='bilinear', overwrite=True)
  r.colors(map=scanNameDEM, color='wave')
  # Shaded relief map
  r.relief(input=scanNameDEM, output=scanNameShaded)


r.out_gdal(input='dem_151117_T_DW_IW_01_Scan0014', output='dem_151117_T_DW_IW_01_Scan0014.tif', format='GTiff')

r.out_vtk(input='dem_151117_T_DW_IW_01_Scan0014', output='dem_151117_T_DW_IW_01_Scan0014.vtk', elevation='dem_151117_T_DW_IW_01_Scan0014', precision=4, overwrite=True)

#r.fillnulls(input='tmp', output='terrace_151124_MC_DW_IW_01_Scan0016', method='bicubic', overwrite=True)




















NumPy_data_shape = NumPy_data.shape
VTK_data = numpy_support.numpy_to_vtk(num_array=dem.ravel(), deep=True, array_type=vtk.VTK_FLOAT)
















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

