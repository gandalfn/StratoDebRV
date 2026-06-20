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
from src.Recipe import Recipe

class OpenSBI(Recipe):
    def __init__(self, name: str, context: str, root: str, stratum):
        super().__init__(name, context, root, stratum)

        self.__platform = self.config["platform"]
        self.__defconfig = self.config["defconfig"]

    def build(self) -> bool:
        self.log.info(f"Building OpenSBI...")
        if not self.isDone(Step.BUILD):
            toolchain = self.stratum.board["Toolchain"]
            os.makedirs(self.buildPath, exist_ok=True)
            if self.runner.run([
                                   "make", "-C", f"{self.sourcePath}",
                                   f"-j{os.cpu_count()}", 
                                   f'CC={toolchain.compiler}', 
                                   f'CROSS_COMPILE="{toolchain.crosscompile}"',
                                   f"PLATFORM={self.__platform}",
                                   f"PLATFORM_DEFCONFIG={self.__defconfig}"
                                ], 
                                f"{self.buildPath}",
                                {
                                    'PATH': f'{toolchain.path}/bin:{os.environ["PATH"]}'
                                }):
                self.done(Step.BUILD)
            else:
                self.log.error(f"Failed to build OpenSBI")
                return False
        return True