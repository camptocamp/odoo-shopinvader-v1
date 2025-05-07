# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.shopinvader.tests.common import InvoiceHelper

from .common import PortalModeCommonCase


class TestInvoiceService(PortalModeCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for sale in cls.shop_sales + cls.non_shop_sales:
            cls._invoice_sale(sale)
        cls.payment_method_manual_in = cls.env.ref(
            "account.account_payment_method_manual_in"
        )
        cls.payment_method_line_manual_in = cls.env[
            "account.payment.method.line"
        ].search([("payment_method_id", "=", cls.payment_method_manual_in.id)], limit=1)
        cls.all_invoices = (cls.shop_sales + cls.non_shop_sales).invoice_ids
        for inv in cls.all_invoices:
            InvoiceHelper._make_payment(inv, cls.payment_method_line_manual_in)

    @staticmethod
    def _invoice_sale(sale):
        for line in sale.order_line:
            line.write({"qty_delivered": line.product_uom_qty})
        return sale._create_invoices()

    def test_invoice_domain_default(self):
        service = self._get_service("invoice")
        domain = service._get_base_search_domain()
        invoices = self.env["account.move"].search(domain)
        self.assertEqual(sorted(invoices.ids), sorted(self.shop_sales.invoice_ids.ids))

    def test_invoice_domain_portal_mode(self):
        self.backend.sale_order_portal_mode = True
        service = self._get_service("invoice")
        domain = service._get_base_search_domain()
        invoices = self.env["account.move"].search(domain)
        self.assertEqual(sorted(invoices.ids), sorted(self.all_invoices.ids))
