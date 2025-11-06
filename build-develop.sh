#!/bin/bash

git fetch origin
git checkout develop
git pull --rebase origin develop
docker buildx build --platform linux/amd64 -f Dockerfile -t odoo:latest --progress=plain .
docker image tag odoo:latest harbor.metaserv.vn/develop/odoo:latest
docker push harbor.metaserv.vn/develop/odoo:latest