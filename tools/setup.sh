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
    GitPython==0.3.2.RC1 \
    iso8601 \
    pytz==2013d \
    pygments \
#    python-dateutil
# flask-mail flask-login python-dateutil requests
