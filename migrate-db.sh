#!/bin/sh
source minimalenv/bin/activate
export FLASK_APP=application.py
flask db migrate # will create migration file for you unless there's an sqlite3 problem

# To make custom revision file (if alter table issue)
# flask db revision
# (since the revision is hand made no need to flask db migrate)
# Edit revision file, probably with batch mode.
# flask db upgrade




