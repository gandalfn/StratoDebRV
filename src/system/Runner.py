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


import subprocess
import os

from src.common.Log import Log

class Runner:
    def __init__(self, context: str):
        self.__log = Log(f"{context}")

    def run(self, cmd: list, cwd: str = None, env: dict = None) -> bool:
        self.__log.debug(f"Launching : {' '.join(cmd)}")
        self.__log.debug(f"CWD : {cwd}")
        if env:
            self.__log.debug(f"ENV :")
            for k, v in env.items():
                self.__log.debug(f"     - {k}={v}")
            
        current_env = os.environ.copy()
        if env:
            current_env.update(env)

        try:
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                env=current_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.__log.debug(f"{output.strip()}")

            rc = process.poll()
            if rc != 0:
                self.__log.error(f"Process exited with code : {rc}")
                return False
                
            return True

        except Exception as e:
            self.__log.error(f"Error : {e}")
            return False