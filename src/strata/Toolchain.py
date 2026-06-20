# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2026 Nicolas Bruguier (gandalfn) <gandalfn@club-internet.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import re
import urllib.request

from src.strata.Stratum import Stratum
from src.system.Downloader import Downloader
from src.system.Archiver import Archiver
from src.system.Stamp import Step

class Toolchain(Stratum):
    def __init__(self, root: str, board: str):
        super().__init__("Toolchain", root, board)

        self.log.info(f"Loading toolchain configuration ...")
        
        self.__arch = self.config["arch"]
        self.__ccache = self.config["ccache"]
        self.__watch = self.config["watch"]
        cflags = self.config["cflags"]
        self.__cflags = " ".join(cflags)
        version = self.config["version"]

        if version.lower() == "latest":
            self.__version = self.__resolveWatchVersion()
        else:
            self.__version = version
        
        self.__url = self.__watch["url_template"].format(version=self.__version)
        
        self.log.debug(f"Toolchain configuration loaded:")
        self.log.debug(f"  -> Board: {self.board.name}")
        self.log.debug(f"  -> Arch: {self.__arch}")
        self.log.debug(f"  -> CCache: {self.__ccache}")
        self.log.debug(f"  -> Version: {self.__version}")
        self.log.debug(f"  -> URL: {self.__url}")
        
    @property
    def arch(self):
        return self.__arch
    
    @property
    def compiler(self):
        return f'ccache {self.path}/bin/{self.arch}-gcc' if self.__ccache else f'{self.path}/bin/{self.arch}-gcc'
    
    @property
    def cflags(self):
        return self.__cflags
    
    @property
    def crosscompile(self):
        return f'{self.arch}-'
    
    @property
    def version(self):
        return self.__version
    
    @property
    def url(self):
        return self.__url
    
    @property
    def path(self):
        return f"{self.root}/build/toolchains/{self.board.name}-{self.__version}"
    
    def fetch(self) -> bool:
        if not self.isDone(Step.FETCH):
            archive = self.__url.split("/")[-1]
            archivePath = f"{self.root}/build/downloads/{archive}"
            
            self.log.info(f"Downloading toolchain archive {archive}...")
            downloader = Downloader("Stratum.Toolchain")
            if not downloader.download(self.__url, archivePath):
                return False

            self.log.info(f"Extracting toolchain archive {archive}...")
            archiver = Archiver("Stratum.Toolchain")
            if not archiver.extract(archivePath, f"{self.path}"):
                return False

            self.done(Step.FETCH)    
        
        return True
    
    def __resolveWatchVersion(self):
        url = self.__watch["url"]
        pattern = self.__watch["regex_version"]
    
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
        except Exception as e:
            raise RuntimeError(f"Error accessing watch page : {e}")

        cregex = re.compile(pattern)
        versions = cregex.findall(html)

        if not versions:
            raise ValueError(f"No version found on page with pattern : {pattern}")

        def parseVersion(version: str):
            clean = version.lstrip('vV')
            return tuple(map(int, clean.split('.')))
        unique_versions = list(set(versions))
        unique_versions.sort(key=parseVersion)

        latest = unique_versions[-1]
        return latest.lstrip('vV')
