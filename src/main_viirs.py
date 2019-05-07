"""Main module to call all classes and functions associated with downloading, preprocessing and analysing VIIRS NTL"""
from pathlib import Path
from extract_rasters import ExtractFromTiles
from reclass_rasters import SetThreshold, NormaliseAdminUnits
from split_admin_units import SplitAdminUnits
from smooth_outliers import SmoothOutliers

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
        SetThreshold(rad, cvg, out_rad, threshold=5) #Reclassifies based on threshold value and deletes tmp file

        ####MAKE RAD AND CVG THRESHOLDS IN THE FUNCTION!!!!! IN THE REMOVE NEGATIVE VALUES FUNCTION

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

    #zonal stats

    #graphs and maps.

if __name__ == "__main__":
    BASEDIR = Path(__file__).resolve().parent.parent
    main()