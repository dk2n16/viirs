"""Module contains classes to carry out different raster classifications

SetThreshold --> Takes continuous and classified raster. Threshold is set to value higher than input in classified raster. Default threshold = 1.
"""
from pathlib import Path
import numpy as np
import rasterio
from rasterio._fill import _fillnodata

class SetThreshold:
    """Class to set threshold value from coverage raster where data in radiance raster will be kept"""

    def __init__(self, rad, cvg, out_rad, cvg_threshold=1, rad_threshold=0, interpolate_nodata=False, remove_rad_threshold=True):
        """Initialisation function
        
        rad --> Continuous temporary radiance raster. Values will be removed        from this raster will be removed if coveraged is below                threshold value and made nodata
        cvg --> Categorical coverage raster
        out_rad --> name of output raster
        cvg_threshold --> Threshold value for cvg raster. Default is 1
        rad_threshold --> The radiance values above which will be kept. Default=0
        interpolate --> Interpolate nodata pixels. Default is false
        remove_rad_threshold --> Remove values in rad below threshold. Default is true 
        """
        self.rad = rad
        self.cvg = cvg
        self.out_rad = out_rad
        self.cvg_threshold = cvg_threshold
        self.rad_threshold = rad_threshold
        self.interpolate_nodata = interpolate_nodata
        self.remove_rad_threshold = remove_rad_threshold

        self.template = rasterio.open(str(self.rad))
        self.profile = self.template.profile
        self.profile.update(count=1,
				        compress='lzw',
				        predictor=2,
				        bigtiff='yes',
				        nodata=-99999)
        self.template.close()
        reclass_data = self.set_threshold()
        if self.remove_rad_threshold:
            reclass_data = self.remove_rad_threshold_values(reclass_data, self.rad_threshold)
        #TO DO TO DO TO DO
        if self.interpolate_nodata:
            reclass_data = self.interpolate_nodata(reclass_data)
        self.save_output(reclass_data)

    def set_threshold(self):
        """Function to open rad and cvg rasters and returns reclassified rad data above threshold value
        Returns reclassed array
        """
        with rasterio.open(str(self.rad)) as rad_src, rasterio.open(str(self.cvg)) as cvg_src:
            data_rad = rad_src.read()
            data_cvg = cvg_src.read()
            data_rad[np.where(data_cvg < self.cvg_threshold)] = -99999
            return data_rad 

    def interpolate_nodata(self, reclass_data):
        """TO DO --> function to interpolate nodata
        Returns reclassed array
        """
        pass

    def remove_negative_values(self, reclass_data):
        """Returns data with negative values as nodata
        Returns reclassed array
        """
        reclass_data[np.where((reclass_data < 0) & (reclass_data != -99999))] = -99999
        return reclass_data

    def remove_rad_threshold_values(self, reclass_data, rad_threshold):
        """Remove values below certain threshold"""
        reclass_data[np.where(reclass_data < rad_threshold)] = -99999
        return reclass_data

    def save_output(self, reclass_data):
        """Function to write output array to raster"""
        profile = self.profile
        with rasterio.open(str(self.out_rad), 'w', **profile) as dst:
            dst.write(reclass_data)
        #self.rad.unlink()

class NormaliseAdminUnits:
    """Class to normalise rasters temporally --> lowest = 0; highest = 1"""
    def __init__(self, names, months, country):
        """Initialisation expects a list of admin unit names from which to normalise and a list of folders in which temporal data sets are kept to be normalised. Class will loop through each name, collect the rasters for that name in each month, normalise (0-1) and save a raster. Will then mosaic the raster.
        names --> List of admin unit names
        month --> list of folders representing temporal time periods
        """
        self.names = names
        self.months = months
        self.country = country
        for name in self.names:
            #for_normalising = self.extract_rasters_to_stacked_array(name)
            for admin_unit in self.extract_rasters_to_stacked_array(name):
                stack = self.stack_arrays(admin_unit)
                for month in self.months:
                    self.write_normalised_rasters(month, stack, name)

    def extract_rasters_to_stacked_array(self, name):
        """Loop through names and return 3D stacked array of admin units monthly rasters"""        
        for_normalising = {}
        for month in self.months:
            raster = month.joinpath(f'subnational/{name}_{month.name}_rad.tif')
            array_name = f'{str(name)}_{month.name}'
            with rasterio.open(raster) as src:
                data = src.read()
                for_normalising[array_name] = data
        yield for_normalising

    def stack_arrays(self, admin_unit):
        """Returns stacked array for admin units over a time period
        admin_unit --> dictionary of admin_units np.arrays over a time period
        """
        result = (admin_unit[x] for x, _ in admin_unit.items())
        stacked_arrays = np.stack(result)
        stack2 = np.ma.masked_array(stacked_arrays, stacked_arrays == -99999)
        stack2 = (stacked_arrays - stacked_arrays.min())/(stacked_arrays.max() - stacked_arrays.min())
        stack2[np.where(stacked_arrays == -99999)] = -99999
        return stack2

    def write_normalised_rasters(self, month, stack, name):
        """Save subsection of stacked array"""
        data = stack[int(month.name) -1]
        out_name = month.joinpath(f'subnational/{name}_{month.name}_norm.tif')
        raster = month.joinpath(f'subnational/{name}_{month.name}_rad.tif')
        template = rasterio.open(str(raster))
        profile = template.profile
        profile.update(count=1,
				        compress='lzw',
				        predictor=2,
				        bigtiff='yes',
				        nodata=-99999)
        template.close()
        with rasterio.open(out_name, 'w', **profile) as dst:
            dst.write(data)
        
