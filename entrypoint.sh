#!/bin/sh
set -e
#                     set the session tag           pass all the other args
exec python3 app.py "${HANFOR_TAG:?set HANFOR_TAG}" "$@"
