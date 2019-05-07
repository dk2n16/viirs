"""Module to carry out zonal stats on VIIRS rasters."""
from pathlib import Path 
import geopandas as gpd 
import numpy as np 
import pandas as pd 
from rasterstats import zonal_stats

class VIIRSZonalStats:
    """Class to calculate zonal stats"""
    UTMS = {'GHA': 2136, 'NPL': 32645, 'HTI':32618, 'MOZ': 4129, 'NAM': 32733}

    def __init__(self, country, months, shp, out_shp, out_csv, raster_type=None):
        """Initialisation arguments:
        
        country --> ISO for input country
        months --> List of paths for months of input rasters
        shp --> shape to use as zones
        out_shp --> Shapefile containing zonal stats table
        out_csv --> csv with zonal tables (missing geometry column from out_shp)
        """
        self.country = country
        self.months = months
        self.shp = shp
        self.out_shp = out_shp
        self.out_csv = out_csv
        self.raster_type = raster_type ##(normalised or seasonality coefficient) ##
        self.utm = self.UTMS[self.country]
        self.gdf = self.zonal_stats_all_months()

    
    def zonal_stats_all_months(self):
        """Returns geodataframe containing summed zonal stats for all months"""
        gdf = gpd.read_file(str(self.shp))
        for month in self.months:
            raster = month.joinpath(f'{self.country}_{month.name}{self.raster_type}')
            stats = zonal_stats(str(self.shp), raster, stats=['sum'], geojson_out=True)
            stats_geojson = gpd.GeoDataFrame.from_features(stats)
            stats_geojson = stats_geojson[['ADM1_id', 'sum']]
            stats_geojson =stats_geojson.rename(index=str, columns={'ADM1_id':'ADM1_id', 'sum': f'sum{month.name}'})
            gdf = gdf.merge(stats_geojson, on='ADM1_id')
        temp = gdf.copy()
        temp = temp.to_crs(epsg=self.utm)
        temp['area'] = temp['geometry'].area * 0.0000001
        temp = temp[['area', 'ADM1_id']]
        gdf = gdf.merge(temp, on='ADM1_id')
        gdf = gdf[['ADM1', 'ADM1_id', 'sum01', 'sum02', 'sum03', 'sum04', 'sum05', 'sum06', 'sum07', 'sum08', 'sum09', 'sum10', 'sum11', 'sum12', 'area', 'geometry']]
        cols = [x for x in gdf.columns.values if x.startswith('sum')]
        gdf['annual_ave'] = gdf[cols].sum(axis=1)/12
        gdf['annual_per_km'] = gdf['annual_ave']/gdf['area']
        cols = ['mean' + x[3:] for x in gdf.columns.values if x.startswith('sum')]
        for col in cols:
            gdf[col] = gdf['sum'+col[-2:]]/gdf['area']
        cols = ['diff' + x[3:] for x in gdf.columns.values if x.startswith('sum')]
        for col in cols:
            gdf[col] = (gdf['sum' + col[-2:]] - gdf['annual_ave'])/gdf['annual_ave'] * 100
        gdf.to_file(str(self.out_shp))
        df = pd.DataFrame(gdf)
        df = df.drop('geometry', axis=1)
        df.to_csv(str(self.out_csv))





