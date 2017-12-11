#!/bin/sh
set -e
name=${1:-my_project}
tag=${2:-latest}

cd $(dirname $0)
docker build -f Dockerfile.base -t $name.base .
docker build --build-arg IMAGE=$name.base -f Dockerfile.deps -t $name.deps .
docker run --rm $name.deps sh -c "find /pypkg -type f | sort | env GZIP=-n /bin/tar -T - -czf -" > req.tar.gz
docker build --build-arg IMAGE=$name.base -f Dockerfile -t $name:$tag .
