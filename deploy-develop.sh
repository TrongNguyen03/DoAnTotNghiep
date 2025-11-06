#!/bin/bash

docker rm -f odoo
docker run --pull=always -d \
-p 0.0.0.0:8080:8069 \
-v /root/app/DoAnTotNghiep/odoo:/var/lib/odoo \
--restart unless-stopped \
--name odoo harbor.metaserv.vn/develop/odoo:latest