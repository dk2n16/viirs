"""Main module to call all classes and functions associated with downloading, preprocessing and analysing VIIRS NTL"""
from pathlib import Path
from extract_rasters import ExtractFromTiles
from reclass_rasters import SetThreshold, NormaliseAdminUnits
from split_admin_units import SplitAdminUnits, MergeAdminUnits
from smooth_outliers import SmoothOutliers
from viirs_zonal_stats import VIIRSZonalStats
from graphs_maps import GraphMaps

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



def explode_shapefiles(iso):
    """Explode national shapefiles into admin units"""
    shp = BASEDIR.joinpath(f'datain/shps/{iso}/{iso}_adm1.shp')
    adm_shp_folder = shp.parent.joinpath('adm_units')
    if not adm_shp_folder.exists():
        adm_shp_folder.mkdir(parents=True, exist_ok=True)
    SplitAdminUnits(shp, adm_shp_folder)



def set_threshold(country):
    """Set threshold value of coverages seen by satellite"""
    months = [x for x in BASEDIR.joinpath(f'datain/{country}').iterdir()]
    for month in months:
        rad = [x for x in month.iterdir() if x.name.endswith('rad_tmp.tif')][0]
        cvg = [x for x in month.iterdir() if x.name.endswith('cvg.tif')][0]
        out_rad = Path(str(rad)[:-11] + 'rad_thrsh_set.tif')
        SetThreshold(rad, cvg, out_rad, cvg_threshold=5, rad_threshold=2) #Reclassifies based on threshold value and deletes tmp file


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

def extract_admin_rasters(country):
    """Extract admin unit rasters from national-level raster"""
    months = sorted([x for x in BASEDIR.joinpath(f'datain/{country}').iterdir()])
    admin_units = [x for x in BASEDIR.joinpath(f'datain/shps/{country}/adm_units').iterdir() if x.name.endswith('.shp')]
    for month in months:
        subnational_raster_folder = month.joinpath('subnational')
        if not subnational_raster_folder.exists():
            subnational_raster_folder.mkdir(parents=True, exist_ok=True)
        for admin_unit in admin_units:
            national_rasters = [x for x in month.iterdir() if x.name.endswith('rad_cap_smth.tif')]
            for raster in national_rasters:
                outfile = subnational_raster_folder.joinpath(f'{admin_unit.name[:-4]}_{month.name}_rad.tif')
                if not outfile.exists():
                    ExtractFromTiles(raster, admin_unit, outfile)

def normalise_admin_level_rasters_temporally(country):
    """Rescale admin unit level rasters between 0 and 1. Lowest value in year will become 0 and highest will become 1, others will be rescaled in between"""
    months = sorted([x for x in BASEDIR.joinpath(f'datain/{country}').iterdir()])
    names = sorted([x.name.split('_')[0] for x in months[0].joinpath('subnational').iterdir() if x.name.endswith('rad.tif')])
    NormaliseAdminUnits(names, months, country)

def merge_admin_units(country):
    """Merge monthly admin unit rasters to national-level raster"""
    months = sorted([x for x in BASEDIR.joinpath(f'datain/{country}').iterdir()])
    if not months[0].joinpath(f'01/{country}/{country}_01_normalised.tif').exists():
        MergeAdminUnits(country, months)

def do_zonal_stats(country):
    """Calculate zonal stats for each admin unit"""
    outfolder = BASEDIR.joinpath(f'dataout/{country}')
    if not outfolder.exists():
        outfolder.mkdir(parents=True, exist_ok=True)
    months = sorted([x for x in BASEDIR.joinpath(f'datain/{country}').iterdir()])
    shp = BASEDIR.joinpath(f'datain/shps/{country}/{country}_adm1.shp')
    out_shp = outfolder.joinpath(f'{country}_zonal_stats_norm.shp')
    out_csv = outfolder.joinpath(f'{country}_zonal_stats_norm.csv')
    if not out_shp.exists():
        VIIRSZonalStats(country, months, shp, out_shp, out_csv, raster_type='_normalised.tif') ### Change this according to zonal stats to be done (normalised OR seasonality coefficient) ###


def make_graphs_maps(country):
    shp = BASEDIR.joinpath(f'datain/shps/{country}/{country}_adm1.shp')
    csv = BASEDIR.joinpath(f'dataout/{country}/{country}_zonal_stats_norm.csv')
    outpath = BASEDIR.joinpath(f'dataout/{country}/mapsgraphs')
    GraphMaps(country, shp, csv, outpath)

    







def main():
    #extract national_rasters    
    TILESDIR = sorted([x for x in Path('/home/david/Documents/work/VIIRS/download_viirs/datain/2016').iterdir() if not x.name == 'ANNUAL_Composite_2016'])
    #countries = {'HTI': '75N180W', 'GHA': '75N060W', 'MOZ': '00N060W', 'NAM': '00N060W', 'NPL': '75N060E'}
    countries = {'HTI': '75N180W'}    
    extract_national_rasters(TILESDIR, countries)

    #explode shapefiles
    for iso, _ in countries.items():
        explode_shapefiles(iso)

    #set threshold
    for country, _ in countries.items():
        set_threshold(country)

    #remove values greater than capital max
    for country, _ in countries.items():
        remove_outliers_outside_capital(country)

    #Extract admin-level from national-level
    for country, _ in countries.items():
        extract_admin_rasters(country)

    #normalise admin-level rasters over time
    for country, _ in countries.items():
        normalise_admin_level_rasters_temporally(country)

    #### CHECK IF NORMALISING WAS THE BEST CHOICE ###
    #merge normalised rasters (try setting extent to fix shift)
    for country, _ in countries.items():
        merge_admin_units(country)

    #zonal stats
    for country, _ in countries.items():
        do_zonal_stats(country)

    #graphs and maps.
    for country, _ in countries.items():
        make_graphs_maps(country)

if __name__ == "__main__":
    BASEDIR = Path(__file__).resolve().parent.parent
    main()