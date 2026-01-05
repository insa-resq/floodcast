#!/usr/bin/env bash
set -e

BUILD_IMAGES=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --build)
      BUILD_IMAGES=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

SCRIPTS_PATH="./scripts/deployment"

if [ "$BUILD_IMAGES" = true ]; then
  source ${SCRIPTS_PATH}/build-images.sh
fi
source ${SCRIPTS_PATH}/create-services.sh

SERVICE_PATH="./services"

kubectl apply -f ${SERVICE_PATH}/config-server/config_deployment.yaml
kubectl rollout status deployment/config-service

kubectl apply -f ${SERVICE_PATH}/flow-data/flow_data_deployment.yaml

kubectl apply -f ${SERVICE_PATH}/gateway/gateway_deployment.yaml

kubectl apply -f ${SERVICE_PATH}/weather-data/weather_data_deployment.yaml


