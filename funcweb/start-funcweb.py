#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Start script for the funcweb TurboGears project.

This script is only needed during development for running from the project
directory. When the project is installed, easy_install will create a
proper start script.
"""

import os
import sys
from funcweb.commands import start, ConfigurationError

if __name__ == "__main__":
    if not os.path.exists("funcweb.egg-info"):
        argv = sys.argv
        sys.argv = ["setup", "egg_info"]
        import setup
        sys.argv = argv
    try:
        start()
    except ConfigurationError, exc:
        sys.stderr.write(str(exc))
        sys.exit(1)
