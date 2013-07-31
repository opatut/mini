#!/bin/bash
virtualenv -p python2 env
. env/bin/activate
pip install --pre --upgrade \
    flask \
    flask-sqlalchemy \
    flask-wtf \
    flask-markdown \
    flask-login \
    GitPython \
    iso8601 \
    pytz \
    pygments \
#    python-dateutil
# flask-mail flask-login python-dateutil requests
