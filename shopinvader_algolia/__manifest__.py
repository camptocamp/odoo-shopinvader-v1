# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Shopinvader Algolia Connector",
    "version": "18.0.1.0.0",
    "author": "Akretion, Camptocamp",
    "website": "https://github.com/camptocamp/odoo-shopinvader-v1",
    "license": "AGPL-3",
    "category": "Generic Modules",
    "depends": ["shopinvader_search_engine", "connector_algolia"],
    "external_dependencies": {
        "python": [
            # use our own fork of connector_search_engine
            "odoo-addon-connector_search_engine @ "
            "git+https://github.com/camptocamp/search-engine-v1@18.0#subdirectory=connector_search_engine",
            "odoo-addon-connector_algolia @ "
            "git+https://github.com/camptocamp/search-engine-v1@18.0#subdirectory=connector_algolia",
        ]
    },
    "data": [
        "data/ir_export_product.xml",
        "views/shopinvader_variant_view.xml",
    ],
    "demo": ["demo/backend_demo.xml", "demo/product_demo.xml"],
    "installable": True,
    "application": True,
}
