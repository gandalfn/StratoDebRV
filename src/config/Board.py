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


import json
import os
import importlib.util

from src.common.Log import Log
from src.strata.Stratum import Stratum

class Board:
    def __init__(self, root: str, board: str, debian: str):

        self.__log = Log("Board")

        self.__log.info(f"Loading board configuration for {board}...")
        
        self.__root = root
        self.__board = board
        self.__debian = debian

        self.__log.info(f"Loading toolchain configuration for {self.__board}...")

        configFile = f"{root}/boards/{self.__board}.json"
        with open(configFile, "r") as f:
            self.__config = json.load(f)

        self.__name = self.__config["name"]
        self.__version = self.__config["version"]

        self.__stratums = {}

        strataList = self.__config.get("strata", [])
        
        for stratumName in strataList:
            stratumPath = f'{self.__root}/strata/{self.__name}/{stratumName}'
            stratumConfigFile = f'{stratumPath}/stratum.json'
            
            if not os.path.exists(stratumConfigFile):
                self.__log.error(f"Missing stratum configuration file: {stratumConfigFile}")
                continue

            stratumScript = f'{stratumPath}/{stratumName}.py'

            loaded = False
            if os.path.exists(stratumScript):
                try:
                    spec = importlib.util.spec_from_file_location(f"strata.{self.__name}.{stratumName}", stratumScript)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    stratumClass = getattr(module, stratumName)

                    if not issubclass(stratumClass, Stratum):
                        raise TypeError(f"Class {stratumName} is not a subclass of Stratum")

                    self.__log.info(f"Loaded custom strata class '{stratumName}'")
                    self.__stratums[stratumName] = stratumClass(self.__root, self)

                    loaded = True
                except (ModuleNotFoundError, AttributeError, TypeError) as e:
                    self.__log.warning(f"Failed to load custom class '{stratumName}', falling back to default Stratum {stratumName}: {e}")
 
            if not loaded:
                try:
                    self.__log.info(f"Loading default strata class '{stratumName}'")
                    stratumScript = f"{self.__root}/src/strata/{stratumName}.py"
            
                    if not os.path.exists(stratumScript):
                        self.__log.error(f"Missing stratum script file: {stratumScript}")
                        continue

                    spec = importlib.util.spec_from_file_location(f"src.strata.{stratumName}", stratumScript)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                
                    stratumClass = getattr(module, stratumName)
                
                    if not issubclass(stratumClass, Stratum):
                        raise TypeError(f"Class {stratumName} is not a subclass of Stratum")

                    self.__log.info(f"Loaded default class '{stratumName}'")
                    self.__stratums[stratumName] = stratumClass(self.__root, self)
                except (ModuleNotFoundError, AttributeError, TypeError) as e:
                    self.__log.error(f"Error loading strata class '{stratumName}': {e}")

        self.__log.debug(f"Board configuration loaded:")
        self.__log.debug(f"  -> Name: {self.__name}")
        self.__log.debug(f"  -> Version: {self.__version}")


    @property
    def name(self):
        return self.__name
    
    @property
    def version(self):
        return self.__version
    
    @property
    def debian(self):
        return self.__debian
    
    @property
    def strata(self):
        return self.__stratums.values()
    
    def __getitem__(self, key):
        return self.__stratums[key]
