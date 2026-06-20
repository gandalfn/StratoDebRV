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
import subprocess

from src.common.Log import Log

class Archiver:
    def __init__(self, context: str):
        self.__log = Log(f"{context}.Archiver")

    def extract(self, archivePath: str, destPath: str) -> bool:
        self.__log.info(f"Extract archive {os.path.basename(archivePath)}...")
        
        if not os.path.exists(archivePath):
            self.__log.error(f"Archive does not exists : {archivePath}")
            return False

        os.makedirs(destPath, exist_ok=True)

        cmd = [
            "tar", 
            "-xf", archivePath, 
            "-C", destPath, 
            "--strip-components=1"
        ]

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.__log.info(f"Extract finished : {destPath}")
            return True
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8').strip()
            self.__log.error(f"Extract failed : {error_msg}")
            return False