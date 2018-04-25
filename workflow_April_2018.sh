# RUN IN INPUT DIR
for file in `ls *.DAT`
do
    echo
    echo $file
    echo
    #mapname="${file%.*}"
    seconds=${file:8:7}
    r.in.bin in=$file out=DEM_fullextent_$seconds n=2.401 s=0 w=0 e=3.936 rows=2401 cols=3936 flip=v -f --o
    r.null map=DEM_fullextent_$seconds setnull=-9999
    g.region -p rast=DEM_fullextent_$seconds # shouldn't be needed
    g.copy raster=DEM_fullextent_$seconds,DEM_fullextent_nulls_$seconds --o
    r.fillnulls input=DEM_fullextent_$seconds output=DEM_fullextent_$seconds method=bilinear --o
    r.mapcalc "DEM_fullextent_$seconds = DEM_fullextent_$seconds / 1000." --o # To meters
done

# THEN RUN IN OUTPUT DIR
cd ..
mkdir DEMs
cd DEMs
for name in `g.list rast pattern="DEM_fullextent_*???????.tif`
do
    echo $name
    r.out.gdal input=$name output=$name.tif --o
done

