/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { AppsMenu } from "@web/webclient/navbar/apps_menu";

patch(AppsMenu.prototype, {
    setup() {
        this._super(...arguments);

        // Gắn sự kiện khi click mở dropdown
        setTimeout(() => {
            const menuButton = document.querySelector('.o_app[data-menu-xmlid="customer_import_menu"]');
            if (menuButton) {
                menuButton.addEventListener('click', () => {
                    setTimeout(() => {
                        document.querySelectorAll(".dropdown-item.o_menu_item").forEach((el) => {
                            const text = el.textContent.trim();
                            if (text !== "Import Khách Hàng") {
                                el.style.display = "none";
                            }
                        });
                    }, 50); // Delay nhỏ sau khi menu mở
                });
            }
        }, 500); // Chờ tất cả render xong
    }
});
