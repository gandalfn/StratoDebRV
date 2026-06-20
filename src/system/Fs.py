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
import shutil

from src.common.Log import Log

class Fs:
    @staticmethod
    def mkdir(path: str) -> bool:
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            return False

    @staticmethod
    def cp(src: str, dst: str) -> bool:
        try:
            dstDir = os.path.dirname(dst) if not os.path.isdir(dst) else dst
            if dstDir:
                os.makedirs(dstDir, exist_ok=True)

            shutil.copy2(src, dst)
            return True
        except Exception as e:
            return False

    @staticmethod
    def cpDir(src: str, dst: str) -> bool:
        try:
            shutil.copytree(src, dst, dirs_exist_ok=True)
            return True
        except Exception as e:
            return False

    @staticmethod
    def rmDir(path: str) -> bool:
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
            return True
        except Exception as e:
            return False

    @staticmethod
    def rm(path: str) -> bool:
        try:
            if os.path.exists(path):
                os.remove(path)
            return True
        except Exception as e:
            return False
        
    @staticmethod
    def chmod(path: str, mode: int) -> bool:
        try:
            os.chmod(path, mode)
            return True
        except Exception as e:
            return False

    @staticmethod
    def exists(path: str) -> bool:
        return os.path.exists(path)