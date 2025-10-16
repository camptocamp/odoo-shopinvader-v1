# Copyright 2025 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase


class ProductCategoryCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.categ_data = [
            dict(
                name="Category 1",
                children=[
                    dict(name="Category 1.1", children=[dict(name="Category 1.1.1")]),
                    dict(name="Category 1.2"),
                ],
            ),
            dict(name="Category 2", children=[dict(name="Category 2.1")]),
            dict(
                name="Category 3",
                children=[
                    dict(
                        name="Category 3.1",
                        children=[
                            dict(name="Category 3.1.1"),
                            dict(
                                name="Category 3.1.2",
                                children=[dict(name="Category 3.1.2.1")],
                            ),
                        ],
                    )
                ],
            ),
        ]
        for categ in cls.categ_data:
            categ = cls._create_category(categ)
            setattr(cls, f"cat_{categ.name.lower().replace(' ', '_')}", categ)

    @classmethod
    def _create_category(cls, data, parent=None):
        categ = cls.env["product.category"].create(
            {"name": data["name"], "parent_id": parent.id if parent else False}
        )
        for child in data.get("children", []):
            cls._create_category(child, categ)
        return categ

    def _get_cat(self, name):
        return self.env["product.category"].search([("name", "=", name)], limit=1)

    # TODO: test search w/ translation
    def _search_cat(self, name, args=None):
        return self.env["product.category"].name_search(name, args=args)

    def test_display_name(self):
        cat = self._get_cat("Category 3.1.1")
        self.assertEqual(
            cat.complete_name, "Category 3 / Category 3.1 / Category 3.1.1"
        )
        self.assertEqual(cat.display_name, "Category 3 / Category 3.1 / Category 3.1.1")
        self.assertEqual(cat.name, "Category 3.1.1")
