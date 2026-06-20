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
from enum import Enum
from pathlib import Path

class Step(str, Enum):
    FETCH = "fetch"
    CONFIGURE = "configure"
    BUILD = "build"
    INSTALL = "install"

class Stamp:
    def __init__(self, buildPath: str):
        self.__buildPath = buildPath
        self.__stampPath = f"{self.__buildPath}/stamps"

    def isDone(self, module: str, step: Step) -> bool:
        return os.path.exists(os.path.join(self.__stampPath, f"{module}.{step.value}.stamp"))

    def done(self, module: str, step: Step):
        os.makedirs(self.__stampPath, exist_ok=True)
        Path(os.path.join(self.__stampPath, f"{module}.{step.value}.stamp")).touch()

    def clear(self, module: str, step: Step):
        steps = [Step.FETCH, Step.CONFIGURE, Step.BUILD, Step.INSTALL]
        
        if step in steps:
            idx = steps.index(step)
            for s in steps[idx:]:
                stamp = os.path.join(self.__stampPath, f"{module}.{s.value}.stamp")
                if os.path.exists(stamp):
                    os.remove(stamp)