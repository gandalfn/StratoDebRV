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
from src.system.Debian import PackagePatch
from src.system.Fs import Fs
from src.system.Runner import Runner
from src.Recipe import Recipe

class BinUtils(Recipe):
    def __init__(self, name: str, context: str, root: str, stratum):
        super().__init__(name, context, root, stratum)

        self.__package = self.config["package"]
        self.__version = self.config["version"]
        self.__packagePatch = PackagePatch(self.log.context, f'{self.buildPath}/{self.__package}-{self.__version}', self.config.get("patches", []))

    def fetch(self) -> bool:
        if not self.isDone(Step.FETCH):
            self.log.info(f"Fetch BinUtils...")
            Fs.mkdir(self.buildPath)
            rootfs = self.stratum["setup-rootfs"]
            runner = Runner(f"{self.log.context}")
            cmd = [
                "fakechroot", "fakeroot", "chroot", rootfs.path, "apt", "source", self.__package
            ]
            if not runner.run(cmd, self.buildPath):
                self.log.error(f"Error on fetch {self.__package}")
                return False
            if not Fs.mv(f"{rootfs.path}/{self.__package}?{self.__version}*", f"{self.buildPath}"):
                self.log.error(f"Error on fetch {self.__package}")
                return False
            self.done(Step.FETCH)
        return True

    def configure(self) -> bool:
        self.log.info(f"Configure BinUtils...")
        if not self.isDone(Step.CONFIGURE):
            rootfs = self.stratum["setup-rootfs"]
            runner = Runner(f"{self.log.context}")
            cmd = [
                "fakechroot", "fakeroot", "chroot", rootfs.path, "apt", "build-dep", "-y", self.__package
            ]
            if not runner.run(cmd, self.buildPath):
                self.log.error(f"Error on fetch  build-dep {self.__package}")
                return False
            if not self.__packagePatch.configure(self.recipePath):
                self.log.error(f"Error on configure {self.__package}")
                return False
            self.done(Step.CONFIGURE)
        return True
    
    def build(self) -> bool:
        self.log.info(f"Build BinUtils...")
        if not self.isDone(Step.BUILD):
            rootfs = self.stratum["setup-rootfs"]
            wrapper = self.stratum["wrapper"]
            toolchain = self.stratum.board["Toolchain"]
            env = {
                'PATH': f"{wrapper.path}:{toolchain.path}/bin:{os.environ['PATH']}",
                'PKG_CONFIG_DIR': f"",
                'PKG_CONFIG_PATH': f"{rootfs.path}/usr/lib/pkgconfig:{rootfs.path}/usr/lib/riscv64-linux-gnu/pkgconfig",
                'PKG_CONFIG_LIBDIR': f"{rootfs.path}/usr/lib/pkgconfig:{rootfs.path}/usr/lib/riscv64-linux-gnu/pkgconfig",
                'PKG_CONFIG_SYSROOT_DIR': f"{rootfs.path}"
            }
            if not self.__packagePatch.build(toolchain.arch.split("-")[0], env):
                self.log.error(f"Error on build {self.__package}")
                return False
            self.done(Step.BUILD)
        return True