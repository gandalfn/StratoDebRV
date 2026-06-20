# StratoDebRV

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v2](https://img.shields.io/badge/License-GPL_v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html)
[![Codeberg](https://img.shields.io/badge/Codeberg-Primary-brightgreen?logo=codeberg)](https://codeberg.org/gandalfn/StratoDebRV)
[![GitHub](https://img.shields.io/badge/GitHub-Mirror-lightgrey?logo=github)](https://github.com/gandalfn/StratoDebRV)

> **📍 Primary Repository**: This repository is **hosted on Codeberg** at [https://codeberg.org/gandalfn/StratoDebRV](https://codeberg.org/gandalfn/StratoDebRV).
> The GitHub version is a **read-only mirror** for better discoverability. **All development, issues, and pull requests happen on Codeberg.**

**StratoDebRV** (Stratified Debian for RISC-V) is a personal bootstrap tool for building **Debian-based system images** for RISC-V Single Board Computers (SBCs), with a primary focus on the **Spacemit pico-itx-k3** board.

###  Why This Project?

My initial motivation was to create a complete, reproducible workflow for generating Debian images for RISC-V SBCs. The specific goals were:

- **Build core firmware components**: Automatically generate latest versions of **U-Boot**, **OpenSBI**, and the **Linux kernel** with board-specific configurations
- **Create custom Debian root filesystem**: Build a tailored rootfs with Debian packages
- **Patch management**: Collect and apply all vendor-specific patches to Debian packages, then rebuild them for the target SBC
- **Vendor package integration**: Include additional manufacturer packages (like Spacemit's) in the final image
- **Reproducible builds**: Ensure the entire process can be repeated with the same results, tracking all patches and modifications

This project was heavily inspired by and learned from the excellent [debian-image-builder](https://github.com/pyavitz/debian-image-builder) project by [pyavitz](https://github.com/pyavitz), which provided valuable insights into structuring a modular Debian-based image builder.

> **Note**: This is a personal project designed for my specific needs with RISC-V SBCs. It is **not** intended as a replacement for established build systems like Yocto, Arch Linux, Buildroot, or OpenWrt. For production-grade embedded Linux builds, please consider using those well-tested solutions.

## Features

- **Modular Design**: Organized into strata (Toolchain, Firmware, etc.) and recipes
- **Reproducibility**: Timestamp system to avoid re-executing completed steps
- **Flexibility**: Customizable recipes in Python or use the default engine
- **Multi-Board Support**: Support for different RISC-V boards via dedicated configurations
- **Automatic Downloads**: Source retrieval from Git, automatic patch application
- **Declarative Configuration**: JSON files to define dependencies and parameters
- **Detailed Logging**: Colorized output with different verbosity levels

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Debian-based Linux system (recommended for cross-building)
- Internet connection for downloading sources
- Sufficient disk space (10+ GB recommended)

### Installation

On Debian, install the required packages:

```bash
# Update package lists
sudo apt update

# Required packages for StratoDebRV
sudo apt install -y python3 python3-pip git build-essential ccache

# Additional packages for cross-compilation (optional but recommended)
sudo apt install -y gawk bison flex texinfo libssl-dev bc device-tree-compiler
```

Then clone and set up StratoDebRV:

```bash
# Clone the repository
git clone https://codeberg.org/gandalfn/StratoDebRV.git StratoDebRV
cd StratoDebRV

# Make the script executable
chmod +x StratoDeb
```

> **Note**: StratoDebRV only uses Python standard library modules. No additional pip packages are required for core functionality.

### Python Dependencies

The project uses only **Python 3 standard library modules**:

- `os`, `sys`, `subprocess`, `shutil` - System operations
- `json`, `configparser` - Configuration handling
- `glob`, `re` - File pattern matching and regular expressions
- `datetime`, `enum`, `pathlib` - Utilities
- `urllib.request` - HTTP downloads
- `importlib.util` - Dynamic module loading

No `pip install` is required for the core functionality.

### Configuration

Edit `config.ini` to match your environment:

```ini
[main]
version=0.0.1
debian=trixie
board=pico-itx-k3

[user]
username=spacemit
password=spacemit

[language]
locale=en_US.UTF-8
timezone=America/New_York
```

**Main Parameters:**
- `version`: StratoDebRV version
- `debian`: Debian version to use (e.g., trixie, bookworm)
- `board`: Target board (must match a file in `boards/`)

## Usage

### Run the complete build

```bash
./StratoDeb
```

The script sequentially executes:
1. **Fetch**: Download sources and apply patches
2. **Configure**: Configure each component
3. **Build**: Compile each recipe
4. **Install**: Install to the final directory structure

### Target a specific step

The timestamp system allows resuming the build from a given step. Each step is executed only if it hasn't been successfully completed yet.

### Logging options

The logging level can be modified in the source code (`src/main.py`):

```python
Log.setLevel(LogLevel.DEBUG)  # DEBUG, INFO, WARNING, ERROR
```
## File Structure

### Configuration Files

#### `boards/<board>.json`

Defines the strata to build for a given board:

```json
{
    "name": "pico-itx-k3",
    "version": "0.0.1",
    "strata": [
        "Toolchain",
        "Firmware"
    ]
}
```

#### `strata/<board>/<stratum>/stratum.json`

Stratum-specific configuration:

**Toolchain Example:**
```json
{
    "arch": "riscv64-unknown-linux-gnu",
    "version": "latest",
    "cflags": [
        "-mcpu=spacemit-x100",
        "-march=rv64gc_zba_zbb_zbc_zbs",
        "-mabi=lp64d",
        "-O2"
    ],
    "ccache": true,
    "watch": {
        "url": "https://github.com/spacemit-com/toolchain/releases",
        "regex_version": "v(\\d+\\.\\d+\\.\\d+)",
        "url_template": "https://github.com/spacemit-com/toolchain/releases/download/v{version}/spacemit-toolchain-linux-glibc-x86_64-v{version}.tar.xz"
    }
}
```

#### `recipes/<board>/<recipe>/recipe.json`

Recipe configuration:

```json
{
    "name": "OpenSBI",
    "url": "https://github.com/spacemit-com/opensbi.git",
    "rev": "k3-br-v1.0.y",
    "platform": "generic",
    "defconfig": "k3_defconfig"
}
```

**Available Fields:**
- `name`: Recipe name (required)
- `url`: Git repository URL (required)
- `rev`: Revision/branch/tag (required)
- `files`: File mappings to copy (optional)
- Any additional field is accessible via `recipe.config`

### Custom Recipes

Create a `<RecipeName>.py` file in the recipe directory:

```python
from src.Recipe import Recipe
from src.system.Stamp import Step

class OpenSBI(Recipe):
    def __init__(self, name: str, context: str, root: str, stratum):
        super().__init__(name, context, root, stratum)
        self.__platform = self.config["platform"]
        self.__defconfig = self.config["defconfig"]

    def build(self) -> bool:
        if not self.isDone(Step.BUILD):
            toolchain = self.stratum.board["Toolchain"]
            # Custom build logic
            if self.runner.run([...], self.buildPath, {...}):
                self.done(Step.BUILD)
            else:
                return False
        return True
```

The methods `fetch()`, `configure()`, `build()`, `install()` can be overridden.

## Available Strata

### Toolchain

Manages the RISC-V cross-compilation toolchain:
- Automatic download from GitHub releases
- Extraction and installation to `build/toolchains/`
- ccache support to speed up builds
- Automatic latest version resolution (`latest` mode)

**Properties available in recipes:**
- `toolchain.compiler`: Path to compiler (e.g., `riscv64-unknown-linux-gnu-gcc`)
- `toolchain.crosscompile`: Cross-compilation prefix (e.g., `riscv64-unknown-linux-gnu-`)
- `toolchain.cflags`: Compiler flags
- `toolchain.path`: Toolchain installation path

### Firmware

Dedicated stratum for firmware (OpenSBI, U-Boot, etc.)
- Firmware build for target board
- Configuration via defconfigs
- Integration with toolchain

## Supported Boards

| Board | Architecture | Status |
|-------|-------------|--------|
| pico-itx-k3 | RISC-V (Spacemit X100) | :white_check_mark: Supported |

### Adding a New Board

1. Create a file in `boards/<new-board>.json`
2. Create the directory `strata/<new-board>/` with stratum configurations
3. Create the directory `recipes/<new-board>/` with necessary recipes
4. Update `config.ini` to point to the new board

## Available Recipes

### pico-itx-k3

| Recipe | Description | Custom Recipe |
|--------|-------------|---------------|
| opensbi | OpenSBI firmware for pico-itx-k3 | :white_check_mark: Yes |
| uboot | U-Boot bootloader | :x: No (uses default Recipe) |
| linux | Linux kernel | :x: No (uses default Recipe) |

## Main Classes and Methods

### `Recipe` Class

Base class for all recipes.

**Properties:**
- `recipe.name`: Recipe name
- `recipe.root`: StratoDebRV root directory
- `recipe.board`: Current Board object
- `recipe.sourcePath`: Path to downloaded sources
- `recipe.buildPath`: Path to build directory
- `recipe.recipePath`: Path to recipe definition
- `recipe.config`: Configuration loaded from recipe.json
- `recipe.runner`: Runner instance for command execution
- `recipe.log`: Log instance for logging

**Methods:**
- `recipe.fetch()`: Download sources and apply patches
- `recipe.configure()`: Configure the recipe
- `recipe.build()`: Compile the recipe
- `recipe.install()`: Install the recipe
- `recipe.isDone(step)`: Check if a step is already completed
- `recipe.done(step)`: Mark a step as completed

**Available Steps (Step enum):**
- `Step.FETCH`
- `Step.CONFIGURE`
- `Step.BUILD`
- `Step.INSTALL`

### `Stratum` Class

Base class for strata.

**Methods:**
- `stratum.fetch()`: Download all recipes
- `stratum.configure()`: Configure all recipes
- `stratum.build()`: Compile all recipes
- `stratum.install()`: Install all recipes

### Utilities

- `Runner`: Execute shell commands with environment management
- `Git`: Git operations (clone, checkout, apply patch)
- `Downloader`: File downloads
- `Archiver`: Archive extraction
- `Fs`: Filesystem operations
- `Stamp`: Step timestamp management
- `Log`: Logging with verbosity levels

## Customization

### Creating a New Stratum

1. Create a class inheriting from `Stratum` in `src/strata/`

```python
from src.strata.Stratum import Stratum

class MyNewStratum(Stratum):
    def __init__(self, root: str, board: str):
        super().__init__("MyNewStratum", root, board)
        # Custom initialization
```

2. Create the configuration in `strata/<board>/MyNewStratum/stratum.json`

3. Add the stratum to `boards/<board>.json`

### Creating a New Custom Recipe

1. Create the directory `recipes/<board>/<recipe-name>/`
2. Create `recipe.json` with the configuration
3. Create `<RecipeName>.py` with the custom class

## Troubleshooting

### Start Fresh

```bash
# Delete build directory
rm -rf build/

# Restart the build
./StratoDeb
```

### Force Rebuild of a Recipe

Delete timestamp files in `build/<board>/stamps/` or the recipe's build directory.

## License

This project is licensed under the **GPL-2.0 License**. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome!

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


*StratoDebRV - Stratified Debian for RISC-V*
*Version 0.0.1*

*Inspired by [debian-image-builder](https://github.com/pyavitz/debian-image-builder)*
