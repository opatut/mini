#!/bin/bash
virtualenv -p python2 env
. env/bin/activate
pip install --upgrade \
    -i http://c.pypi.python.org/simple/ \
    flask==0.9 \
    werkzeug==0.8.3 \
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
