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
import glob
import json

from src.common.Log import Log
from src.system.Git import Git
from src.system.Runner import Runner
from src.system.Stamp import Stamp, Step
from src.system.Fs import Fs

class Recipe:
    def __init__(self, name: str, context: str, root: str, stratum):
        self.__log = Log(f"{context}.Recipe.{name}")

        self.__git = Git(f"{context}.Recipe.{name}")
        self.__runner = Runner(f"{context}.Recipe.{name}")
        self.__root = root
        self.__board = stratum.board
        self.__stamps = Stamp(f"{root}/build/{self.__board.name}")

        self.__recipePath = f"{self.__root}/recipes/{self.__board.name}/{name}"
        self.__buildPath = f"{self.__root}/build/{self.__board.name}/{name}/build"
        self.__sourcePath = f"{self.__root}/build/{self.__board.name}/{name}/src"
        self.__patchPath = f"{self.__recipePath}/patches"

        configFile = f"{self.__recipePath}/recipe.json"
        with open(configFile, "r") as f:
            self.__config = json.load(f)

        self.__name = self.__config['name']
        self.__url = self.__config['url']
        self.__rev = self.__config['rev']

        self.__files = self.__config.get('files', {})

        if not self.__url or not self.__rev:
            raise Exception(f"Missing configuration (url/rev) in JSON for recipe : {self.__name}")
        
    @property
    def name(self):
        return self.__name
    
    @property
    def root(self):
        return self.__root
    
    @property
    def board(self):
        return self.__board
    
    @property
    def runner(self):
        return self.__runner
    
    @property
    def log(self):
        return self.__log
    
    @property
    def config(self):
        return self.__config
    
    @property
    def recipePath(self):
        return self.__recipePath
    
    @property
    def sourcePath(self):
        return self.__sourcePath
    
    @property
    def buildPath(self):
        return self.__buildPath
    
    def isDone(self, step: Step) -> bool:
        return self.__stamps.isDone(f"{self.__log.context}", step)
    
    def done(self, step: Step):
        self.__stamps.done(f"{self.__log.context}", step)
        
    def fetch(self) -> bool:
        if not self.__stamps.isDone(f"{self.__log.context}", Step.FETCH):
            if not self.__git.sync(self.__url, self.__sourcePath, self.__rev, depth=1):
                self.__log.error(f"Failed to fetch {self.__url} rev {self.__rev}")
                return False
            
            for srcFile, dstFile in self.__files.items():
                src = srcFile.format(sourcePath=self.__sourcePath, recipePath=self.__recipePath, rootPath=self.__root)
                dst = dstFile.format(sourcePath=self.__sourcePath, recipePath=self.__recipePath, rootPath=self.__root)
                self.__log.info(f"Copying {src} to {dst}...")
                if not Fs.cp(src, dst):
                    self.__log.error(f"Failed to copy {src} to {dst}")
                    return False
                
            if os.path.isdir(self.__patchPath):
                self.__log.info(f"Collecting patches from {self.__patchPath}...")
                patches = sorted(glob.glob(os.path.join(self.__patchPath, "*.patch")))
                
                for patch in patches:
                    self.__log.info(f"Applying patch {patch}...")
                    if not self.__git.applyPatch(self.__sourcePath, patch):
                        self.__log.error(f"Failed to apply patch {patch}")
                        return False
            
            self.__stamps.done(f"{self.__log.context}", Step.FETCH)

        return True
    
    def configure(self) -> bool:
        if not self.__stamps.isDone(f"{self.__log.context}", Step.CONFIGURE):
            self.__stamps.done(f"{self.__log.context}", Step.CONFIGURE)
        return True
    
    def build(self) -> bool:
        if not self.__stamps.isDone(f"{self.__log.context}", Step.BUILD):
            self.__stamps.done(f"{self.__log.context}", Step.BUILD)
        return True
    
    def install(self) -> bool:
        if not self.__stamps.isDone(f"{self.__log.context}", Step.INSTALL):
            self.__stamps.done(f"{self.__log.context}", Step.INSTALL)
        return True