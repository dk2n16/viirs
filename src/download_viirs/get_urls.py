"""Class to get list of url from which to download VIIRS data"""

import sys
import urllib3
from pathlib import Path 

from bs4 import BeautifulSoup
import certifi

BASE_DIR = Path(__file__).resolve().parent.parent

class GetNOOAUrls(object):
	"""Class to get list of url from which to download VIIRS data"""

	def __init__(self, years='all', annual_composites=False, extent='global'):
		__nooa_download_page = "https://ngdc.noaa.gov/eog/viirs/download_dnb_composites_iframe.html"
		try:
			self.years = years
			if self.years == 'all':
				self.years = range(2012, 2019)
			elif type(self.years) == int:
				self.years = [self.years]
			elif type(self.years) == list:
				self.years = years
			else:
				self.years = int(years)
				self.years = [self.years]
		except ValueError as e:
			print('Years should be a years or a list of years')
			print(e)
			sys.exit(1)
		if extent != 'global':
			self.extent = extent #should be a list
		else:
			self.extent = []
		self.annual_composites=annual_composites
		self.hrefs = self.get_page()
		if self.years != 'all':
			self.hrefs = self.trim_years(self.hrefs, self.years)


	def get_page(self):
		"""Function to get NOOA and list all available datasets"""
		http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
		url = "https://ngdc.noaa.gov/eog/viirs/download_dnb_composites_iframe.html"
		page = http.request('GET', url)
		nooa = BeautifulSoup(page.data, 'html.parser')
		hrefs = [a['href'] for a in nooa.find_all('a', href=True) if a['href'].endswith('tgz') if 'vcmslcfg' not in a['href']]
		return hrefs

	def trim_years(self, hrefs, years):
		"""Remove unwanted years from href list"""
		wanted_hrefs = []
		for _, href in enumerate(hrefs):
			parts = href.split('//')
			file_name = parts[-1]
			date = file_name.split('/')[0]
			file_extent = file_name.split('_')[3]
			if file_extent not in self.extent:
				continue
			if len(date) == 4 and not self.annual_composites:
				continue
			else:
				year = date[:4]
				year = int(year)
				if year in years:
					wanted_hrefs.append(href)
		return wanted_hrefs