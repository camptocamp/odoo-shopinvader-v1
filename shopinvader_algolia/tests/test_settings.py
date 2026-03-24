# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase


class TestAlgoliaSettings(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.spec_backend = cls.env.ref("connector_algolia.se_algolia_demo")
        cls.spec_backend.write(
            {
                "algolia_app_id": "TESTAPPID",
            }
        )
        if "algolia_api_key_public" in cls.spec_backend._fields:
            cls.spec_backend.write({"algolia_api_key_public": "test_public_key"})

    def setUp(self):
        super().setUp()
        with self.work_on_services(
            partner=self.env.ref("shopinvader.partner_1")
        ) as work:
            self.settings_service = work.component(usage="settings")

    def test_search_engine_is_algolia(self):
        """Search engine name is algolia."""
        res = self.settings_service.dispatch("search_engine")
        self.assertEqual(res["search_engine"]["name"], "algolia")

    def test_algolia_application_id(self):
        """Algolia application_id is included in search engine config."""
        res = self.settings_service.dispatch("search_engine")
        self.assertEqual(res["search_engine"]["application_id"], "TESTAPPID")

    def test_algolia_api_key(self):
        """Algolia public api_key is included in search engine config."""
        res = self.settings_service.dispatch("search_engine")
        if "algolia_api_key_public" in self.spec_backend._fields:
            self.assertEqual(res["search_engine"]["api_key"], "test_public_key")
        else:
            self.assertIsNone(res["search_engine"]["api_key"])

    def test_algolia_indices(self):
        """Algolia indices are exposed."""
        res = self.settings_service.dispatch("search_engine")
        indices = res["search_engine"]["indices"]
        names = {i["name"] for i in indices}
        self.assertIn("products", names)
        self.assertIn("categories", names)

    def test_all_includes_algolia_config(self):
        """get_all includes Algolia-specific search engine config."""
        res = self.settings_service.dispatch("get_all")
        se = res["search_engine"]
        self.assertEqual(se["name"], "algolia")
        self.assertEqual(se["application_id"], "TESTAPPID")
