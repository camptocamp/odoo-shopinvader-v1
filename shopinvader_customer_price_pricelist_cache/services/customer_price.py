# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class CustomerPriceService(Component):
    _inherit = "shopinvader.customer.price.service"

    def _to_json(self, records, **kw):
        pricelist = self.shopinvader_backend._get_cart_pricelist(self.partner)
        if pricelist.is_pricelist_cache_available:
            cached = self._get_cached_prices(records)
            return cached[0] if cached and kw.get("one") else cached
        # Falling back to the original implementation when pricelist cache
        # is inconsistent (once a day)
        return super()._to_json(records, **kw)

    def _get_cached_prices(self, records):
        pricelist = self.shopinvader_backend._get_cart_pricelist(self.partner)
        company = self.shopinvader_backend.company_id
        products = records.record_id
        price_caches = self.env[
            "product.pricelist.cache"
        ].get_cached_prices_for_pricelist(pricelist, products)
        res = []
        for cache in price_caches:
            res.append(
                {
                    "id": cache.product_id.id,
                    "price": {
                        self.invader_partner.role: cache.product_id._get_price(
                            price_unit=cache.price, pricelist=pricelist, company=company
                        )
                    },
                }
            )
        return res
