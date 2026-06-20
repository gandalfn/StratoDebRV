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
import json
import importlib.util

from src.common.Log import Log
from src.Recipe import Recipe
from src.system.Stamp import Stamp, Step

class Stratum:
    def __init__(self, context: str, root: str, board):
        self.__log = Log(f"Stratum.{context}")
        self.__name = context
        self.__root = root
        self.__board = board
        self.__stamps = Stamp(f"{root}/build/{self.__board.name}")

        configFile = f"{root}/strata/{self.__board.name}/{context}/stratum.json"
        with open(configFile, "r") as f:
            self.__config = json.load(f)

        self.__recipes = {}

        recipesList = self.__config.get("recipes", [])
        
        for recipeName in recipesList:
            recipePath = f'{self.__root}/recipes/{self.__board.name}/{recipeName}'
            recipeConfigFile = f'{recipePath}/recipe.json'
            
            if not os.path.exists(recipeConfigFile):
                self.__log.error(f"Missing recipe configuration file: {recipeConfigFile}")
                continue

            with open(recipeConfigFile, "r") as f:
                singleRecipeConfig = json.load(f)

            if 'recipe' in singleRecipeConfig:
                recipeClassName = singleRecipeConfig["recipe"]["name"]
            else:
                recipeClassName = singleRecipeConfig["name"]

            recipeScript = f'{recipePath}/{recipeClassName}.py'

            if os.path.exists(recipeScript):
                try:
                    spec = importlib.util.spec_from_file_location(f"recipes.{self.__board.name}.{recipeName}", recipeScript)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    recipeClass = getattr(module, recipeClassName)

                    if not issubclass(recipeClass, Recipe):
                        raise TypeError(f"Class {recipeClassName} is not a subclass of Recipe")

                    self.__log.info(f"Loaded custom recipe class '{recipeClassName}'")
                    self.__recipes[recipeName] = recipeClass(recipeName, self.__log.context, self.__root, self)

                except (ModuleNotFoundError, AttributeError, TypeError) as e:
                    self.__log.warning(f"Failed to load custom class '{recipeClassName}', falling back to default Recipe: {e}")
                    self.__recipes[recipeName] = Recipe(recipeName, self.__log.context, self.__root, self)
            else:
                self.__log.info(f"No custom script found for '{recipeName}'. Using default Recipe engine.")
                self.__recipes[recipeName] = Recipe(recipeName, self.__log.context, self.__root, self)

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
    def log(self):
        return self.__log
    
    @property
    def config(self):
        return self.__config
    
    @property
    def recipes(self):
        return self.__recipes.values()
    
    def __getitem__(self, key):
        return self.__recipes[key]
    
    def isDone(self, step: Step) -> bool:
        return self.__stamps.isDone(f"{self.__log.context}", step)
    
    def done(self, step: Step):
        self.__stamps.done(f"{self.__log.context}", step)

    def fetch(self) -> bool:
        if not self.__stamps.isDone(f"{self.__log.context}", Step.FETCH):
            self.__stamps.done(f"{self.__log.context}", Step.FETCH)
        return True
    
    def configure(self) -> bool:
        self.__log.info(f"Configuring stratum {self.__board.name}...")
        if not self.__stamps.isDone(f"{self.__log.context}", Step.CONFIGURE):
            self.__stamps.done(f"{self.__log.context}", Step.CONFIGURE)
        return True
    
    def build(self) -> bool:
        self.__log.info(f"Building stratum {self.__board.name}...")
        if not self.__stamps.isDone(f"{self.__log.context}", Step.BUILD):
            for recipe in self.recipes:
                if not recipe.fetch():
                    return False
                if not recipe.configure():
                    return False
                if not recipe.build():
                    return False
            self.__stamps.done(f"{self.__log.context}", Step.BUILD)
        return True
    
    def install(self) -> bool:
        self.__log.info(f"Installing stratum {self.__board.name}...")
        if not self.__stamps.isDone(f"{self.__log.context}", Step.INSTALL):
            self.__stamps.done(f"{self.__log.context}", Step.INSTALL)
        return True
    
