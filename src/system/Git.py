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

from src.common.Log import Log
from src.system.Runner import Runner

class Git:
    def __init__(self, context: str):
        self.__log = Log(f"{context}.Git")
        self.__runner = Runner(f"{context}.Git")

    def sync(self, url: str, destPath: str, reference: str = "main", depth: int = None) -> bool:
        gitPath = os.path.join(destPath, ".git")
        
        if not os.path.exists(gitPath):
            self.__log.info(f"Initialize git repository {url}...")
            os.makedirs(destPath, exist_ok=True)
            
            if not self.__runner.run(["git", "init"], cwd=destPath):
                return False
            if not self.__runner.run(["git", "remote", "add", "origin", url], cwd=destPath):
                return False

        self.__log.info(f"Fetch '{reference}'...")
        fetch = ["git", "fetch", "origin"]
        if depth:
            fetch.extend(["--depth", str(depth)])
        fetch.append(reference)
        
        if not self.__runner.run(fetch, cwd=destPath):
            self.__log.warning("Fetch failed, trying fallback...")
            fallback = ["git", "fetch", "origin"]
            if not self.__runner.run(fallback, cwd=destPath):
                return False

        self.__log.info(f"Checkout {reference}...")
        checkout = ["git", "checkout", reference]
        if not self.__runner.run(checkout, cwd=destPath):
            self.__log.warning("Checkout failed...")
            return False

        return True

    def applyPatch(self, targetPath: str, patchPath: str) -> bool:
        self.__log.info(f"Apply patch {os.path.basename(patchPath)} on {os.path.basename(targetPath)}...")
        
        check = ["git", "-C", targetPath, "apply", "--check", patchPath]
        if self.__runner.run(check):
            apply = ["git", "-C", targetPath, "apply", patchPath]
            return self.__runner.run(apply)
        
        self.__log.warning("Patch already applied or has conflicts.")
        return True
