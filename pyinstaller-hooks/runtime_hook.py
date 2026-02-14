"""
PyInstaller runtime hook for FlatCAM.

Sets the current working directory to the executable's directory so that
relative paths (e.g. share/ icons) resolve correctly in frozen builds.
"""

import sys
import os

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
