#!/bin/sh
deluser test_user_1
deluser test_user_2
deluser test_user_3
delgroup test_user_1
delgroup test_user_2
delgroup test_user_3
delgroup test_group_1
delgroup test_group_2
delgroup test_group_3

rm -r /root/.bash*
rm -r /etc/skel/*
rm -r /etc/skel/.*
rm -r /media/images
rm    /root/scripts/*.sh
rm -r /root/bin
