# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_test_helper import FakeModelLoader

from odoo.addons.shopinvader.tests.common import CommonCase


class TestSearchEngineSettings(CommonCase):
    def setUp(self):
        super().setUp()
        self.loader = FakeModelLoader(self.env, self.__module__)
        self.loader.backup_registry()
        from odoo.addons.connector_search_engine.tests.models import SeBackendFake

        self.loader.update_registry((SeBackendFake,))
        self.se_backend = (
            self.env[SeBackendFake._name].create({"name": "Fake SE"}).se_backend_id
        )
        self.backend.se_backend_id = self.se_backend
        with self.work_on_services(
            partner=self.env.ref("shopinvader.partner_1")
        ) as work:
            self.settings_service = work.component(usage="settings")

    def tearDown(self):
        self.loader.restore_registry()
        super().tearDown()

    def test_search_engine_no_backend(self):
        """Returns None when no SE backend is configured."""
        self.backend.se_backend_id = False
        res = self.settings_service.dispatch("search_engine")
        self.assertIsNone(res["search_engine"])

    def test_search_engine_name(self):
        """Returns the search engine name."""
        res = self.settings_service.dispatch("search_engine")
        self.assertEqual(res["search_engine"]["name"], "FakeSE")

    def test_search_engine_indices_empty(self):
        """Indices are empty when no se.index records exist."""
        res = self.settings_service.dispatch("search_engine")
        self.assertEqual(res["search_engine"]["indices"], [])

    def test_search_engine_indices(self):
        """Indices are built from se.index records."""
        variant_model = self.env["ir.model"]._get("shopinvader.variant")
        categ_model = self.env["ir.model"]._get("shopinvader.category")
        lang_en = self.backend.lang_ids[:1]
        self.env["se.index"].create(
            {
                "name": f"fake-product_{lang_en.code}",
                "backend_id": self.se_backend.id,
                "model_id": variant_model.id,
                "lang_id": lang_en.id,
                "exporter_id": self.env.ref(
                    "shopinvader.ir_exp_shopinvader_variant"
                ).id,
            }
        )
        self.env["se.index"].create(
            {
                "name": f"fake-category_{lang_en.code}",
                "backend_id": self.se_backend.id,
                "model_id": categ_model.id,
                "lang_id": lang_en.id,
                "exporter_id": self.env.ref(
                    "shopinvader.ir_exp_shopinvader_category"
                ).id,
            }
        )
        res = self.settings_service.dispatch("search_engine")
        indices = res["search_engine"]["indices"]
        names = {i["name"] for i in indices}
        self.assertEqual(names, {"products", "categories"})
        for idx in indices:
            # lang suffix stripped
            self.assertNotIn(lang_en.code, idx["index"])

    def test_all_includes_search_engine(self):
        """get_all response includes search_engine."""
        res = self.settings_service.dispatch("get_all")
        self.assertIn("search_engine", res)
