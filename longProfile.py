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

channels = gscript.parse_command('g.list', type='vector', pattern='channel_centerline_*').keys()
for channel in channels:
    channel_points = channel[:-7] + 'points_' + channel[-7:]
    v.to_points(input=channel, output=channel_points, type='line', dmax=0.002, overwrite=True)
    v.db_addcolumn(map=channel_points, layer=2, columns='x double precision, y double precision, z double precision')
    v.to_db(map=channel_points, option='coor', columns='x,y', layer=2)
    v.what_rast(map=channel_points, layer=2, raster='DEM_'+channel[-7:], column='z')
    v.db.select(map=channel_points, layer=2, separator=',', file=channel_points+'.csv')


for file in `ls *.DAT`
do
    echo
    echo $file
    echo
    #mapname="${file%.*}"
    seconds=${file:8:7}
    r.in.bin in=$file out=DEM_$seconds n=2401 s=0 w=0 e=3936 rows=2401 cols=3936 flip=v -f --o
    r.null map=DEM_$seconds setnull=-9999
    g.region -p rast=DEM_$seconds # shouldn't be needed
    r.fillnulls input=DEM_$seconds output=DEM_$seconds method=bilinear --o
    r.mapcalc "DEM_$seconds = DEM_$seconds / 1000." --o # To meters

    # Region with watershed input
    g.region -p w=280 e=3700 s=600 n=1900
    r.mapcalc "DEMtmp = DEM_$seconds" --o
    # Add walls
    g.region -p w=278 e=3700 s=598 n=1902
    r.mapcalc "bc = 1." --o
    r.patch input=DEMtmp,bc out=DEMtmp --o

    # Watershed input
    r.mapcalc "flow = ( (x() == 280.5) * (y() == 1259.5) )" --o
    r.watershed elev=DEMtmp flow=flow accumulation=channel_centerline_$seconds -sa --o
    r.null map=channel_centerline_$seconds null=0
    r.stream.extract elev=DEMtmp accumulation=channel_centerline_$seconds stream_vector=channel_centerline_$seconds threshold=1 --o

    # Region + extract
    g.region -p w=300 e=3700 s=600 n=1900
    v.in.region out=calcWindow --o
    v.extract in=channel_centerline_$seconds out=tmp type=line --o
    v.overlay ainput=tmp atype=line binput=calcWindow operator=and output=channel_centerline_$seconds --o
    r.mapcalc "DEM_$seconds = DEM_$seconds" --o # Replace DEM with clipped version
done

for file in `ls *.DAT`
do
    seconds=${file:8:7}
    echo
    echo $seconds
    echo
    # Export
    r.out.bin in=DEM_$seconds out=DEM_$seconds.bil -b
    v.out.ogr in=channel_centerline_$seconds out=channel_centerline_$seconds
done


