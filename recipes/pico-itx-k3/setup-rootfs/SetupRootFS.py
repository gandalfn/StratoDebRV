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
from src.system.Archiver import Archiver
from src.system.Fs import Fs
from src.system.Runner import Runner
from src.Recipe import Recipe

class SetupRootFS(Recipe):
    def __init__(self, name: str, context: str, root: str, stratum):
        super().__init__(name, context, root, stratum)

        self.__mirror = self.config["mirror"]

    @property
    def path(self) -> str:
        return f"{self.buildPath}/rootfs"

    def fetch(self) -> bool:
        if not self.isDone(Step.FETCH):
            self.log.info(f"Fetch Setup RootFS...")
            rootfs = self.stratum.board["RootFS"]
            archiver = Archiver(self.log.context)
            Fs.mkdir(self.buildPath)
            if not archiver.extract(f"{rootfs.outputPath}/rootfs.tar.xz", self.path, fakeRoot=True):
                self.log.error(f"Error on fetch rootfs")
                return False
            self.done(Step.FETCH)
        return True

    def configure(self) -> bool:
        self.log.info(f"Configure Setup RootFS...")
        if not self.isDone(Step.CONFIGURE):
            sourcesList = f"{self.path}/etc/apt/sources.list"
            with open(sourcesList, 'w') as f:
                f.write(f"deb {self.__mirror} {self.stratum.board.debian} main\n" )
                f.write(f"deb-src {self.__mirror} {self.stratum.board.debian} main\n" )

            runner = Runner(f"{self.log.context}")
            cmd = [
                "fakechroot", "fakeroot", "chroot", self.path, 
                "apt", "update"
            ]
            if not runner.run(cmd, self.buildPath):
                self.log.error(f"Error on configure rootfs")
                return False
            self.done(Step.CONFIGURE)
        return True

    def build(self) -> bool:
        self.log.info(f"Build Setup RootFS...")
        if not self.isDone(Step.BUILD):
            runner = Runner(f"{self.log.context}")
            cmd = [
                "fakechroot", "fakeroot", "chroot", self.path, 
                "apt", "install", "-y", "devscripts", "dpkg-dev", "quilt"
            ]
            if not runner.run(cmd, self.buildPath):
                self.log.error(f"Error on build rootfs")
                return False
            cmd = [
                'sed', '-i', "s|/usr/lib/riscv64-linux-gnu/||g", f'{self.path}/usr/lib/riscv64-linux-gnu/libc.so'
            ]
            if not runner.run(cmd, self.buildPath):
                self.log.error(f"Error on build rootfs")
                return False
            
            cmd = [
                'sed', '-i', "s|/lib/riscv64-linux-gnu/||g", f'{self.path}/usr/lib/riscv64-linux-gnu/libc.so'
            ]
            if not runner.run(cmd, self.buildPath):
                self.log.error(f"Error on build rootfs")
                return False
            
            cmd = [
                'sed', '-i', "s|/usr/lib/riscv64-linux-gnu/||g", f'{self.path}/usr/lib/riscv64-linux-gnu/libpthread.so.0'
            ]
            if not runner.run(cmd, self.buildPath):
                self.log.error(f"Error on build rootfs")
                return False
            
            cmd = [
                'sed', '-i', "s|/lib/riscv64-linux-gnu/||g", f'{self.path}/usr/lib/riscv64-linux-gnu/libpthread.so.0'
            ]
            if not runner.run(cmd, self.buildPath):
                self.log.error(f"Error on build rootfs")
                return False
            
            self.done(Step.BUILD)
        return True
    
    def cleanup(self) -> bool:
        return True