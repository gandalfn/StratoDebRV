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
from src.system.Debian import Package as DebianPackage
from src.Recipe import Recipe

class UBoot(Recipe):
    def __init__(self, name: str, context: str, root: str, stratum):
        super().__init__(name, context, root, stratum)

        self.__defconfig = self.config["defconfig"]

        self.__package = DebianPackage(self.log.context, self.config.get("debian-package", {}))

    def configure(self) -> bool:
        self.log.info(f"Updating U-Boot defconfig...")
        self.__updateDefconfig(f"{self.sourcePath}/configs/{self.__defconfig}")
        
        self.log.info(f"Configuring U-Boot...")
        if not self.isDone(Step.CONFIGURE):
            toolchain = self.stratum.board["Toolchain"]
            Fs.mkdir(self.buildPath)
            if self.runner.run([
                                   "make", "-C", f"{self.sourcePath}", 
                                   f'CC={toolchain.compiler}', 
                                   f'CFLAGS="{toolchain.cflags}"',
                                   f'CROSS_COMPILE={toolchain.crosscompile}',
                                   self.__defconfig
                                ], 
                                f"{self.buildPath}",
                                {
                                    'PATH': f'{toolchain.path}/bin:{os.environ["PATH"]}'
                                }):
                self.done(Step.CONFIGURE)
            else:
                self.log.error(f"Failed to configure U-Boot")
                return False
        return True
    
    def build(self) -> bool:
        self.log.info(f"Building U-Boot...")
        if not self.isDone(Step.BUILD):
            toolchain = self.stratum.board["Toolchain"]
            os.makedirs(self.buildPath, exist_ok=True)

            if not self.runner.run([
                                   "make", "-C", f"{self.sourcePath}", 
                                   f"-j{os.cpu_count()}", 
                                   f'CC={toolchain.compiler}', 
                                   f'CFLAGS="{toolchain.cflags}"',
                                   f'CROSS_COMPILE={toolchain.crosscompile}',
                                ], 
                                f"{self.buildPath}",
                                {
                                    'PATH': f'{toolchain.path}/bin:{os.environ["PATH"]}'
                                }):
                return False

            if self.__package.build(self):            
                self.done(Step.BUILD)
            else:
                self.log.error(f"Failed to build U-Boot")
                return False
        return True
    
    def __updateDefconfig(self, defconfig: str):
        needed = [
            "CONFIG_SD_BOOT=y",
            "CONFIG_EXT4_WRITE=y",
            "CONFIG_FS_BTRFS=y",
            "CONFIG_CMD_BTRFS=y",
            "CONFIG_CMD_CAT=y"
        ]
        
        with open(defconfig, "r") as f:
            lines = f.readlines()

        cleanedLines = [line.strip() for line in lines]

        modified = False

        for cfg in needed:
            if cfg not in cleanedLines:
                lines.append(f"{cfg}\n")
                cleanedLines.append(cfg)
                modified = True

        target_sed = "# CONFIG_CMD_SETEXPR is not set"
        for idx, line in enumerate(lines):
            if target_sed in line:
                lines[idx] = line.replace(target_sed, "")
                modified = True

        if modified:
            with open(defconfig, "w") as f:
                f.writelines(lines)