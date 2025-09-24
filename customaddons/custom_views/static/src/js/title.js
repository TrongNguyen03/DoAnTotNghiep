/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";

patch(WebClient.prototype, "custom_views.CustomPageTitle", {
    setup() {
        this._super();

        onMounted(async () => {
            const response = await fetch("/get/tab/title/");
            if (response.ok) {
                const newTitle = await response.text();
                this.title.setParts({ zopenerp: newTitle });
            }
        });
    },
});
