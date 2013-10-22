#!/bin/sh
(cd www/scripts/celestrium &&\
 npm install &&\
 ./node_modules/.bin/coffee --compile -o core/ core-coffee/*.coffee\
) && python server.py $PORT