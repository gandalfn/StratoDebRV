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


import sys
from datetime import datetime
from enum import IntEnum

class LogLevel(IntEnum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4

class Log:
    __level = LogLevel.DEBUG
    
    __colors = {
        LogLevel.DEBUG: "\033[36m",
        LogLevel.INFO: "\033[32m",
        LogLevel.WARNING: "\033[33m",
        LogLevel.ERROR: "\033[31m",
    }
    __reset = "\033[0m"
    __bold = "\033[1m"

    def __init__(self, context: str):
        self.__context = context

    @classmethod
    def setLevel(cls, level: LogLevel):
        cls.__level = level

    @property
    def context(self):
        return self.__context

    def __log(self, level: LogLevel, message: str, stream=sys.stdout):
        if level >= self.__level:
            timestamp = datetime.now().strftime("%H:%M:%S")
            color = self.__colors.get(level, "")
            levelName = level.name.ljust(7)
            
            sys.stdout.flush()
            print(
                f"[{timestamp}] {color}{self.__bold}{levelName}{self.__reset}  "
                f"[{self.__context}] {message}",
                file=stream
            )

    def debug(self, message: str):
        self.__log(LogLevel.DEBUG, message)

    def info(self, message: str):
        self.__log(LogLevel.INFO, message)

    def warning(self, message: str):
        self.__log(LogLevel.WARNING, message)

    def error(self, message: str):
        self.__log(LogLevel.ERROR, message, stream=sys.stderr)
