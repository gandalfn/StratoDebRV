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

class Wrapper(Recipe):
    def __init__(self, name: str, context: str, root: str, stratum):
        super().__init__(name, context, root, stratum)

        self.__arch = self.config["arch"]

    @property
    def path(self) -> str:
        return f"{self.buildPath}/bin"
    
    def fetch(self) -> bool:
        if not self.isDone(Step.FETCH):
            self.done(Step.FETCH)
        return True

    def configure(self) -> bool:
        self.log.info(f"Configure Wrapper...")
        if not self.isDone(Step.CONFIGURE):
            rootfs = self.stratum["setup-rootfs"]
            toolchain = self.stratum.board["Toolchain"]
            Fs.mkdir(self.path)
            
            with open(f"{self.path}/{self.__arch}-gcc", "w") as f:
                f.write(f"#!/bin/sh\n\n")
                f.write(f'if [ "$GLIBC_BUILD" = "1" ]; then\n')
                f.write(f'exec "{toolchain.path}/bin/{toolchain.arch}-gcc" \\\n')
                f.write(f'      {toolchain.cflags}\\\n')
                f.write(f'      --sysroot="{rootfs.path}" \\\n')
                f.write(f'      -B"{rootfs.path}/usr/lib/{self.__arch}" \\\n')
                f.write(f'      -B"{rootfs.path}/lib/{self.__arch}" \\\n')
                f.write(f'      -L"{rootfs.path}/usr/lib/{self.__arch}" \\\n')
                f.write(f'      -L"{rootfs.path}/lib/{self.__arch}" \\\n')
                f.write(f'      "$@" \\\n')
                f.write(f'      -ldl\n')
                f.write(f'else\n')
                f.write(f'exec "{toolchain.path}/bin/{toolchain.arch}-gcc" \\\n')
                f.write(f'      {toolchain.cflags}\\\n')
                f.write(f'      --sysroot="{rootfs.path}" \\\n')
                f.write(f'      -B"{rootfs.path}/usr/lib/{self.__arch}" \\\n')
                f.write(f'      -B"{rootfs.path}/lib/{self.__arch}" \\\n')
                f.write(f'      -I"{rootfs.path}/usr/include/{self.__arch}" \\\n')
                f.write(f'      -I"{rootfs.path}/usr/include" \\\n')
                f.write(f'      -I"{rootfs.path}/include" \\\n')
                f.write(f'      -L"{rootfs.path}/usr/lib/{self.__arch}" \\\n')
                f.write(f'      -L"{rootfs.path}/lib/{self.__arch}" \\\n')
                f.write(f'      "$@" \\\n')
                f.write(f'      -ldl\n')
                f.write(f'fi\n')
            Fs.chmod(f"{self.path}/{self.__arch}-gcc", 0o755)
            
            with open(f"{self.path}/{self.__arch}-g++", "w") as f:
                f.write(f"#!/bin/sh\n\n")
                f.write(f'if [ "$GLIBC_BUILD" = "1" ]; then\n')
                f.write(f'exec "{toolchain.path}/bin/{toolchain.arch}-g++" \\\n')
                f.write(f'      {toolchain.cflags}\\\n')
                f.write(f'      --sysroot="{rootfs.path}" \\\n')
                f.write(f'      -B"{rootfs.path}/usr/lib/{self.__arch}" \\\n')
                f.write(f'      -B"{rootfs.path}/lib/{self.__arch}" \\\n')
                f.write(f'      -L"{rootfs.path}/usr/lib/{self.__arch}" \\\n')
                f.write(f'      -L"{rootfs.path}/lib/{self.__arch}" \\\n')
                f.write(f'      "$@" \\\n')
                f.write(f'      -ldl\n')
                f.write(f'else\n')
                f.write(f'exec "{toolchain.path}/bin/{toolchain.arch}-g++" \\\n')
                f.write(f'      {toolchain.cflags}\\\n')
                f.write(f'      --sysroot="{rootfs.path}" \\\n')
                f.write(f'      -B"{rootfs.path}/usr/lib/{self.__arch}" \\\n')
                f.write(f'      -B"{rootfs.path}/lib/{self.__arch}" \\\n')
                f.write(f'      -I"{rootfs.path}/usr/include/{self.__arch}" \\\n')
                f.write(f'      -I"{rootfs.path}/usr/include" \\\n')
                f.write(f'      -I"{rootfs.path}/include" \\\n')
                f.write(f'      -L"{rootfs.path}/usr/lib/{self.__arch}" \\\n')
                f.write(f'      -L"{rootfs.path}/lib/{self.__arch}" \\\n')
                f.write(f'      "$@" \\\n')
                f.write(f'      -ldl\n')
                f.write(f'fi\n')
            Fs.chmod(f"{self.path}/{self.__arch}-g++", 0o755)

            with open(f"{self.path}/dpkg-shlibdeps", "w") as f:
                f.write(f"#!/bin/sh\n\n")
                f.write(f'exec /usr/bin/dpkg-shlibdeps \\\n')
                f.write(f'      --ignore-missing-info \\\n')
                f.write(f'      --admindir="{rootfs.path}/var/lib/dpkg" \\\n')
                f.write(f'      -l"{rootfs.path}/usr/lib/riscv64-linux-gnu" \\\n')
                f.write(f'      -l"{rootfs.path}/lib/riscv64-linux-gnu" \\\n')
                f.write(f'      "$@"\n')
            Fs.chmod(f"{self.path}/dpkg-shlibdeps", 0o755)

            self.done(Step.CONFIGURE)
        return True

    def cleanup(self) -> bool:
        return True

