#!/bin/sh

DIR="$1"
if [ -z "$DIR" ]
  then
    echo "Must supply full local path to directory to browse."
    exit 1
fi

docker kill weavegrid-hw:dev
docker build -t weavegrid-hw:dev .
docker run -p 5000:5000 --mount type=bind,source=$DIR,target=/root_dir --rm weavegrid-hw:dev