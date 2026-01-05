#!/bin/sh

kubectl delete deployment config-deployment flow-data-deployment gateway-deployment weather-data-deployment

kubectl delete service config-service flow-data-service gateway-service weather-data-service

