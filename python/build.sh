#!/bin/bash

for VERSION in 2.4 2.6 2.7 3.2 3.3 3.4 3.5
do
    cd "$VERSION"
    image="sivel/python:$VERSION"
    docker build --no-cache -t "$image" .
    cd ..
done
