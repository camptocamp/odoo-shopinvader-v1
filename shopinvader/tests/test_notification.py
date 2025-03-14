# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import CommonCase, NotificationCaseMixin
from .test_address import CommonAddressCase


class NotificationCartCase(CommonCase, NotificationCaseMixin):
    allow_inherited_tests_method = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cart = cls.env.ref("shopinvader.sale_order_2")

    def test_cart_notification(self):
        with self._catpure_notification("cart_confirmation", notif_target=self.cart):
            self.cart.action_confirm_cart()

        with self._catpure_notification("sale_confirmation", notif_target=self.cart):
            self.cart.action_confirm()

    def test_invoice_notification(self):
        self.cart.action_confirm_cart()
        self.cart.action_confirm()
        for line in self.cart.order_line:
            line.qty_delivered = line.product_uom_qty
        self.cart._create_invoices()

        with self._catpure_notification(
            "invoice_open", notif_target=self.cart.invoice_ids[0]
        ):
            self.cart.invoice_ids._post()


class NotificationCustomerCase(CommonAddressCase, NotificationCaseMixin):
    allow_inherited_tests_method = True

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        with self.work_on_services(
            partner=None, shopinvader_session=self.shopinvader_session
        ) as work:
            self.customer_service = work.component(usage="customer")

    def _create_customer(self, **kw):
        data = {
            "email": "new@customer.example.com",
            "external_id": "D5CdkqOEL",
            "name": "Purple",
            "street": "Rue du jardin",
            "zip": "43110",
            "city": "Aurec sur Loire",
            "phone": "0485485454",
            "country": {"id": self.env.ref("base.fr").id},
        }
        data.update(kw)
        res = self.customer_service.dispatch("create", params=data)["data"]
        return self.env["res.partner"].browse(res["id"])

    def test_new_customer_welcome(self):
        job_props = dict(
            description="Notify new_customer_welcome for res.partner,{partner_id}"
        )
        with self._catpure_notification(
            "new_customer_welcome",
            notif_target_model="res.partner",
            job_props=job_props,
        ):
            self._create_customer()

    def test_address_created(self):
        params = dict(self.address_params, name="John Doe")
        with self._catpure_notification("address_created", notif_target=self.partner):
            self.address_service.dispatch("create", params=params)
            address = self.env["res.partner"].search([("name", "=", "John Doe")])
            self.assertEqual(address.parent_id, self.partner)

    def test_address_updated(self):
        params = dict(email="joe@foo.com")
        with self._catpure_notification("address_updated", notif_target=self.partner):
            self.address_service.dispatch("update", self.address.id, params=params)
