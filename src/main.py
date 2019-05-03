"""Main module to call all classes and functions associated with downloading, preprocessing and analysing VIIRS NTL"""
from pathlib import Path
from extract_rasters import ExtractFromTiles
from reclass_rasters import SetThreshold
from split_admin_units import SplitAdminUnits

def main():
    """Main function"""
    BASEDIR = Path(__file__).resolve().parent.parent
    TILESDIR = [x for x in Path('/home/david/Documents/work/VIIRS/download_viirs/datain/2016').iterdir() if not x.name == 'ANNUAL_Composite_2016']
    
    #Extract national-scale rasters from the tiles
    #countries = {'HTI': '75N180W', 'GHA': '75N060W', 'MOZ': '00N060W', 'NAM': '00N060W', 'NPL': '75N060E'}
    countries = {'HTI': '75N180W'}
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

            #Explode the National=level shapes into individual admin shps
            adm_shp_folder = shp.parent.joinpath('adm_units')
            if not adm_shp_folder.exists():
                adm_shp_folder.mkdir(parents=True, exist_ok=True)
            SplitAdminUnits(shp, adm_shp_folder)

            ################################################################################
            #do something to clean of nodata or no coverages in national level before splitting.
            ###############################################################################
    for country, extent in countries.items():
        months = [x for x in BASEDIR.joinpath(f'datain/{country}').iterdir()]
        for month in months:
            rad = [x for x in month.iterdir() if x.name.endswith('rad_tmp.tif')][0]
            cvg = [x for x in month.iterdir() if x.name.endswith('cvg.tif')][0]
            out_rad = Path(str(rad)[:-11] + 'rad.tif')
            print(f'OUTRAD NAME = {out_rad.name}')
            SetThreshold(rad, cvg, out_rad, threshold=5) #Reclassifies based on threshold value and deletes tmp file

            #WRITE SOMETHING TO REMOVE VALUES HIGHER THAN CAPITAL MAX


    #Extract admin-level rasters from national-level

    for country, extent in countries.items():
        months = [x for x in BASEDIR.joinpath(f'datain/{country}').iterdir()]
        admin_units = [x for x in BASEDIR.joinpath(f'datain/shps/{country}/adm_units').iterdir() if x.name.endswith('.shp')]
        for month in months:
            subnational_raster_folder = month.joinpath('subnational')
            if not subnational_raster_folder.exists():
                subnational_raster_folder.mkdir(parents=True, exist_ok=True)
            for admin_unit in admin_units:
                national_rasters = [x for x in month.iterdir()]
                for raster in national_rasters:
                    outfile = subnational_raster_folder.joinpath(f'{admin_unit.name[:-4]}_{raster.name[-7:]}')
                    ExtractFromTiles(raster, admin_unit, outfile)


if __name__ == "__main__":
    main()
