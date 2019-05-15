"""Module to carry out zonal stats on VIIRS rasters."""
from pathlib import Path 
import geopandas as gpd 
import numpy as np 
import pandas as pd 
from rasterstats import zonal_stats
from sklearn import preprocessing

class VIIRSZonalStats:
    """Class to calculate zonal stats"""
    UTMS = {'GHA': 2136, 'NPL': 32645, 'HTI':32618, 'MOZ': 4129, 'NAM': 32733}

    def __init__(self, country, months, shp, out_shp, out_csv, level, raster_type=None):
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
        self.level = level
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
            stats_geojson = stats_geojson[[f'NAME{self.level}', 'sum']]
            stats_geojson =stats_geojson.rename(index=str, columns={f'NAME{self.level}':f'NAME{self.level}', 'sum': f'sum{month.name}'})
            gdf = gdf.merge(stats_geojson, on=f'NAME{self.level}')
        temp = gdf.copy()
        temp = temp.to_crs(epsg=self.utm)
        temp['area'] = temp['geometry'].area * 0.0000001
        temp = temp[['area', f'NAME{self.level}']]
        gdf = gdf.merge(temp, on=f'NAME{self.level}')
        gdf = gdf[['ADM1', f'NAME{self.level}', 'sum01', 'sum02', 'sum03', 'sum04', 'sum05', 'sum06', 'sum07', 'sum08', 'sum09', 'sum10', 'sum11', 'sum12', 'area', 'geometry']]
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

class PPPZonalStats:
    """Class for calculating zonal stats sums of input ppp raster and subnational shapefile"""
    def __init__(self, country, level, raster, shp, out_csv, append_to_shp=False):
        """
        raster --> Input ppp raster
        shp --> shapefile defining the zones
        out_csv --> out zonal stats table
        append_to_shp --> append zonal stats to shapefile as well
        """
        self.country = country
        self.level = level
        self.raster = raster
        self.shp = shp
        self.out_csv = out_csv
        self.append_to_shp = append_to_shp
        self.ppp_zonal_stats()

    def ppp_zonal_stats(self):
        """Function to calculate zonal stats"""
        gdf = gpd.read_file(str(self.shp))
        stats = zonal_stats(str(self.shp), self.raster, stats=['sum', 'mean', 'std'], geojson_out=True)
        stats_geojson = gpd.GeoDataFrame.from_features(stats)
        stats_geojson = stats_geojson[['GID', f'NAME{self.level}', 'sum', 'mean', 'std']]
        if self.append_to_shp:
            gdf = gdf.merge(stats_geojson, on='ADM{self.level}_id')
        #stats_geojson = stats_geojson.groupby(f'NAME{self.level}').sum()
        stats_geojson.to_csv(str(self.out_csv), index=False)


class ThresholdZonalStats:
    """Calculates zonal stats of rad raster and appends to ppp zonal stats table"""
    def __init__(self, raster, shp, level, threshold_value, csv_to_append):
        """
        raster -> radiance raster
        shp --> shapefiles defining zones
        csv_to_append --> ppp zonal table to append to
        """
        self.raster = raster
        self.shp = shp
        self.level = level
        self.threshold_value = threshold_value
        self.csv_to_append = csv_to_append
        self.threshold_zonal_stats()

    def threshold_zonal_stats(self):
        """Function to calculate zonal stats and append to table"""
        df = pd.read_csv(self.csv_to_append)
        stats = zonal_stats(str(self.shp), self.raster, stats=['sum', 'mean', 'std'], geojson_out=True)
        stats_geojson = gpd.GeoDataFrame.from_features(stats)
        stats_geojson = stats_geojson[['GID', 'sum', 'mean', 'std']]
        stats_geojson.columns = ['GID', f'sum{self.threshold_value}', f'mean{self.threshold_value}', f'std{self.threshold_value}']
        #stats_geojson = stats_geojson.groupby(f'NAME{self.level}').sum()
        #df = df.merge(stats_geojson, on=f'NAME{self.level}')
        df = df.merge(stats_geojson, on='GID')
        df.to_csv(self.csv_to_append, index=False)

