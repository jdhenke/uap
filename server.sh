#!/bin/sh

# compile coffeescript
./node_modules/.bin/coffee --compile -o src/www/scripts/celestrium/core/ src/www/scripts/celestrium/core-coffee/ &&\

# run server
# USAGE: python src/server.py <knowledgebase-uri> <num-axes> <concepts|assertions> <port>
python src/server.py conceptnet 100 concepts $PORT
