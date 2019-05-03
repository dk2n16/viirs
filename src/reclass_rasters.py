"""Module contains classes to carry out different raster classifications

SetThreshold --> Takes continuous and classified raster. Threshold is set to value higher than input in classified raster. Default threshold = 1.
"""
from pathlib import Path
import numpy as np
import rasterio
from rasterio._fill import _fillnodata

class SetThreshold:
    """Class to set threshold value from coverage raster where data in radiance raster will be kept"""

    def __init__(self, rad, cvg, out_rad, threshold=1, interpolate_nodata=False, remove_negative=True):
        """Initialisation function
        
        rad --> Continuous temporary radiance raster. Values will be removed        from this raster will be removed if coveraged is below                threshold value and made nodata
        cvg --> Categorical coverage raster
        out_rad --> name of output raster
        threshold --> Threshold value for cvg raster. Default is 1
        interpolate --> Interpolate nodata pixels. Default is false
        remove_negative --> Remove values in rad below 0. Default is true 
        """
        self.rad = rad
        self.cvg = cvg
        self.out_rad = out_rad
        self.threshold = threshold
        self.interpolate_nodata = interpolate_nodata
        self.remove_negative = remove_negative

        self.template = rasterio.open(str(self.rad))
        self.profile = self.template.profile
        self.profile.update(count=1,
				        compress='lzw',
				        predictor=2,
				        bigtiff='yes',
				        nodata=-99999)
        self.template.close()
        reclass_data = self.set_threshold()
        if self.remove_negative:
            reclass_data = self.remove_negative_values(reclass_data)
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
            data_rad[np.where(data_cvg < self.threshold)] = -99999
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

    def save_output(self, reclass_data):
        """Function to write output array to raster"""
        profile = self.profile
        with rasterio.open(str(self.out_rad), 'w', **profile) as dst:
            dst.write(reclass_data)
        self.rad.unlink()