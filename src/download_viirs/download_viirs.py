"""Docstring"""

from pathlib import Path
import shutil
import tarfile
import urllib3
import certifi

BASE_DIR = Path(__file__).resolve().parent.parent

class DownloadViirs:
    """Docstring"""

    def __init__(self, url):
        """Docstring"""
        parts = url.split('//')
        self.download_zip_name = parts[-1].split('/')[-1]
        self.date = parts[-1].split('/')[0]
        self.year = self.date[:4]
        if len(self.date) > 4:
            self.month = self.date[-2:]
        else:
            self.month = f'ANNUAL_Composite_{self.year}'
        self.url = url
        self.download_path = BASE_DIR.joinpath(f'datain/{self.year}/{self.month}')
        self.create_folders()


    def __str__(self):
        """Docstring"""
        return f'DownloadViirs object to download tile from: {self.url}'

    def create_folders(self):
        """Docstring"""
        if not self.download_path.exists():
            self.download_path.mkdir(parents=True, exist_ok=True)

    def download_rasters(self):
        """Docstring"""
        #path = BASE_DIR.joinpath(f'datain/{self.year}/{self.month}/{self.download_zip_name}')
        file_loc = self.download_path.joinpath(self.download_zip_name)
        print(file_loc)
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        if http.request('GET', self.url, preload_content=False).status == 200:
            with http.request('GET', self.url, preload_content=False) as src, open(file_loc, 'wb') as out_file:
                shutil.copyfileobj(src, out_file)
            #r.release_conn()

    def open_tgz(self):
        """Docstring"""
        tar_url = self.download_path.joinpath(self.download_zip_name)
        tar = tarfile.open(tar_url, 'r')
        tar.extractall(self.download_path)
        self.download_path.joinpath(self.download_zip_name).unlink()
        