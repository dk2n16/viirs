import pandas as pd
import numpy as np 
import geopandas as gpd 
import rasterio
from pathlib import Path 
import matplotlib.pyplot as plt
import adjustText as aT

class GraphMaps(object):
	def __init__(self, country, shp, csv, outpath):
		self.country = country
		self.shp = shp
		self.csv = csv
		self.outpath = outpath
		self.months = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
		if not self.outpath.exists():
			self.outpath.mkdir(parents=True, exist_ok=True)
		self.make_sum_bars()
		self.make_areal_bars()
		self.make_sum_lines()
		self.make_areal_lines()
		self.make_sum_maps()
		self.make_diff_maps()

	def make_sum_bars(self):
		df = pd.read_csv(str(self.csv))
		df = df.set_index('ADM1')
		df = df.transpose()
		df_sum = df[2:14]
		sum_rad = df_sum.plot.bar(figsize=(12,12),stacked=True, title=f'{self.country} total radiance by month - 2016')
		sum_rad.set_xlabel('Month')
		sum_rad.set_ylabel('Radiance')
		plt.savefig(self.outpath.joinpath(f'{self.country}_sum_bars.png'))
		plt.close()

	def make_areal_bars(self):
		df = pd.read_csv(str(self.csv))
		df = df.set_index('ADM1')
		df = df.transpose()
		df_areal = df[17:29]
		areal_rad = df_areal.plot.bar(figsize=(12,12),stacked=True, title=f'{self.country} avg radiance by month - 2016')
		areal_rad.set_xlabel('Month')
		areal_rad.set_ylabel('Radiance')
		plt.savefig(self.outpath.joinpath(f'{self.country}_areal_bars.png'))
		plt.close()

	def make_sum_lines(self):
		df = pd.read_csv(str(self.csv))
		df = df.set_index('ADM1')
		df = df.transpose()
		df_sum = df[2:14]
		line = df_sum.plot.line(figsize=(12,12),title=f'{self.country} total radiance by month - 2016')
		line.set_xlabel('Month')
		line.set_ylabel('Radiance')
		plt.savefig(self.outpath.joinpath(f'{self.country}_sum_lines.png'))
		plt.close()

	def make_areal_lines(self):
		df = pd.read_csv(str(self.csv))
		df = df.set_index('ADM1')
		df = df.transpose()
		df_areal = df[17:29]
		line = df_areal.plot.line(figsize=(12,12),title=f'{self.country} avg radiance by month - 2016')
		line.set_xlabel('Month')
		line.set_ylabel('Radiance')
		plt.savefig(self.outpath.joinpath(f'{self.country}_areal_lines.png'))
		plt.close()

	def make_sum_maps(self):
		cols = ['sum01', 'sum02', 'sum03', 'sum04', 'sum05', 'sum06', 'sum07', 'sum08', 'sum09', 'sum10', 'sum11', 'sum12']
		gdf = gpd.read_file(str(self.shp))
		gdf['center'] = gdf['geometry'].centroid
		gdf_points = gdf.copy()
		gdf_points.set_geometry("center", inplace=True)
		for index, i in enumerate(cols):
			g_plot = gdf.plot(column=i, figsize=(12,12), legend=True)
			texts = []
			for x, y, label in zip(gdf_points.geometry.x, gdf_points.geometry.y, gdf_points['ADM1']):
				texts.append(plt.text(x, y, label, fontsize=8))
			aT.adjust_text(texts, force_points=0.3, force_text=0.8, expand_points=(1,1), expand_text=(1,1), 
               arrowprops=dict(arrowstyle="-", color='white', lw=0.5))
			g_plot.set_title(self.months[index + 1])
			plt.savefig(self.outpath.joinpath(f'{self.country}_{str(index + 1)}_sum.png'))
			plt.close()
			

	def make_diff_maps(self):
		cols = ['diff01', 'diff02', 'diff03', 'diff04', 'diff05', 'diff06', 'diff07', 'diff08', 'diff09', 'diff10', 'diff11', 'diff12']
		gdf = gpd.read_file(str(self.shp))
		gdf['center'] = gdf['geometry'].centroid
		gdf_points = gdf.copy()
		gdf_points.set_geometry("center", inplace=True)
		for index, i in enumerate(cols):
			g_plot = gdf.plot(column=i, figsize=(12,12), cmap='RdBu_r', legend=True)
			texts = []
			for x, y, label in zip(gdf_points.geometry.x, gdf_points.geometry.y, gdf_points['ADM1']):
				texts.append(plt.text(x, y, label, fontsize=8))
			aT.adjust_text(texts, force_points=0.3, force_text=0.8, expand_points=(1,1), expand_text=(1,1), 
               arrowprops=dict(arrowstyle="-", color='white', lw=0.5))
			g_plot.set_title(self.months[index + 1])
			plt.savefig(self.outpath.joinpath(f'{self.country}_{str(index + 1 )}_diff.png'))
			plt.close()


		
