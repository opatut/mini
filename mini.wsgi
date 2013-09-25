#!/usr/bin/env python2
import sys, os, datetime
from os.path import *

# Activate the virtual environment to load the library.
activate_this = join(dirname(abspath(__file__)), "env", "bin", "activate_this.py")
execfile(activate_this, dict(__file__ = activate_this))

sys.path.insert(0, dirname(abspath(__file__)))
from mini import app as application
