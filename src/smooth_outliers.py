import rasterio
import numpy as np 
import rasterstats
from pathlib import Path
from rasterio._fill import _fillnodata


class SmoothOutliers(object):
	"""Calculates maximum NTL value in capital region of country (defined by input shapefile. Any other pixels >= this value are made NoData and then interpolated (IDW) using values from surrounding pixels. This reduces the effect of outliers caused by snow, gas flairs and dry river beds"""
	def __init__(self, rad_raster, capital_shp, out_raster):
		self.rad_raster = rad_raster
		self.capital_shp = capital_shp
		self.out_raster = out_raster

	def get_max_in_capital(self):
		"""Returns maximum of zonal statistics of NTL in capital region defined by input shapefile"""
		stats = rasterstats.zonal_stats(str(self.capital_shp), str(self.rad_raster), stats=['max'])
		return stats[0]['max']

	def interpolate_high_values(self, max_value):
		"""Creates raster with smoothed outliers"""
		template = rasterio.open(self.rad_raster)
		profile = template.profile
		profile.update(count=1,
				        compress='lzw',
				        predictor=2,
				        bigtiff='yes',
				        nodata=-99999)
		template.close()
		with rasterio.open(str(self.rad_raster)) as src, rasterio.open(str(self.out_raster), 'w', **profile) as dst:
			rad_data = src.read()
			mask = np.full((rad_data.shape), 1)
			mask[np.where(rad_data > max_value)] = 0
			print(mask[np.where(mask == 0)])
			rad_data[np.where(rad_data > max_value)] = -99999
			result = _fillnodata(rad_data, mask=mask)
			dst.write(result)

    def remove_cap_max(self, cap_max):
        """Function max values over capital maximum ND, instead of interpolating into these pixels
        cap_max --> Value returned from self.get_max_in_captal()
        """
        template = rasterio.open(self.rad_raster)
        profile = template.profile
		profile.update(count=1,
				        compress='lzw',
				        predictor=2,
				        bigtiff='yes',
				        nodata=-99999)
		template.close()
        with rasterio.open(str(self.rad_raster)) as src, rasterio.open(str(self.out_raster), 'w', **profile) as dst:
            rad_data = src.read()
            rad_data[np.where(rad_data > cap_max)] = -99999
			dst.write(result)
