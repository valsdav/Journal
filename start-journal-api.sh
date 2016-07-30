#!/bin/sh
docker stop mongodb
docker rm mongodb

docker run -tid  -p 27017:27017 \
    -v mongodb_data:/data/db \
    -v mongodb_config:/data/configdb \
    --name mongodb  mongo

#docker run -ti --rm --link mongodb:mongo \
#        -p 5000:5000 \
#        --name journal-server journal-api
