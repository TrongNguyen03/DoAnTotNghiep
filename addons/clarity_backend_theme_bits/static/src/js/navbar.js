/** @odoo-module **/

import { NavBar } from '@web/webclient/navbar/navbar';
import { useService } from '@web/core/utils/hooks';
import { patch } from "@web/core/utils/patch";
import { useState, onMounted } from "@odoo/owl";

patch(NavBar.prototype, 'navbar_patch_menu_click_fix', {
    setup() {
        this._super();
        this.menuService = useService("menu");
        this.state = useState({
            isSidebarCollapsed: false,
            activeMenuId: null,
        });
        let isClickingMenu = false;
        onMounted(() => {
            const nav = document.querySelector('.primary-nav');
            if (nav) {
                nav.addEventListener('click', async (event) => {
                    const link = event.target.closest('a[data-menu].main_link, a[data-menu].child_menus');
                    if (!link) return;

                    event.preventDefault();

                    if (isClickingMenu) return;
                    isClickingMenu = true;

                    try {
                        const menuId = parseInt(link.dataset.menu);
                        await this.menuService.selectMenu(menuId, {
                            clearBreadcrumb: true,
                        });

                        this.state.activeMenuId = menuId;
                        const allLinks = nav.querySelectorAll('a[data-menu]');
                        allLinks.forEach((el) => {
                            el.classList.remove('active', 'active-parent');
                            const icon = el.querySelector('.fa-chevron-down');
                            if (icon) icon.classList.remove('rotated');
                        });

                        link.classList.add('active');
                        const icon = link.querySelector('.fa-chevron-down');
                        if (icon) icon.classList.add('rotated');
                        const parentLi = link.closest('li');
                        if (parentLi) {
                            const parentLink = parentLi.closest('ul')?.closest('li')?.querySelector('a[data-menu]');
                            if (parentLink) {
                                parentLink.classList.add('active-parent');
                                const parentIcon = parentLink.querySelector('.fa-chevron-down');
                                if (parentIcon) parentIcon.classList.add('rotated');
                            }
                        }

                    } catch (err) {
                        console.error("Lỗi khi mở menu:", err);
                    } finally {
                        isClickingMenu = false;
                    }
                });
            }
        });
    },
    toggleSidebar(ev) {
        document.body.classList.toggle('sidebar-collapsed');
        const navWrapper = document.querySelector('.nav-wrapper-bits');
        this.state.isSidebarCollapsed = !this.state.isSidebarCollapsed;

        const icon = document.querySelector('.sidebar-icon-toggle');
        if (icon) {
            icon.classList.toggle('fa-chevron-left', !this.state.isSidebarCollapsed);
            icon.classList.toggle('fa-chevron-right', this.state.isSidebarCollapsed);
        }

        if (navWrapper) {
            navWrapper.classList.toggle('toggle-show');
        }
    },
});