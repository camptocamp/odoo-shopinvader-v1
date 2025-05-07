# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Sale Packaging",
    "Summary": """
        Sell products by packaging.
    """,
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Camptocamp",
    "website": "https://github.com/camptocamp/odoo-shopinvader-v1",
    "depends": [
        "shopinvader",
        "sale_stock",
        "sell_only_by_packaging",
        "product_packaging_level_salable",
        "product_packaging_calculator_packaging_level",
    ],
    "data": [
        "data/ir_export_product.xml",
        "views/product_packaging.xml",
        "views/product_packaging_level.xml",
    ],
}
