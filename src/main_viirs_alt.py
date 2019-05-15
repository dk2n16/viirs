"""Main module to call all classes and functions associated with downloading, preprocessing and analysing VIIRS NTL"""
from pathlib import Path
import pandas as pd
from extract_rasters import ExtractFromTiles
from reclass_rasters import SetThreshold, NormaliseAdminUnits
from split_admin_units import SplitAdminUnits, MergeAdminUnits
from smooth_outliers import SmoothOutliers
from viirs_zonal_stats import VIIRSZonalStats
from graphs_maps import GraphMaps

#for each country
# for each month:
#   remove outliers (<2)
#national level zonal stats --> Sol(m) --> get the lowest month --> Sol(min)
#get observation coefficient --> S(obs) = Sol(m)/Sol(min)
#graph and map

def extract_national_rasters(TILESDIR, countries):
    """Extract national rasters from tiles"""
    for month in TILESDIR:
        for country, extent in countries.items():
            shp = BASEDIR.joinpath(f'datain/shps/{country}/{country}_adm1.shp')
            tiles = [x for x in month.iterdir() if extent in x.name if x.name.endswith('.tif')]
            for tile in tiles:
                tile_folder = BASEDIR.joinpath(f'datain/{country}/{month.name}')
                if not tile_folder.exists():
                    tile_folder.mkdir(parents=True, exist_ok=True)
                if tile.name.endswith('rade9h.tif'):
                    outfile = tile_folder.joinpath(f'{country}_{month.name}_rad_tmp.tif')
                else:
                    outfile = tile_folder.joinpath(f'{country}_{month.name}_cvg.tif')
                if not outfile.exists():
                    ExtractFromTiles(tile, shp, outfile)

def set_threshold(country):
    """Set threshold value of coverages seen by satellite"""
    months = [x for x in BASEDIR.joinpath(f'datain/{country}').iterdir()]
    for month in months:
        rad = [x for x in month.iterdir() if x.name.endswith('rad_tmp.tif')][0]
        cvg = [x for x in month.iterdir() if x.name.endswith('cvg.tif')][0]
        out_rad = Path(str(rad)[:-11] + 'rad_thrsh_set.tif')
        SetThreshold(rad, cvg, out_rad, cvg_threshold=1, rad_threshold=2) #Reclassifies based on threshold value and deletes tmp file

def remove_outliers_outside_capital(country):
    """Remove values higher than highest in capital. This iteration does not interpolate or change values --> only makes NoData"""
    capital_shp = BASEDIR.joinpath(f'datain/shps/capitals/{country}_capital.shp')
    months = [x for x in BASEDIR.joinpath(f'datain/{country}').iterdir()]
    for month in months:
        rad_raster = [x for x in month.iterdir() if x.name.endswith('rad_thrsh_set.tif')][0]
        out_raster = month.joinpath(f'{country}_{month.name}_rad_cap_smth.tif')
        if not out_raster.exists():
            cap_smth = SmoothOutliers(rad_raster, capital_shp, out_raster)
            cap_max = cap_smth.get_max_in_capital()
            cap_smth.remove_cap_max(cap_max)

def do_zonal_stats(country):
    """Calculate zonal stats for each admin unit"""
    outfolder = BASEDIR.joinpath(f'dataout/{country}')
    if not outfolder.exists():
        outfolder.mkdir(parents=True, exist_ok=True)
    months = sorted([x for x in BASEDIR.joinpath(f'datain/{country}').iterdir()])
    shp = BASEDIR.joinpath(f'datain/shps/{country}/{country}_adm1.shp')
    out_shp = outfolder.joinpath(f'{country}_zonal_stats.shp')
    out_csv = outfolder.joinpath(f'{country}_zonal_stats.csv')
    if not out_shp.exists():
        VIIRSZonalStats(country, months, shp, out_shp, out_csv, raster_type='_rad_cap_smth.tif') ### Change this according to zonal stats to be done (normalised OR seasonality coefficient) ###

def get_national_zonal_stats(country):
    """Calculate national level zonal stats and month with min value"""
    outfolder = BASEDIR.joinpath(f'dataout/{country}')
    if not outfolder.exists():
        outfolder.mkdir(parents=True, exist_ok=True)
    months = sorted([x for x in BASEDIR.joinpath(f'datain/{country}').iterdir()])
    shp = BASEDIR.joinpath(f'datain/shps/{country}/{country.lower()}_level0_2000_2020.shp')
    out_shp = outfolder.joinpath(f'{country}_zonal_stats_National.shp')
    out_csv = outfolder.joinpath(f'{country}_zonal_stats_National.csv')
    if not out_shp.exists():
        VIIRSZonalStats(country, months, shp, out_shp, out_csv, raster_type='_rad_cap_smth.tif') ### Change this according to zonal stats to be done (normalised OR seasonality coefficient) ###
    df = pd.read_csv(str(BASEDIR.joinpath(f'dataout/{country}/{country}_zonal_stats_National.csv')))
    cols = []
    for i in range(12):
        i += 1
        if len(str(i)) < 2:
            month = f'sum0{str(i)}'
        else:
            month = f'sum{str(i)}'
        cols.append(month)
    df = df[cols].min()
    min_month = df.idxmin(axis=1)
    do_zonal_stats(country)
    df = pd.read_csv(BASEDIR.joinpath(f'dataout/{country}/{country}_zonal_stats.csv'))
    cols = []
    for i in range(12):
        i += 1
        if len(str(i)) < 2:
            month = f'sum0{str(i)}'
        else:
            month = f'sum{str(i)}'
        cols.append(month)
    for i in cols:
        df.insert(1, f'SoL_obs{i[-2:]}', value=df[i]/df[min_month])
    df = df.fillna(value=0)
    df.to_csv(BASEDIR.joinpath(f'dataout/{country}/{country}_zonal_stats.csv'))

def make_graphs_maps(country):
    shp = BASEDIR.joinpath(f'datain/shps/{country}/{country}_adm1.shp')
    csv = BASEDIR.joinpath(f'dataout/{country}/{country}_zonal_stats.csv')
    outpath = BASEDIR.joinpath(f'dataout/{country}/mapsgraphs')
    GraphMaps(country, shp, csv, outpath)



if __name__ == "__main__":
    BASEDIR = Path(__file__).resolve().parent.parent
    TILESDIR = sorted([x for x in Path('/home/david/Documents/work/VIIRS/download_viirs/datain/2016').iterdir() if not x.name == 'ANNUAL_Composite_2016'])
    countries = {'HTI': '75N180W', 'GHA': '75N060W', 'MOZ': '00N060W', 'NAM': '00N060W', 'NPL': '75N060E'}
    #countries = {'HTI': '75N180W'}
    extract_national_rasters(TILESDIR, countries)
    for country, _ in countries.items():
        set_threshold(country)
        remove_outliers_outside_capital(country)
        get_national_zonal_stats(country) #finding country min and subnational zonal stats included in this function
        make_graphs_maps(country)