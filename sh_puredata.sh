#!/bin/sh

sleep 5

/usr/bin/pd -verbose -nogui -alsa -open /home/patch/plantoidz-pi/plantoid3.pd  > /home/patch/plantoidz-pi/logs/plantoid.log 2>&1



