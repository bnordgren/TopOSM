# TopOSM #

A system for rendering OpenStreetMap Based Topographic Maps


## Requirements ##

TopOSM runs on Linux. It may be possible to build and run it on other platforms, but I have not tested this. If you try it, please let me know.

The original TopOSM documentation mentioned dependencies on these versions of the following software, with Ubuntu 11.04 as a base:

* Mapnik (2.0) with included patches and Cairo support
* Python (2.6)
* GDAL (1.7)
* PostgreSQL + PostGIS
* ImageMagick

My fork is running with Ubuntu 16.04 as a base.


## Installation ##

My Dockerfile sets up my installation as follows: 

```
FROM ubuntu:16.04
MAINTAINER Bryce Nordgren <bnordgren@gmail.com>

# Need multiverse for mscorefonts
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    apt-add-repository "deb http://us.archive.ubuntu.com/ubuntu/ xenial multiverse" && \
    apt-add-repository "deb http://us.archive.ubuntu.com/ubuntu/ xenial-updates multiverse" && \
    apt-get update

# Processing requirements for TopOSM
RUN apt-get install -y debconf-utils && \
    echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula boolean true | debconf-set-selections && \
    apt-get install -y python-mapnik mapnik-utils gdal-bin gdal-contrib python-gdal \
       libgdal-dev proj-bin proj-data libproj-dev python-pyproj python-numpy imagemagick \
       gcc g++ optipng git postgresql postgresql-contrib \
       postgresql-server-dev-all postgis wget libxml2-dev python-libxml2 \
       libgeos-dev libbz2-dev make htop python-cairo python-cairo-dev \
       osm2pgsql unzip python-pypdf libboost-all-dev libicu-dev libpng-dev \
       libjpeg-dev libtiff-dev libz-dev libfreetype6-dev libxml2-dev \
       libproj-dev libcairo-dev libcairomm-1.0-dev python-cairo-dev \
       libpq-dev libgdal-dev libsqlite3-dev libcurl4-gnutls-dev \
       libsigc++-2.0-dev fonts-sil-gentium ttf-mscorefonts-installer \
       "ttf-adf-*" vim python-xattr python-lockfile python-pillow \
       python-pastescript python-webob \
    && rm -rf /var/lib/apt/lists/*
```

Set up PostgreSQL with PostGIS, see:
http://wiki.openstreetmap.org/wiki/Mapnik/PostGIS


### Build local patched Mapnik ###

This is retained for historical purposes. I'm using plain Mapnik installed from packages as shown above. 
I have not been able to determine whether this patch was added to the Mapnik code base in the interim.
Regardless, the process seems to work without it. 

```
$ git clone https://github.com/mapnik/mapnik.git
$ cd mapnik
$ patch -p0 < <toposm-dir>/mapnik2_erase_patch.diff
$ python scons/scons.py configure \
    INPUT_PLUGINS=raster,osm,gdal,shape,postgis,ogr \
    PREFIX=$HOME PYTHON_PREFIX=$HOME
$ python scons/scons.py
$ python scons/scons.py install
```

Also a historical note, because the process works with Boost installed from packages: _If you need a more recent boost than available for your system, you can build one locally (i.e. with PREFIX=$HOME) and tell the mapnik configure step to link against that by adding:_

```
BOOST_INCLUDES=$HOME/include BOOST_LIBS=$HOME/lib
```


### Required data files ###

* Processed / simplified / corrected OSM data
  * __$WORLD_BOUNDARIES_DIR__ http://tile.openstreetmap.org/world_boundaries-spherical.tgz
  * __$WORLD_BOUNDARIES_DIR/water-polygons-split-3857/water_polygons__ Water polygons (in spherical mercator) from http://openstreetmapdata.com/
