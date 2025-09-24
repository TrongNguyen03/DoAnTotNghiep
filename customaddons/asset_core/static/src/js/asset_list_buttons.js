/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";

patch(ListController.prototype, "asset_core.AssetListImport", {
    async onImportAsset() {
        this.env.services.action.doAction("asset_core.action_asset_import");
    },
});
