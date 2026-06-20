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


import os
import sys
import urllib.request
from datetime import datetime

from src.common.Log import Log

class Downloader:
    __color = "\033[32m"
    __reset = "\033[0m"
    __bold = "\033[1m"


    def __init__(self, context: str):
        self.__context = context
        self.__log = Log(f"{context}.Downloader")

    def download(self, url: str, destPath: str) -> bool:
        if os.path.exists(destPath):
            self.__log.info(f"The file already exists : {os.path.basename(destPath)}")
            return True

        self.__log.info(f"Starting download : {url}")
        
        os.makedirs(os.path.dirname(destPath), exist_ok=True)

        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'StratoDebRV-Bootstrap'})
            
            with urllib.request.urlopen(req) as response:
                totalSize = int(response.info().get('Content-Length', 0))
                blockSize = 1024 * 64
                downloaded = 0

                with open(destPath, 'wb') as f:
                    while True:
                        buffer = response.read(blockSize)
                        if not buffer:
                            break
                        f.write(buffer)
                        downloaded += len(buffer)
                        
                        if totalSize > 0:
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            color = self.__color
                            percent = int(downloaded * 100 / totalSize)
                            sys.stdout.write(f"\r[{timestamp}] {color}{self.__bold}DOWNLOAD{self.__reset} [{self.__context}.Downloader] {os.path.basename(destPath)} : {percent}% ({downloaded // 1024 // 1024} Mo / {totalSize // 1024 // 1024} Mo)")
                            sys.stdout.flush()
                
                print("") 
            self.__log.info("Download completed.")
            return True

        except Exception as e:
            print("")
            self.__log.error(f"Error during download : {e}")
            if os.path.exists(destPath):
                os.remove(destPath)
            return False