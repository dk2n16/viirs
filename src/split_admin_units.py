"""Module to explode national level multipolygon shapefile into individual admin units. Shapefile needs columns for ['ADM1', 'ADM1_id', 'geometry'] and will save shapefiles using row['ADM1'] as name"""
import subprocess
from pathlib import Path
import geopandas as gpd


class SplitAdminUnits:
    """Class to explode admin units"""

    def __init__(self, shp, out_folder):
        """"Initialisation functions
        shp --> National-level shapefile
        out_folder --> Folder in which to save output shps
        """
        self.shp = shp
        self.out_folder = out_folder
        self.explode_shapes(self.shp, self.out_folder)

    def explode_shapes(self, shp, out_folder):
        """Function to explode shapes and save to individual admin units"""
        gdf = gpd.read_file(str(shp))
        gdf = gdf[['ADM1', 'ADM1_id', 'geometry']]
        for row in gdf.iterrows():
            adm_df = gpd.GeoDataFrame({'ADM1': [row[1][0]], 'ADM1_id': [row[1][1]], 'geometry': [row[1][2]]})
            name = (out_folder.joinpath("{0}.shp".format(row[1]["ADM1"])))
            adm_df.to_file(name)

class MergeAdminUnits:
    """Class to merge exploded subnational unit rasters into natainal level raster"""
    def __init__(self, country, months):
        """
        country ---> Country whose subnational rasters will be merged
        months --> List of directories which contain 'subnational' folder of rasters to be merged
        """
        self.country = country
        self.months = months
        self.make_tiff_list(self.months)
        self.make_vrt() #CHOOSE ONE
        self.merge_rasters() # OR THE OTHER METHOD


    def make_tiff_list(self, months):
        """Function to make lists of rasters for VRT"""
        for index, i in enumerate(months):
            if not i.joinpath('subnational/tiffs.txt').exists():
                month = index + 1
                rasters = [x for x in i.joinpath('subnational').iterdir() if x.name.endswith('norm.tif')]
                with open(i.joinpath('subnational/tiffs.txt'), 'w') as f:
                    for raster in rasters:
                        f.write(str(raster.resolve()))
                        f.write('\n')

    def make_vrt(self):
        """Make vrt from list of admin units"""
        for index, i in enumerate(self.months):
            month = str(index + 1)
            if len(month) < 2:
                month = '0' + month
            txt_file = i.joinpath('subnational/tiffs.txt')
            outfile = i.joinpath(f'{self.country}_{month}_normalised.vrt')
            if not outfile.exists():
                gdal_cmd = f'gdalbuildvrt -input_file_list {str(txt_file)} {str(outfile)}'
                subprocess.call(gdal_cmd, shell=True)

    def merge_rasters(self):
        """Makes list of tiffs in folder and inputs list into gdal_merge cmd"""
        for index, i in enumerate(self.months):
            month = str(index + 1)
            if len(month) < 2:
                month = '0' + month
            rasters = [str(x) for x in i.joinpath('subnational').iterdir() if not x.name.endswith('txt') if x.name.endswith('norm.tif')]
            outfile = i.joinpath(f'{self.country}_{month}_normalised.tif')
            tiffs = " ".join(rasters)
            gdal_cmd = f"gdal_merge.py -o {outfile} -a_nodata -99999.0 -of gtiff {tiffs}"
            subprocess.call(gdal_cmd, shell=True)

