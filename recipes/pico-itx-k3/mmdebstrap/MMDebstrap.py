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

class MMDebstrap(Recipe):
    def __init__(self, name: str, context: str, root: str, stratum):
        super().__init__(name, context, root, stratum)

        self.__mirror = self.config["mirror"]
        self.__arch = self.config["arch"]        
        self.__packages = ",".join(self.config.get("packages", []))

    def fetch(self) -> bool:
        if not self.isDone(Step.FETCH):
            self.done(Step.FETCH)
        return True

    def build(self) -> bool:
        self.log.info(f"Build MMDebstrap...")
        if not self.isDone(Step.BUILD):
            os.makedirs(self.buildPath, exist_ok=True)
            cmd = [
                      "mmdebstrap",
                      f"--arch={self.__arch}",
                      "--skip=check/empty",
                      "--verbose"
                  ]
            
            if self.__packages:
                cmd.append(f"--include={self.__packages}")
            
            cmd.extend([
                self.stratum.board.debian,
                f"{self.buildPath}/rootfs.tar.xz",
                self.__mirror
            ])

            if self.runner.run(cmd, f"{self.buildPath}"):
                self.done(Step.BUILD)
            else:
                self.log.error(f"Failed to build MMDebstrap")
                return False
        return True