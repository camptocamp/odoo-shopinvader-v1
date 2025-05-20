# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools import mute_logger

from odoo.addons.connector_search_engine.tests.test_all import TestBindingIndexBaseFake
from odoo.addons.queue_job.tests.common import JobMixin


class StockCommonCase(TestBindingIndexBaseFake, JobMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,  # speed up tests
                queue_job__no_delay=False,  # we want the jobs
            )
        )
        ref = cls.env.ref
        cls.shopinvader_backend = ref("shopinvader.backend_1")
        cls.warehouse_1 = ref("stock.warehouse0")
        cls.loc_1 = cls.warehouse_1.lot_stock_id
        cls.warehouse_2 = cls.env["stock.warehouse"].create(
            {
                "name": "Warehouse 2",
                "code": "WH2",
                "lot_stock_id": ref("stock.stock_location_stock").id,
                "view_location_id": ref("stock.stock_location_stock").id,
            }
        )
        cls.loc_2 = cls.warehouse_2.lot_stock_id
        cls.product = cls.env["product.product"].create(
            {"name": "Stock prod 1", "is_storable": True}
        )
        with mute_logger("odoo.addons.queue_job.utils"):
            cls.shopinvader_backend.with_context(
                queue_job__no_delay=True
            ).bind_all_product()
        cls.index = cls.env["se.index"].create(
            {
                "name": "test-product-index",
                "backend_id": cls.backend_specific.se_backend_id.id,
                "exporter_id": ref("shopinvader.ir_exp_shopinvader_variant").id,
                "lang_id": ref("base.lang_en").id,
                "model_id": ref("shopinvader.model_shopinvader_variant").id,
            }
        )
        cls.shopinvader_backend.write(
            {
                "se_backend_id": cls.backend_specific.se_backend_id.id,
                "warehouse_ids": [(6, 0, cls.warehouse_1.ids)],
                "product_stock_field_id": ref(
                    "stock.field_product_product__qty_available"
                ).id,
            }
        )
        cls.loc_supplier = cls.env.ref("stock.stock_location_suppliers")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")

    def _add_stock_to_product(self, product, location, qty):
        """Set the stock quantity of the product.

        :param product: product.product recordset
        :param qty: float
        """
        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "location_id": location.id,
                "inventory_quantity_auto_apply": qty,
            }
        )

    def _create_incoming_move(self):
        location_dest = self.picking_type_in.default_location_dest_id
        return self.env["stock.move"].create(
            {
                "name": "Forced Move",
                "location_id": self.loc_supplier.id,
                "location_dest_id": location_dest.id,
                "product_id": self.product.id,
                "product_uom_qty": 2.0,
                "product_uom": self.product.uom_id.id,
                "picking_type_id": self.picking_type_in.id,
            }
        )
