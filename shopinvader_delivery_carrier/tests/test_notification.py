# Copyright 2019 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.queue_job.tests.common import trap_jobs
from odoo.addons.shopinvader.tests.common import CommonCase
from odoo.addons.shopinvader.tests.test_notification import NotificationCaseMixin


class NotificationPickingCase(CommonCase, NotificationCaseMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cart = cls.env.ref("shopinvader.sale_order_2")
        cls.cart.action_confirm()
        cls.picking = cls.cart.picking_ids

    def test_picking_notification1(self):
        """
        Check notification on outgoing picking.
        For this case, we should have a notification
        :return:
        """
        with self._catpure_notification(
            "stock_picking_outgoing_validated", notif_target=self.picking
        ):
            self.picking._action_done()

    def test_picking_notification2(self):
        """
        Check notification on outgoing picking.
        For this case, the picking is outgoing but is not related to a sale
        (with backend) so it shouldn't notify anything
        :return:
        """
        picking = self.picking.copy()
        # Remove the link with procurement/sales
        picking.move_ids.write({"sale_line_id": False})
        with trap_jobs() as trap:
            picking._action_done()
            trap.assert_jobs_count(0)

    def test_picking_notification3(self):
        """
        Check notification on outgoing picking.
        For this case, we change the picking type. So it shouldn't notify
        anything.
        :return:
        """
        self.picking.picking_type_id.write({"code": "internal"})
        with trap_jobs() as trap:
            self.picking._action_done()
            trap.assert_jobs_count(0)
