#! /bin/bash -x

set -e

cd ..

docker-compose -f docker-compose.yml up -d

sleep 5

cd ./scripts/mongodb

. init.sh
