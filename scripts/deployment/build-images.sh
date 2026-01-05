#!/bin/sh

REGISTRY_ADDRESS=172.0.0.39
REGISTRY_PORT=5000
IMAGE_NAME="floodcast-uv-image"

# launch registry service if not done already
if [ ! "$(docker ps -q -f name=registry)" ]; then
    docker run -d -p ${REGISTRY_PORT}:${REGISTRY_PORT} --restart=always --name registry registry:2
fi

docker build -t ${IMAGE_NAME} .

docker tag ${IMAGE_NAME}:latest ${REGISTRY_ADDRESS}:${REGISTRY_PORT}/${IMAGE_NAME}:latest

docker push ${REGISTRY_ADDRESS}:${REGISTRY_PORT}/${IMAGE_NAME}:latest