* Cannot find where these are referenced by mapnik files... Loaded into postgis? Unused? 
  * http://tile.openstreetmap.org/processed_p.tar.bz2
  * http://tile.openstreetmap.org/shoreline_300.tar.bz2
  * http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_populated_places.zip
  * http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_boundary_lines_land.zip

* USGS Data
  * USGS NHD shapefiles (__$NHD_DIR__): ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/Hydrography/NHD/
  * USGS NED data, as needed (__$NED13_DIR__): ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/NED/13/
  * NLCD 2006 (Land cover) data (__$NLCD_DIR__): http://www.mrlc.gov/nlcd06_data.php
* Planet.osm or other OSM dataset (loaded into PostGIS database):
  * http://planet.openstreetmap.org/
  * http://download.geofabrik.de/


### Spatial Reference Information ###

These scripts are not really set up to allow you to easily change the projection of the rendered output. If you want
to try, here are a few places to add the PROJ.4 definition of your desired projection: 

* prep_toposm_data
* import_nhd
* include/utils.inc.templ

Once defined, you'll need to tell mapnik to use your projection. In the above, you should have added an `<!ENTITY >` statement to the include/utils.inc.templ file. Use it in the `<Map />` elements of:

* templates/areas.xml.templ
* templates/contours.xml.templ
* templates/features.xml.templ
* templates/hypsorelief.xml.templ
* templates/landcoverrelief.xml.templ
* templates/ocean.xml.templ

Finally, a `<Map />` contains many `<Layer />`s. By default, the `<Layer />`s inherit the projection information from 
the `<Map />` to which they belong. If the layer definition does not explicitly specify the projection of the data source, 
then changing the Map's output projection silently changed the _assumed_ projection of all your input data. This is almost
certainly not what you want. You must visit each `<Layer />` element inside the map and add an srs="xxx" attribute, 
where "xxx" is whatever was originally in the Map element before you replaced it.
  
### Configuring the Rendering Environment ###

Create the required directories for tiles and temp files:

```
$ mkdir -p temp tile
```

TopOSM is configured through environment variables. A template for this is included. Make a copy, modify it according to you system, and source it:

```
$ cp set-toposm-env.templ set-toposm-env
$ emacs set-toposm-env
$ . set-toposm-env
```

Import OSM data. The import will be cropped to the area specified in set-toposm-env.
```
$ ./import_planet geodata/osm/Planet.osm
```

The import script can also import OSM daily diffs (ending in .osc.gz).


Import NHD data:
```
$ ./import_nhd
```

Generate hillshade and colormaps:
```
$ ./prep_toposm_data
```
Generate turning circle images:
```
$ ./generate_turning_circles.py
```


Add a shortcut for your area(s) of interest to areas.py.

Generate the mapnik style files from templates:
```
$ ./generate_xml
```
(you need to do this every time you modify the styles in the
templates and include directories)

Create contour tables and generate contour lines, for example:
```
$ ./prep_contours_table
$ ./toposm.py prep WhiteMountains
```

After the contours are created, you need to sort out the contours for better rendering. Create a column called "class" and
apply the following criteria: 
```
   - Class 5 == 1000 ft intervals
   - Class 4 == 400 ft intervals (not also class 5)
   - Class 3 == 200 ft intervals (not also class 4,5)
   - Class 2 == 80 ft intervals  (not also class 3/4/5)
   - Class 1 == 40 ft intervals  (not also class 2+)
```


To render tiles for the specified area and image size:
```
$ ./toposm.py png|pdf WhiteMountains <filename> <size x> <size y>
```

For faster rendering, create indexes on: 

| Table | Column |
| ----- | ------ |
| contour | class | 
| contour | way | 

## Credits ##

Created by Lars Ahlzen (lars@ahlzen.com), with contributions from Ian Dees (hosting, rendering and troubleshooting), Phil Gold (patches and style improvements), Kevin Kenny (improved NHD rendering, misc patches), Yves Cainaud (legend), Richard Weait (shield graphics) and others.

License: GPLv2
