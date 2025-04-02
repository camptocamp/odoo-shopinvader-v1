# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import NotificationCaseMixin
from odoo.addons.shopinvader.tests.test_address import CommonAddressCase


class NotificationCustomerCase(CommonAddressCase, NotificationCaseMixin):
    def setUp(self):
        super().setUp()
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

    def test_new_customer_welcome_not_validated(self):
        self.backend.update(
            dict(validate_customers=True, validate_customers_type="all")
        )
        with self._catpure_notification(
            "new_customer_welcome_not_validated",
            notif_target_model="res.partner",
        ):
            partner = self._create_customer(
                email="new@tovalidate.example.com",
                external_id="F5CdkqOEL",
                name="To Validate",
            )

        # now enable it
        invader_partner = partner._get_invader_partner(self.backend)
        with self._catpure_notification(
            "customer_validated",
            notif_target=partner,
        ):
            invader_partner._get_shopinvader_validate_wizard().action_apply()

    def test_address_created_not_validated(self):
        self.backend.update(
            dict(validate_customers=True, validate_customers_type="all")
        )
        params = dict(self.address_params, name="John Doe")
        with self._catpure_notification(
            "address_created_not_validated",
            # notification goes to the owner of the address
            notif_target=self.partner,
        ):
            self.address_service.dispatch("create", params=params)
        address = self.env["res.partner"].search([("name", "=", "John Doe")], limit=1)
        self.assertEqual(address.parent_id, self.partner)

        # now enable it
        wiz = address._get_shopinvader_validate_address_wizard()
        with self._catpure_notification(
            "address_validated",
            # notification goes to the owner of the address
            notif_target=self.partner,
        ):
            wiz.action_apply()
