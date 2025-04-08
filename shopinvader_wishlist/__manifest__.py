# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Wishlist",
    "summary": """
        Handle shop wishlist""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "website": "https://github.com/camptocamp/odoo-shopinvader-v1",
    "depends": ["shopinvader", "sale_wishlist"],
    "demo": ["demo/product_set.xml"],
    "data": ["views/product_set.xml", "wizard/sale_product_set_wiz.xml"],
    "installable": True,
}
