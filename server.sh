#!/bin/sh

# compile celestrium's coffeescript
./node_modules/.bin/coffee --compile -o src/www/scripts/celestrium/core/ src/www/scripts/celestrium/core-coffee/ &&\

# compile uap's coffeescript
./node_modules/.bin/coffee --compile -o src/www/scripts/uap src/www/scripts/uap-coffee/ &&\

# run server
# USAGE: python src/server.py <knowledgebase-uri> <num-axes> <concepts|assertions> <port>
python src/server.py data:matrices/conceptnet_en.gz 5,10,50,100 concepts src/www $PORT
