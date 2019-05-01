"""Module to explode national level multipolygon shapefile into individual admin units. Shapefile needs columns for ['ADM1', 'ADM1_id', 'geometry'] and will save shapefiles using row['ADM1'] as name"""
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