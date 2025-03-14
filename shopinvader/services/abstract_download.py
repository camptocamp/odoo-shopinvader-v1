# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import mimetypes

from odoo.exceptions import MissingError
from odoo.http import content_disposition, request
from odoo.tools.safe_eval import safe_eval, time

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import AbstractComponent


class AbstractDownload(AbstractComponent):
    """
    Class used to define behaviour to generate and download a document.
    You only have to inherit this AbstractComponent and implement the function
    _get_report_ref(...).

    """

    _name = "abstract.shopinvader.download"

    @restapi.method(
        routes=[(["/<int:_id>/download"], "GET")],
        output_param=restapi.BinaryData(required=True),
    )
    def download(self, _id, **params):
        """
        Get target file. This method is also callable by HTTP GET
        """
        params = params or {}
        target = self._get(_id)
        headers, content = self._get_binary_content(target, params=params)
        if not content:
            raise MissingError(self.env._("No content found for %(_id)s", _id=_id))
        response = request.make_response(content, headers)
        response.status_code = 200
        return response

    def _get_binary_content(self, target, params=None):
        """
        Generate the report for the given target
        :param target:
        :param params: dict
        :returns: (headers, content)
        """
        # Ensure the report is generated
        report_ref = self._get_report_ref(params=params)
        content, extension = self.env["ir.actions.report"]._render(
            report_ref, target.ids
        )
        report = self.env["ir.actions.report"]._get_report(report_ref)
        filename = self._get_binary_content_filename(
            target, report, extension, params=params
        )
        mimetype = mimetypes.guess_type(filename)
        if mimetype:
            mimetype = mimetype[0]
        headers = [
            ("Content-Type", mimetype),
            ("X-Content-Type-Options", "nosniff"),
            ("Content-Disposition", content_disposition(filename)),
            ("Content-Length", len(content)),
        ]
        return headers, content

    def _get_report_ref(self, params=None):
        """
        Return ref to lookup for the report,

        report_ref: can be one of
            - ir.actions.report id
            - ir.actions.report record
            - ir.model.data reference to ir.actions.report
            - ir.actions.report report_name
        """
        raise NotImplementedError()

    def _get_binary_content_filename(self, target, report, extension, params=None):
        """
        Build the filename
        :param target: recordset
        :param report: ir.actions.report.xml recordset
        :param format: str
        :param params: dict
        :return: str
        """
        if report.print_report_name and not len(target) > 1:
            report_name = safe_eval(
                report.print_report_name, {"object": target, "time": time}
            )
            return f"{report_name}.{extension}"
        return f"{report.name}.{extension}"
