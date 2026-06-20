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


import configparser

from src.common.Log import Log

class Main:
    def __init__(self, root: str):
        self.__log = Log("Main")

        self.__log.info("Loading main configuration...")
        self.__config = configparser.ConfigParser()
        self.__config.read(f"{root}/config.ini")

        self.__version = self.__config.get("main", "version")
        self.__debian = self.__config.get("main", "debian")
        self.__board = self.__config.get("main", "board")

        self.__log.debug(f"Main configuration loaded:")
        self.__log.debug(f"  -> Version: {self.__version}")
        self.__log.debug(f"  -> Debian: {self.__debian}")
        self.__log.debug(f"  -> Board: {self.__board}")

    @property
    def version(self):
        return self.__version

    @property
    def debian(self):
        return self.__debian

    @property
    def board(self):
        return self.__board