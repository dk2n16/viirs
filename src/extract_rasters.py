"""Extract data from VIIRS in_rasters using shapefiles as input."""
from pathlib import Path
import subprocess
import geopandas as gpd
import numpy as np 
import rasterio
from rasterio._fill import _fillnodata

class ExtractFromTiles:
    """Class to extract VIIRS data from in_rasters using shapefiles as input"""

    def __init__(self, in_raster, shp, out_raster):
        """Initialisation function

        in_raster --> Input VIIRS in_raster
        shp --> Shapefile from which to extract raster
        out_raster --Output file name

        returns None
        """
        self.in_raster = in_raster
        self.shp = shp
        self.out_raster = out_raster
        self.bounding_box = self.get_extent()
        self.clip_raster(self.bounding_box)

    def get_extent(self):
        """Get bounding box of shapefile to specify extent of extracted raster.
		returns bounding box of shapefile
		"""
        gdf = gpd.read_file(str(self.shp))
        extent = gdf['geometry'].bounds
        bounding_box = {}
        bounding_box['minx'] = extent.loc[0]['minx']
        bounding_box['miny'] = extent.loc[0]['miny']
        bounding_box['maxx'] = extent.loc[0]['maxx']
        bounding_box['maxy'] = extent.loc[0]['maxy']
        return bounding_box

    def clip_raster(self, bounding_box):
        minx, miny, maxx, maxy = bounding_box['minx'], bounding_box['miny'], bounding_box['maxx'], bounding_box['maxy']
        gdal_cmd = f'gdalwarp --config GDALWARP_IGNORE_BAD_CUTLINE YES -te {minx} {miny} {maxx} {maxy} -crop_to_cutline -cutline {str(self.shp)} {str(self.in_raster)} {str(self.out_raster)}'
        subprocess.call(gdal_cmd, shell=True)

