#!/usr/bin/env bash
dropdb problembuildings
createdb -T template_postgis problembuildings
./manage.py syncdb --noinput
./manage.py LoadFootprints