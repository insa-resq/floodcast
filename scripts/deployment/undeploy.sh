#!/bin/sh

kubectl delete deployment config-service flow-data-service gateway-service weather-data-service

kubectl delete service config-service flow-data-service gateway-service weather-data-service

kubectl delete ingress gateway-ingress

