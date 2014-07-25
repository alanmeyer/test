#!/bin/sh
# Alan Meyer
# https://github.com/alanmeyer/test

GIT_PROJ=alanmeyer/test/master
GIT_SCRIPT=test

rm -f $GIT_SCRIPT_get_and_run.sh
rm -f $GIT_SCRIPT.py
rm -f $GIT_SCRIPT.cfg
wget https://raw.github.com/$GIT_PROJ/$GIT_SCRIPT_get_and_run.sh
wget https://raw.github.com/$GIT_PROJ/$GIT_SCRIPT.py

chmod +x *.sh

python $GIT_SCRIPT.py
