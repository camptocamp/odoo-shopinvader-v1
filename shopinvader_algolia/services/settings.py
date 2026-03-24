# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class ExportSettingsService(Component):
    _inherit = "shopinvader.settings.service"

    def _get_search_engine_schema(self):
        schema = super()._get_search_engine_schema()
        schema["application_id"] = {
            "type": "string",
            "required": False,
            "nullable": True,
        }
        schema["api_key"] = {
            "type": "string",
            "required": False,
            "nullable": True,
        }
        return schema

    def _get_search_engine(self):
        res = super()._get_search_engine()
        if not res:
            return res
        se_backend = self.shopinvader_backend.se_backend_id
        if se_backend and se_backend.search_engine_name == "algolia":
            spec = se_backend.specific_backend
            res["application_id"] = spec.algolia_app_id or None
            # algolia_api_key_public is added by shopinvader_locomotive_algolia
            if "algolia_api_key_public" in spec._fields:
                res["api_key"] = spec.algolia_api_key_public or None
            else:
                res["api_key"] = None
        return res
