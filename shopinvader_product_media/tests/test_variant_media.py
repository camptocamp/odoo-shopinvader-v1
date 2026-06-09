# Copyright 2024 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.addons.shopinvader.tests.common import ProductCommonCase

from .common import Mixin


class ProductMediaCase(ProductCommonCase, Mixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.media1 = cls._create_storage_media("test-media.pdf")
        cls.media2 = cls._create_storage_media("test-media.txt")
        cls.media3 = cls._create_storage_media("test-media.csv")
        # Ensure the storage backend is public so media are exported
        cls.storage_backend = cls.media1.backend_id
        cls.storage_backend.is_public = True

    def test_availability(self):
        self.assertEqual(len(self.shopinvader_variant.variant_media_ids), 0)
        self.env["product.media.relation"].create(
            {"product_tmpl_id": self.template.id, "media_id": self.media1.id}
        )
        self.assertEqual(
            self.shopinvader_variant.variant_media_ids.media_id, self.media1
        )
        self.env["product.media.relation"].create(
            {"product_tmpl_id": self.template.id, "media_id": self.media2.id}
        )
        self.assertEqual(
            self.shopinvader_variant.variant_media_ids.media_id,
            self.media1 | self.media2,
        )
        self.env["product.media.relation"].create(
            {"product_tmpl_id": self.template.id, "media_id": self.media3.id}
        )
        self.assertEqual(
            self.shopinvader_variant.variant_media_ids.media_id,
            self.media1 | self.media2 | self.media3,
        )
        self.media1.active = False
        self.shopinvader_variant.invalidate_recordset()
        self.assertEqual(
            self.shopinvader_variant.variant_media_ids.media_id,
            self.media2 | self.media3,
        )

    def test_non_public_excluded(self):
        """Media on a non-public backend are excluded from export."""
        self.env["product.media.relation"].create(
            {"product_tmpl_id": self.template.id, "media_id": self.media1.id}
        )
        self.env["product.media.relation"].create(
            {"product_tmpl_id": self.template.id, "media_id": self.media2.id}
        )
        self.assertEqual(
            self.shopinvader_variant.variant_media_ids.media_id,
            self.media1 | self.media2,
        )
        # Mark the backend as non-public
        self.storage_backend.is_public = False
        self.shopinvader_variant.invalidate_recordset()
        self.assertEqual(len(self.shopinvader_variant.variant_media_ids), 0)

    def test_mixed_public_non_public(self):
        """Only media on public backends are included."""
        private_backend = self.storage_backend.copy(
            {"name": "Private Backend", "is_public": False}
        )
        # media3 goes on a private backend
        self.media3.file_id.backend_id = private_backend
        self.env["product.media.relation"].create(
            {"product_tmpl_id": self.template.id, "media_id": self.media1.id}
        )
        self.env["product.media.relation"].create(
            {"product_tmpl_id": self.template.id, "media_id": self.media3.id}
        )
        self.shopinvader_variant.invalidate_recordset()
        # Only media1 (public backend) should be included
        self.assertEqual(
            self.shopinvader_variant.variant_media_ids.media_id, self.media1
        )
