#!/bin/sh
# Alan Meyer
# https://github.com/alanmeyer/test

GIT_PROJ=alanmeyer/test/master
GIT_SCRIPT=test

GIT_SCRIPT_GET=$GIT_SCRIPT"_get_and_run.sh"
GIT_SCRIPT_PYT=$GIT_SCRIPT".py"
GIT_SCRIPT_CFG=$GIT_SCRIPT".cfg"
GIT_SCRIPT_LOG=$GIT_SCRIPT".log"

rm -f $GIT_SCRIPT_GET $GIT_SCRIPT_PYT $GIT_SCRIPT_CFG $GIT_SCRIPT_LOG cleanup.sh
wget https://raw.github.com/$GIT_PROJ/$GIT_SCRIPT_GET
wget https://raw.github.com/$GIT_PROJ/$GIT_SCRIPT_PYT
wget https://raw.github.com/$GIT_PROJ/cleanup.sh
chmod +x *.sh

./cleanup.sh
python $GIT_SCRIPT_PYT
