Generate moving wallpapers
==========================

Generate moving wallpapers on Windows

Pull requests are welcome for reasonable features and other operating system support

1. [installation](./install.txt)

Download and view the video at the same time

Videos are stored at ~/Videos/VideoWallpapers

Usage:

    python movingwallpaper.py

Help:

    python movingwallpaper.py --help

### Autostart

- Create a shortcut at %USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
- Target should be the path to your pythonw.exe and then path to movingwallpaper.py

Example Shortcut Target (Properties):

    C:\Users\Bryce\AppData\Local\Microsoft\WindowsApps\pythonw3.exe C:\Users\Bryce\executables\vlc_wallpaper.py

## TODO

- auto generate shortcut link for starting at startup
