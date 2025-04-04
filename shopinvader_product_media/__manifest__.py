# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader Product Media",
    "summary": "Index storage media data into external search engine",
    "version": "14.0.1.1.0",
    "category": "e-commerce",
    "website": "https://github.com/camptocamp/odoo-shopinvader-v1",
    "author": "Akretion, Camptocamp",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": True,
    "depends": ["shopinvader", "storage_media_product"],
    "data": ["data/ir_product_export.xml"],
}
