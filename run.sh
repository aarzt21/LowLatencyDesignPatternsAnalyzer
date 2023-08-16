#!/bin/bash

#run container after building image
docker run -it \
           --rm \
           -e DISPLAY=$DISPLAY \
           -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
           -v /:/host:rw \
           lldpa

