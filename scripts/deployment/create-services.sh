#!/bin/sh
SERVICE_PATH="./services"

kubectl apply -f ${SERVICE_PATH}/config-server/config_service.yaml

kubectl apply -f ${SERVICE_PATH}/flow-data/flow_data_service.yaml

kubectl apply -f ${SERVICE_PATH}/gateway/gateway_service.yaml

kubectl apply -f ${SERVICE_PATH}/weather-data/weather_data_service.yaml

