# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase


class SaleCase(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product = cls.env["product.product"].create(
            {
                "name": "Product A",
                "is_storable": True,
            }
        )
        cls.sale = cls.env.ref("shopinvader.sale_order_2")
        cls.sale.order_line[0].product_id = product
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.stock_loc = cls.env.ref("stock.stock_location_stock")
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.wh_main = cls.env.ref("stock.warehouse0")
        cls.env["stock.quant"]._update_available_quantity(product, cls.stock_loc, 10)

        with cls.work_on_services(cls, partner=cls.partner) as work:
            cls.service = work.component(usage="sales")

    def _confirm_and_deliver_sale(self):
        self.sale.action_confirm()
        picking = self.sale.picking_ids
        picking.action_confirm()
        picking.action_assign()
        picking.move_line_ids._action_done()

    def test_read_sale(self):
        self.sale.action_confirm_cart()
        self._confirm_and_deliver_sale()
        res = self.service.get(self.sale.id)
        pick = self.sale.picking_ids[0]
        self.assertEqual(
            res["deliveries"][0],
            {"id": pick.id, "name": pick.name, "date": pick.scheduled_date},
        )

    def test_available_carriers(self):
        # Carriers are available on the backend
        all_carriers = self.env["delivery.carrier"].search(
            [
                "|",
                ("company_id", "=", False),
                ("company_id", "=", self.env.company.id),
            ]
        )
        carriers = self.env.ref("delivery.delivery_carrier") + self.env.ref(
            "delivery.free_delivery_carrier"
        )
        sale = self.sale
        self.assertEqual(sale.shopinvader_backend_id.carrier_ids, carriers)
        # Carriers available on SO are limited to the ones on the backend
        self.assertEqual(sale.shopinvader_available_carrier_ids, carriers)
        self.assertEqual(sale._available_carriers(), all_carriers)
        # No carrier on the backend
        sale.shopinvader_backend_id = False
        self.assertEqual(sale.shopinvader_available_carrier_ids, carriers.browse())

    def test_available_carriers_by_country(self):
        sale = self.sale
        all_carriers = self.env["delivery.carrier"].search([])
        be_carrier = sale.shopinvader_backend_id.carrier_ids[0]
        be_carrier.country_ids = self.env.ref("base.be")
        rest_of_carriers = all_carriers - be_carrier
        rest_of_carriers.country_ids = self.env.ref("base.de")
        sale.partner_shipping_id.country_id = self.env.ref("base.be")
        self.assertEqual(sale.shopinvader_available_carrier_ids, be_carrier)
        self.assertEqual(sale._available_carriers(), be_carrier)
