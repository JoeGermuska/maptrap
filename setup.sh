#!/usr/bin/env bash
dropdb maptrap
createdb -T template_postgis maptrap
./manage.py syncdb --noinput
./manage.py LoadFootprints