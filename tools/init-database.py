#!/usr/bin/env python2
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from minigit import db
from minigit.util import generate_authorized_keys

db.drop_all()
db.create_all()
db.session.commit()

generate_authorized_keys()
