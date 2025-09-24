FROM odoo:16
COPY config/requirements.txt /etc/odoo/requirements.txt
COPY config/odoo.conf /etc/odoo/odoo.conf
COPY addons /mnt/extra-addons
COPY customaddons /mnt/customaddons
USER root
RUN apt update && pip install --no-cache-dir -r /etc/odoo/requirements.txt
USER odoo
EXPOSE 8069 8072
ENV ODOO_RC=/etc/odoo/odoo.conf
CMD ["odoo"]