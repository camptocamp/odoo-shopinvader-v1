# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    shopinvader_state = fields.Selection(
        selection_add=[
            ("shipping_unprocessed", "No shipping yet"),
            ("shipping_partially", "Partially shipped"),
            ("shipping_done", "Fully shipped"),
        ]
    )

    def _compute_shopinvader_state_depends(self):
        return super()._compute_shopinvader_state_depends() + ("delivery_status",)

    def _get_shopinvader_state(self):
        if not self.delivery_status:
            return super()._get_shopinvader_state()
        # v18: the status value changed from v14 to v18
        # hence here we need a custom mapping to not migrate
        # existing data and above all to not break the shop UI
        # which relies on the old values.
        return {
            "pending": "shipping_unprocessed",
            "partial": "shipping_partially",
            "full": "shipping_done",
        }.get(self.delivery_status)
