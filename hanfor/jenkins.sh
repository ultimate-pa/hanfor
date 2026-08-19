#!/bin/bash
if [ -d "venv" ]; then rm -r venv ; fi
mkdir venv
cd venv || exit 1
virtualenv -p python3 .
source ./bin/activate
cd ..
pip install -r requirements.txt
pip install -r requirements-dev.txt
if [ -f "config.py" ] ; then rm config.py ; fi
cp config.dist.py config.py
python run_tests.py
