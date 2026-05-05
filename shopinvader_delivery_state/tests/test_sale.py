# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader.tests.common import CommonCase


class TestSalesService(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.shop_sales = cls.env.ref("shopinvader.sale_order_2")
        cls.shop_sales += cls.shop_sales.copy()

    def _get_service(self):
        work_ctx = dict(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        )
        with self.work_on_services(**work_ctx) as work:
            return work.component(usage="sales")

    def test_state_default(self):
        service = self._get_service()
        res = service.search()
        states = sorted([x["state"] for x in res["data"]])
        self.assertEqual(states, ["pending"] * len(res["data"]))

    def test_state_unprocessed(self):
        self.shop_sales.action_confirm()
        service = self._get_service()
        res = service.search()
        states = sorted([x["state"] for x in res["data"]])
        self.assertEqual(states, ["shipping_unprocessed"] * len(res["data"]))

    def _deliver_picking_partially(self, order):
        """Validate only the first move of the order's picking."""
        picking = order.picking_ids
        first_move = picking.move_ids[0]
        first_move.quantity = first_move.product_uom_qty
        first_move.picked = True
        picking.with_context(skip_backorder=True).button_validate()

    def _deliver_picking_fully(self, order):
        """Validate all moves of the order's picking."""
        picking = order.picking_ids
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
            move.picked = True
        picking.button_validate()

    def test_state_partial(self):
        self.shop_sales.action_confirm()
        self._deliver_picking_partially(self.shop_sales[0])
        service = self._get_service()
        res = service.search()
        states = sorted([x["state"] for x in res["data"]])
        self.assertEqual(states, ["shipping_partially", "shipping_unprocessed"])

    def test_state_done(self):
        self.shop_sales.action_confirm()
        self._deliver_picking_fully(self.shop_sales[0])
        service = self._get_service()
        res = service.search()
        states = sorted([x["state"] for x in res["data"]])
        self.assertEqual(states, ["shipping_done", "shipping_unprocessed"])

    def test_state_done_not_shipped(self):
        self.shop_sales.action_confirm()
        service = self._get_service()
        res = service.search()
        states = sorted([x["state"] for x in res["data"]])
        self.assertEqual(states, ["shipping_unprocessed", "shipping_unprocessed"])
