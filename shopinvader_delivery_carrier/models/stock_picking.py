# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _notify_backend(self, notification):
        """
        Send the notification to current recordset
        :param notification: str
        :return: bool
        """
        if notification == "stock_picking_outgoing_validated":
            self._notify_backend_outgoing(notification)
        return True

    def _notify_backend_outgoing(self, notification):
        """
        Notify current picking with outgoing type
        :param notification: str
        :return: bool
        """
        picking_outgoing = self.filtered(lambda p: p.picking_type_id.code == "outgoing")
        all_moves = picking_outgoing.mapped("move_ids")
        backends = picking_outgoing._get_related_backends()

        def filter_line(move, backend):
            line_backend = move.sale_line_id.order_id.shopinvader_backend_id
            return line_backend == backend

        for backend in backends:
            moves = all_moves.filtered(lambda ml, b=backend: filter_line(ml, b))
            pickings = moves.mapped("picking_id")
            for picking in pickings:
                backend._send_notification(notification, picking)
        return True

    def _get_related_backends(self):
        """
        Get backend related to current pickings
        :return: shopinvader.backend recordset
        """
        moves = self.mapped("move_ids")
        # Load backend from related sale order lines
        backends = moves.mapped("sale_line_id.order_id.shopinvader_backend_id")
        return backends

    def _action_done(self):
        """
        Inherit to update the invoice state if necessary
        :return:
        """
        result = super()._action_done()
        self._notify_backend("stock_picking_outgoing_validated")
        return result
