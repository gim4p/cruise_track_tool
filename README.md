# cruisetrackexport

QGIS Plugin that helps exporting navigation files for Transas Ecdis. The order of waypoints can simply be sorted in a preferred way.

Export to the following file formats:
- rtz
- rt3
- cvt-files.

Build by utilizing QGIS Plugin Builder.

Any tips, help, tests are welcome. :)

## Installation

### Ubuntu 

```bash
git clone https://github.com/gim4p/cruise_track_tool.git
ln -s cruise_track_tool/cruisetrack/ ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins
```

### Windows

#### with zip

Download link for zip file for QGIS:
[download](https://minhaskamal.github.io/DownGit/#/home?url=https://github.com/gim4p/cruise_track/tree/main/cruisetrack)
([DownGit](https://minhaskamal.github.io/DownGit/#/home) by [MinhasKamal](https://github.com/MinhasKamal))

Or just use the rezipped cruisetrack in folder cruise_track_tool-main for installation in 'install from ZIP' in the Plugin Installer.

#### with symlink

[see instructions here](https://www.howtogeek.com/howto/16226/complete-guide-to-symbolic-links-symlinks-on-windows-or-linux/)

```shell
git clone https://github.com/gim4p/cruise_track_tool.git
mklink /J "cruise_track_tool\cruisetrack" "QGIS\QGIS3\profiles\default\python\plugins"
```

## Examples

### Gui

![cruisetrack1](img/qgis-plugins-screenshot.png)


### rtz output file:

![cruisetrack2](img/rtz-file-screenshot.PNG)


