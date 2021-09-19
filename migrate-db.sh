#!/bin/sh
source venv/bin/activate
export FLASK_APP=application.py
flask db migrate

# after this if everything looks in order, run:
# flask db upgrade


