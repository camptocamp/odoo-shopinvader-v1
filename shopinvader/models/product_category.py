# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression


class ProductCategory(models.Model):
    _inherit = "product.category"

    shopinvader_bind_ids = fields.One2many(
        "shopinvader.category",
        "record_id",
        string="Shopinvader Binding",
        context={"active_test": False},
    )
    filter_ids = fields.Many2many(comodel_name="product.filter", string="Filter")
    active = fields.Boolean(default=True)
    # V13 restore translate on category name...
    # This code is a transversal fix and should go into a dedicated addon...
    # The translate=True has been removed in
    # https://github.com/odoo/odoo/pull/36717 to workaround a bug introduced
    # in https://github.com/odoo/odoo/pull/16220 To avoid a bug into the seach
    # on category name, we must also restore the name_get method and
    # name_search
    # see also https://github.com/odoo/odoo/issues/22060#issuecomment-356567683
    _rec_name = None
    name = fields.Char(translate=True)

    def _compute_display_name(self):
        """Override to use the original record's complete_name field."""

        def get_names(cat):
            """Return the list [cat.name, cat.parent_id.name, ...]"""
            res = []
            while cat and cat.id:
                res.append(cat.name)
                cat = cat.parent_id
            return res

        for record in self:
            record.display_name = " / ".join(reversed(get_names(record)))

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        if name:
            category_names = [x.strip() for x in name.split(" / ")]
            parents = category_names[:]
            child = parents.pop()
            domain = [("name", operator, child)]
            if parents:
                names_ids = self.name_search(
                    " / ".join(parents),
                    args=args[:],  # safer recursion
                    operator="ilike",
                    limit=limit,
                )
                category_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    categories = self.search([("id", "not in", category_ids)])
                    domain = expression.OR(
                        [[("parent_id", "in", categories.ids)], domain]
                    )
                else:
                    domain = expression.AND(
                        [[("parent_id", "in", category_ids)], domain]
                    )
                # Optional fallback search for partial matches
                if operator not in expression.NEGATIVE_TERM_OPERATORS:
                    for i in range(1, len(category_names)):
                        domain = expression.OR(
                            [
                                [
                                    (
                                        "name",
                                        operator,
                                        " / ".join(category_names[-1 - i :]),
                                    )
                                ],
                                domain,
                            ]
                        )
            search_domain = expression.AND([domain, args])
        else:
            search_domain = args

        records = self.search_fetch(search_domain, ["display_name"], limit=limit)
        return [(record.id, record.display_name) for record in records.sudo()]
