from pathlib import Path
from viirs_zonal_stats import PPPZonalStats, VIIRSZonalStats

def main(BASEDIR, country, level):
    raster = BASEDIR.joinpath(f'datain/{country}/ppp_2016/{country.lower()}_ppp_2016.tif')
    shp = BASEDIR.joinpath(f'datain/shps/{country}/{country}_adm{level}.shp')
    out_csv = BASEDIR.joinpath(f'dataout/{country}/{country}_ppp_stats.csv')
    ppp_stats = PPPZonalStats(country, level, raster, shp, out_csv)

    months = [x for x in BASEDIR.joinpath(f'datain/{country}').iterdir() if not x.name == 'ppp_2016' if not x.name.endswith('csv')]
    for month in months:
        raster = month.joinpath(f'{country}_{month.name}_rad_cap_smth.tif')
        #out_shp = BASEDIR.joinpath(f'dataout/{country}/{country}_viirs_L{level}.shp')
        out_csv2 = BASEDIR.joinpath(f'dataout/{country}/{country}_viirs_L{level}_{month.name}.csv')
        #light_stats = VIIRSZonalStats(country, months, shp, out_shp, out_csv2, level, raster_type='_rad_cap_smth.tif')
        light_stats = PPPZonalStats(country, level, raster, shp, out_csv2)
    df_to_concat = []
    for month in months:
        csv = BASEDIR.joinpath(f'dataout/{country}/{country}_viirs_L{level}_{month.name}.csv')
        df = pd.read_csv(str(csv))
        df_to_concat.append(df)
    


if __name__ == "__main__":
    countries = {'HTI': 4}
    for country, level in countries.items():
        BASEDIR = Path(__file__).resolve().parent.parent
        main(BASEDIR, country, level)