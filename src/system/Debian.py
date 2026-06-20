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


from src.common.Log import Log
from src.system.Fs import Fs
from src.system.Runner import Runner

class Package:
    def __init__(self, context: str, config: dict):
        self.__name = config['name']
        self.__version = config['version']
        self.__arch = config['arch']
        self.__description = config['description']
        self.__preinstall = config.get('preinst', [])
        self.__postinstall = config.get('postinst', [])
        self.__files = config.get('files', {})

        self.__log = Log(f"{context}.Package.{self.__name}")
    
    def build(self, recipe) -> bool:
        self.__log.info(f"Building package {self.__name}_{self.__version}_{self.__arch}...")

        targetPath = f'{recipe.buildPath}/{self.__name}_{self.__version}_{self.__arch}'
        Fs.mkdir(f'{targetPath}/DEBIAN')

        with open(f'{targetPath}/DEBIAN/control', 'w') as f:
            f.write(f'Package: {self.__name}\n')
            f.write(f'Version: {self.__version}\n')
            f.write(f'Architecture: {self.__arch}\n')
            f.write(f'Maintainer: gandalfn <gandalfn@gondor.com>\n')
            f.write(f'Description: {self.__description}\n')

        if self.__preinstall:
            with open(f'{targetPath}/DEBIAN/preinst', 'w') as f:
                f.write('#!/bin/sh\n\n')
                f.write('set -e\n\n')
                for command in self.__preinstall:
                    f.write(f'{command}\n')
                f.write('exit 0\n')
            Fs.chmod(f'{targetPath}/DEBIAN/preinst', 0o755)
        
        if self.__postinstall:
            with open(f'{targetPath}/DEBIAN/postinst', 'w') as f:
                f.write('#!/bin/sh\n\n')
                f.write('set -e\n\n')
                for command in self.__postinstall:
                    f.write(f'{command}\n')
                f.write('exit 0\n')
            Fs.chmod(f'{targetPath}/DEBIAN/postinst', 0o755)

        for srcFile, dstFile in self.__files.items():
            src = srcFile.format(sourcePath=recipe.sourcePath, recipePath=recipe.recipePath, rootPath=recipe.root, targetPath=targetPath)
            dst = dstFile.format(sourcePath=recipe.sourcePath, recipePath=recipe.recipePath, rootPath=recipe.root, targetPath=targetPath)
            if not Fs.cp(src, dst):
                self.__log.error(f"Failed to copy {src} to {dst}")
                return False
            
        runner = Runner(self.__log.context)
        if not runner.run(['dpkg-deb', '-Zxz', '--build', '--root-owner-group', f'{targetPath}'], recipe.buildPath):
            self.__log.error(f"Failed to build package {self.__name}_{self.__version}")
            return False
                
        return True