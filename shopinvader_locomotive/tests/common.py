# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from contextlib import contextmanager

from odoo.addons.shopinvader.tests.common import CommonCase

_logger = logging.getLogger(__name__)

# pylint: disable=W7936
try:
    import requests_mock
except (OSError, ImportError) as err:
    _logger.debug(err)


class LocoCommonCase(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.base_url = cls.backend.location + "/locomotive/api/v3"
        cls.site = {
            "name": "My site",
            "handle": "shopinvader",
            "_id": "space_id",
        }


@contextmanager
def mock_site_api(base_url, site):
    with requests_mock.mock() as m:
        m.post(base_url + "/tokens.json", json={"token": "744cfcfb3cd3"})
        m.get(base_url + "/sites", json=[site])
        yield m.put(
            base_url + "/sites/{}".format(site["_id"]),
            json={"foo": "we_do_not_care"},
        )
