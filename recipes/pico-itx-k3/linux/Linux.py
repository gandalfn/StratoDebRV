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

# Based on work from pyavitz/debian-image-builder
# https://github.com/pyavitz/debian-image-builder
# Licensed under GPL-2.0 (see: https://github.com/pyavitz/debian-image-builder/blob/feature/COPYING)


import os

from src.system.Stamp import Step
from src.system.Fs import Fs
from src.Recipe import Recipe

class Linux(Recipe):
    def __init__(self, name: str, context: str, root: str, stratum):
        super().__init__(name, context, root, stratum)

        self.__defconfig = self.config["defconfig"]
        self.__arch = self.config["arch"] 
        version = self.config["version"]
        def parseVersion(version: str):
            clean = version.lstrip('vV')
            return tuple(map(int, clean.split('.')))
        self.__version = parseVersion(version)

    def configure(self) -> bool:
        self.log.info(f"Configuring Linux...")
        if not self.isDone(Step.CONFIGURE):
            toolchain = self.stratum.board["Toolchain"]
            if self.runner.run([
                                   "make", "-C", f"{self.sourcePath}", 
                                   f"ARCH={self.__arch}",
                                   f'CC={toolchain.compiler}', 
                                   f'CFLAGS="{toolchain.cflags}"',
                                   f'CROSS_COMPILE={toolchain.crosscompile}',
                                   self.__defconfig
                                ], 
                                f"{self.sourcePath}",
                                {
                                    'PATH': f'{toolchain.path}/bin:{os.environ["PATH"]}'
                                }):
                self.done(Step.CONFIGURE)
            else:
                self.log.error(f"Failed to configure Linux")
                return False
        return True
    
    def build(self) -> bool:
        self.log.info(f"Building Linux...")
        if not self.isDone(Step.BUILD):
            toolchain = self.stratum.board["Toolchain"]
            if self.runner.run([
                                   "make", "-C", f"{self.sourcePath}", 
                                   f"-j{os.cpu_count()}",
                                   f"ARCH={self.__arch}",
                                   f'CC={toolchain.compiler}', 
                                   f'CFLAGS="{toolchain.cflags}"',
                                   f'CROSS_COMPILE={toolchain.crosscompile}',
                                   f'KBUILD_BUILD_USER=gandalfn',
                                   f'KBUILD_BUILD_HOST=gondor.com',
                                   f'KDEB_COMPRESS=xz',
                                   f'KERNELRELEASE={self.__version[0]}.{self.__version[1]}+{self.stratum.board.name}',
                                   f'KDEB_PKGVERSION={self.__version[0]}.{self.__version[1]}.{self.__version[2]}',
                                   f'bindeb-pkg'
                                ], 
                                f"{self.sourcePath}",
                                {
                                    'PATH': f'{toolchain.path}/bin:{os.environ["PATH"]}'
                                }):
                self.done(Step.BUILD)
            else:
                self.log.error(f"Failed to build Linux")
                return False
        return True