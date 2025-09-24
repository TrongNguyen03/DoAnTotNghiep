#!/bin/bash

git fetch origin
git checkout develop
git pull --rebase origin develop
docker buildx build --platform linux/amd64 -f Dockerfile -t odoo:latest .
docker image tag odoo:latest 103.20.144.134:80/develop/odoo:latest
docker push 103.20.144.134:80/develop/odoo:latest