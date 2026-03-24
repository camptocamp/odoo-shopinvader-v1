# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component


class ExportSettingsService(Component):
    _inherit = "shopinvader.settings.service"

    def _get_all_schema(self):
        schema = super()._get_all_schema()
        schema["search_engine"] = {
            "type": "dict",
            "required": True,
            "nullable": True,
            "schema": self._get_search_engine_schema(),
        }
        return schema

    def _get_all(self):
        res = super()._get_all()
        res["search_engine"] = self._get_search_engine()
        return res

    def _get_search_engine_schema(self):
        return {
            "name": {
                "type": "string",
                "required": True,
                "nullable": True,
            },
            "indices": {
                "type": "list",
                "required": True,
                "nullable": False,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "name": {
                            "type": "string",
                            "required": True,
                            "nullable": False,
                        },
                        "index": {
                            "type": "string",
                            "required": True,
                            "nullable": False,
                        },
                    },
                },
            },
        }

    def _get_search_engine(self):
        se_backend = self.shopinvader_backend.se_backend_id
        if not se_backend:
            return None
        return {
            "name": se_backend.search_engine_name or None,
            "indices": self._get_se_indices(se_backend),
        }

    def _get_se_indices(self, se_backend):
        indices = []
        seen = set()
        for index in se_backend.index_ids:
            model = index.model_id.model
            if model in seen:
                continue
            seen.add(model)
            usage = self._get_se_index_usage(model)
            if not usage:
                continue
            indices.append(
                {
                    "name": usage,
                    "index": self._get_index_name(index),
                }
            )
        return indices

    def _get_se_index_usage(self, model):
        return {
            "shopinvader.category": "categories",
            "shopinvader.variant": "products",
        }.get(model)

    def _get_index_name(self, index):
        """Strip language suffix to get the base index name."""
        lang_code = index.lang_id.code
        if lang_code:
            return index.name.replace(f"_{lang_code}", "")
        return index.name

    def _get_search_engine_detail_schema(self):
        return {
            "search_engine": {
                "type": "dict",
                "required": True,
                "nullable": True,
                "schema": self._get_search_engine_schema(),
            }
        }

    @restapi.method(
        [(["/search-engine"], "GET")],
        output_param=restapi.CerberusValidator("_get_search_engine_detail_schema"),
        auth="public_or_default",
    )
    def search_engine(self):
        return {"search_engine": self._get_search_engine()}
