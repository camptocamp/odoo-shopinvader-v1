# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2025 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.queue_job.tests.common import trap_jobs

from .common import StockCommonCase


class TestStockMove(StockCommonCase):
    """
    Tests for stock.move
    """

    def _assert_enqueued_job(self, trap):
        """Assert that the job function is enqueued."""
        desc = "Update shopinvader variants (stock update trigger)"
        trap.assert_enqueued_job(
            self.product.synchronize_all_binding_stock_level,
            properties=dict(description=desc),
            kwargs=dict(company_id=self.env.company),
        )

    def test_create_move(self):
        """create should not create a new job."""
        with trap_jobs() as trap:
            self._create_incoming_move()
            trap.assert_jobs_count(0)

    def test_action_cancel(self):
        """action_cancel should create a new job."""
        with trap_jobs() as trap:
            move = self._create_incoming_move()
            move._action_cancel()
            trap.assert_jobs_count(1)
            self._assert_enqueued_job(trap)

    def test_action_confirm(self):
        """action_confirm should create a new job."""
        with trap_jobs() as trap:
            move = self._create_incoming_move()
            move._action_confirm()
            trap.assert_jobs_count(1)
            self._assert_enqueued_job(trap)

    def test_action_done(self):
        """action_done should create a new job."""
        with trap_jobs() as trap:
            move = self._create_incoming_move()
            move._action_done()
            trap.assert_jobs_count(1)
            self._assert_enqueued_job(trap)

    def test_action_confirm_not_bound(self):
        """action_confirm for non bound products should not create a job."""
        with trap_jobs() as trap:
            self.product.shopinvader_bind_ids.unlink()
            move = self._create_incoming_move()
            move._action_confirm()
            trap.assert_jobs_count(0)

    def test_duplicated_action_done(self):
        """action_done should create a new job."""
        with trap_jobs() as trap:
            move = self._create_incoming_move()
            move._action_done()
            move = self._create_incoming_move()
            move._action_done()
            trap.assert_jobs_count(1)
            self._assert_enqueued_job(trap)
