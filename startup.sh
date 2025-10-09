#!/bin/sh


/usr/bin/pd -verbose -nogui -alsa -open /home/patch/plantoidz-pi/plantoid3.pd  > /home/patch/plantoidz-pi/logs/plantoid.log 2>&1 &

/usr/bin/python3 /home/patch/plantoidz-pi/listener5.py  > /home/patch/plantoidz-pi/logs/listen.log 2>&1 &

cd /home/patch/plantoidz-pi/plantoid-server/; yarn start  > /home/patch/plantoidz-pi/logs/server.log 2>&1 &



