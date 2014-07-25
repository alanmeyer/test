#!/bin/sh
# Alan Meyer
# https://github.com/alanmeyer/test

GIT_PROJ=alanmeyer/test/master
GIT_SCRIPT=test

GIT_SCRIPT_GET=$GIT_SCRIPT"_get_and_run.sh"
GIT_SCRIPT_PYT=$GIT_SCRIPT".py"
GIT_SCRIPT_CFG=$GIT_SCRIPT".cfg"

rm -f $GIT_SCRIPT_GET $GIT_SCRIPT_PYT $GIT_SCRIPT_CFG
wget https://raw.github.com/$GIT_PROJ/$GIT_SCRIPT_GET
wget https://raw.github.com/$GIT_PROJ/$GIT_SCRIPT_PYT
chmod +x *.sh

python $GIT_SCRIPT_PYT
