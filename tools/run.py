#!/usr/bin/env python2
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mini import app
app.run(debug=True, host="0.0.0.0", threaded=True)
