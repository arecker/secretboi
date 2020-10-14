#!/usr/bin/env bash

set -e

# PLATFORMS="linux/386,linux/amd64,linux/arm/v6,linux/arm/v7,linux/arm64"
PLATFORMS="linux/386,linux/amd64,linux/arm/v7"

docker_build() {
    docker buildx build \
	   --platform "${PLATFORMS}" \
	   --output "type=image,push=true" \
	   --tag "arecker/${1}:latest" \
	   --file "Dockerfile" .
}

docker_build "secretboi"
