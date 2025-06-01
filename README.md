# PackSearch

A Ulauncher extension for searching and installing packages from Arch Linux repositories and AUR using pacman, pamac, or yay.

## Features

- 🔍 **Fast package search** across multiple package managers
- 📦 **Multi-backend support**: pacman, pamac, and yay
- 🏷️ **Repository identification**: Shows which repo each package comes from ([core], [extra], [aur], etc.)
- ⚡ **Smart prioritization**: Exact matches and official repos appear first
- 📋 **Copy to clipboard**: Press Enter to copy the install command
- 🎯 **Intelligent search**: Searches official repos first, then AUR when using yay

## Installation

### Method 1: From Ulauncher Extensions (Recommended)

1. Open Ulauncher preferences
2. Go to "Extensions" tab
3. Click "Add extension"
4. Paste this repository URL: `https://github.com/albano-a/PackSearch`
5. Click "Add"

### Method 2: Manual Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/albano-a/PackSearch.git
   ```
2. Create a symlink in Ulauncher's extensions directory:
   ```bash
   ln -s /path/to/PackSearch ~/.local/share/ulauncher/extensions/com.github.albano-a.packsearch
   ```
3. Restart Ulauncher

## Usage

1. Open Ulauncher (default: `Ctrl+Space`)
2. Type the keyword `pack` followed by your search query
3. Browse the results showing package name, repository, and description
4. Press `Enter` on any result to copy the install command to clipboard
5. Paste the command in your terminal to install the package

### Examples

```
pack neovim          # Search for neovim
pack firefox         # Search for Firefox browser
pack discord         # Search for Discord
pack code            # Search for Visual Studio Code
```

## Supported Package Managers

The extension automatically detects and uses the available package manager:

| Package Manager | Install Command          | Repositories         |
| --------------- | ------------------------ | -------------------- |
| **yay**         | `yay -S package`         | Official repos + AUR |
| **pamac**       | `pamac install package`  | Official repos + AUR |
| **pacman**      | `sudo pacman -S package` | Official repos only  |

## Repository Types

Packages are labeled with their source repository:

- `[core]` - Essential Arch packages
- `[extra]` - Additional official packages
- `[community]` - Community-maintained packages
- `[multilib]` - 32-bit packages
- `[aur]` - Arch User Repository
- `[stable]` - Manjaro stable packages
- `[testing]` - Manjaro testing packages
- `[unstable]` - Manjaro unstable packages

## Configuration

The extension uses the default keyword `pack`. You can change this in Ulauncher preferences:

1. Open Ulauncher preferences
2. Go to "Extensions" tab
3. Find "PackSearch" and click the gear icon
4. Modify the keyword as desired

## Requirements

- **Ulauncher** (version 5.0+)
- **Python 3.6+**
- At least one of: `pacman`, `pamac`, or `yay`

### For Arch Linux users:

```bash
sudo pacman -S ulauncher
```

### For Manjaro users:

```bash
pamac install ulauncher
```

## Troubleshooting

### Extension not working

1. Check if Ulauncher is running the correct Python version
2. Verify that pacman/pamac/yay is installed and in PATH
3. Restart Ulauncher after installation

### No packages found

- Ensure your package manager is working: try `pacman -Ss test` in terminal
- Check your internet connection
- Verify the package name spelling

### Permission issues

- Make sure your user has sudo privileges for pacman
- For yay/pamac, ensure they're configured correctly

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork this repository
2. Clone your fork
3. Make changes
4. Test with your local Ulauncher installation
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0

- Initial release
- Support for pacman, pamac, and yay
- Repository identification
- Smart search prioritization
- Copy to clipboard functionality

## Author

**André Albano** - [GitHub Profile](https://github.com/albano-a)

## Acknowledgments

- Thanks to the Ulauncher team for the excellent launcher framework
- Inspired by the Arch Linux community and package management ecosystem
