#!/bin/sh
./node_modules/.bin/coffee --compile -o www/scripts/celestrium/core/ www/scripts/celestrium/core-coffee &&\
python server.py $PORT
