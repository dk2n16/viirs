"""Main module for new (15/05/2019) method to extract VIIRS, find optimal threshold, baseline NTL month from which to compare other months, and calculate zonal stats"""
from pathlib import Path
import shutil
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from extract_rasters import ExtractFromTiles
from reclass_rasters import SetThreshold, NormaliseAdminUnits, ReclassByThreshold
from split_admin_units import SplitAdminUnits, MergeAdminUnits
from smooth_outliers import SmoothOutliers
from viirs_zonal_stats import VIIRSZonalStats, PPPZonalStats, ThresholdZonalStats
from graphs_maps import GraphMaps

class GetOptimalThresholdValue:
    """Class to loop through range of radiance values to find optimal threshold that best correlates with population raster of year. Uses annual average composite (VIIRS) and 2016 ppp (WorldPop)"""
    def __init__(self, country, level, rad_raster, shp, ppp, rad_min, rad_max, rad_interval=0.1):
        """
        country --> Input country
        shp --> Shapefile to use for zonal stats
        rad_min --> radiance value to start correlation
        rad_max -->  radiance value to stop correlation
        rad_interval --> increments to increase radiance value for each correlation
        """
        self.country = country
        self.level = level
        self.shp = shp
        self.ppp = ppp
        self.rad_min = rad_min
        self.rad_max = rad_max
        self.rad_interval = rad_interval
        self.rad_raster = rad_raster
        self.temp_rad_raster = self.rad_raster.parent.joinpath(f'{self.country}_tmp_rad.tif')
        self.thresholds_csv = self.rad_raster.parent.joinpath(f'{self.country}_thresholds.csv')
        shutil.copy(self.rad_raster, self.temp_rad_raster)
        PPPZonalStats(self.country, self.level, self.ppp, self.shp, self.thresholds_csv)
        self.loop_through_thresholds()

    def loop_through_thresholds(self):
        """Function to loop throught iterations and call functions to extract raster according to thresholds, run zonal stats and check correlation"""
        for i in np.arange(self.rad_min, self.rad_max + self.rad_interval, self.rad_interval):
            self.reclass_to_threshold(i)
            self.radiance_zonal_stats(i)
        self.get_max_threshold()


    def reclass_to_threshold(self, i):
        """Reclass raster to threshold"""
        ReclassByThreshold(self.rad_raster, i, self.rad_raster.parent.joinpath(f'{self.country}_tmp_rad.tif'))

    def radiance_zonal_stats(self, i):
        """Function to get zonal stats of radiance when classified to threshold value"""
        ThresholdZonalStats(self.temp_rad_raster, self.shp, self.level, i, self.thresholds_csv)

    def get_max_threshold(self):
        """Get maximum correlation between radiance threshold and ppp"""
        df = pd.read_csv(self.thresholds_csv)
        sums = [x for x in df.columns.values if x.startswith('sum')]
        sums.remove('sum')
        df_final = dict()
        for column in sums:
            df_corr = df[['sum', column]]
            df_corr = df_corr.corr(method='pearson')
            df_final[column] = [df_corr[column][0]]
        df_sums = pd.DataFrame.from_dict(df_final)
        max_corr = df_sums.max(axis=1)
        max_threshold = df.idxmax(axis=1)
        print(f'maximum threshold is {max_threshold} with correlation of {max_corr}')
        df_sums = df_sums.transpose()
        df_sums.columns = ['Threshold']
        line = df_sums.plot.line(figsize=(12,12),title=f'{self.country} lights correlation with ppp')
        line.set_ylabel('Radiance')
        plt.savefig(self.temp_rad_raster.parent.joinpath(f'{self.country}_lights_corr_with_ppp.png'))
        plt.close()

        






if __name__ == "__main__":
    BASEDIR = Path(__file__).resolve().parent.parent
    #countries = {'HTI': '75N180W', 'GHA': '75N060W', 'MOZ': '00N060W', 'NAM': '00N060W', 'NPL': '75N060E'}
    countries = {'HTI': {'location': '75N180W', 'admin_level': 4}}
    print(BASEDIR)
    TILESDIR = sorted([x for x in Path('/home/david/Documents/work/VIIRS/download_viirs/datain/2016').iterdir() if x.name == 'ANNUAL_Composite_2016'])[0]
    for country, info in countries.items():
        rad_tile = TILESDIR.joinpath(f'SVDNB_npp_20160101-20161231_{info["location"]}_vcm-orm-ntl_v10_c201807311200.avg_rade9.tif')
        cvg_tile = TILESDIR.joinpath(f'SVDNB_npp_20160101-20161231_{info["location"]}_vcm_v10_c201807311200.cvg.tif')
        threshold_selection = BASEDIR.joinpath(f'datain/{country}/threshold_selection')
        if not threshold_selection.exists():
            threshold_selection.mkdir(parents=True, exist_ok=True)
        ppp = BASEDIR.joinpath(f'datain/{country}/ppp_2016/{country.lower()}_ppp_2016.tif')
        shp = BASEDIR.joinpath(f'datain/shps/{country}/{country}_adm{info["admin_level"]}.shp')
        out_raster_rad = BASEDIR.joinpath(f'datain/{country}/threshold_selection/{country}_ann_rad.tif')
        if not out_raster_rad.exists():
            ExtractFromTiles(rad_tile, shp, out_raster_rad)
        threshold = GetOptimalThresholdValue(country, info['admin_level'], out_raster_rad, shp, ppp, 0, 5, rad_interval=0.05)
        
        