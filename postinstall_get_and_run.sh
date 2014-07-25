#!/bin/sh
# Alan Meyer
# https://github.com/alanmeyer/test

GIT_PROJ=alanmeyer/test/master

rm -f postinstall_get_and_run.sh
rm -f ubuntu-14.04-postinstall.py
rm -f ubuntu-14.04-postinstall.cfg
wget https://raw.github.com/$GIT_PROJ/postinstall_get_and_run.sh
wget https://raw.github.com/$GIT_PROJ/ubuntu-14.04-postinstall.py

chmod +x *.sh

python ubuntu-14.04-postinstall.py
