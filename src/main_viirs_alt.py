"""Main module to call all classes and functions associated with downloading, preprocessing and analysing VIIRS NTL"""
from pathlib import Path
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