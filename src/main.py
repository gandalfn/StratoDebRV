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

from src.common.Log import Log, LogLevel
from src.config.Main import Main
from src.config.Board import Board
from src.system.Runner import Runner

def main(ROOT_DIR):
    Log.setLevel(LogLevel.DEBUG)

    log = Log("Bootstrap")
    log.info("Starting bootstrap...")
    
    try:
        log.info("Loading main configuration...")
        mainConfig = Main(str(ROOT_DIR))
    
        log.info(f"Loading board configuration for {mainConfig.board}...")
        boardConfig = Board(str(ROOT_DIR), mainConfig.board)

        log.info("Fetching strata...")        
        for stratum in boardConfig.strata:
            if not stratum.fetch():
                log.error(f"Failed to fetch stratum {stratum.name}")
                sys.exit(1)
            if not stratum.configure():
                log.error(f"Failed to configure stratum {stratum.name}")
                sys.exit(1)
            if not stratum.build():
                log.error(f"Failed to build stratum {stratum.name}")
                sys.exit(1)
            if not stratum.install():
                log.error(f"Failed to install stratum {stratum.name}")
                sys.exit(1)
            
    except Exception as e:
        log.error(f"Error during bootstrap : {e}")
        sys.exit(1)
