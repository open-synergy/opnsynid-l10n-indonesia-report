# -*- coding: utf-8 -*-
# Copyright 2018 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from openerp import api, fields, models
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class RestaurantEtax(models.TransientModel):
    _name = "l10n_id.restaurant_etax"

    date_start = fields.Date(
        string="Date Start",
        required=True,
        default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    date_end = fields.Date(
        string="Date End",
        required=True,
        default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    config_ids = fields.Many2many(
        string="Config(s)",
        comodel_name="pos.config",
        relation="rel_restaurant_etax_2_config",
        column1="wizard_id",
        column2="config_id",
        required=True,
    )
    output_format = fields.Selection(
        string="Output Format",
        required=True,
        selection=[("csv", "CSV"), ("ods", "ODS"), ("xls", "XLS")],
        default="csv",
    )

    @api.constrains("date_start", "date_end")
    def _check_date(self):
        strWarning = _("Date start must be greater than date end")
        if self.date_start and self.date_end:
            if self.date_start > self.date_end:
                raise UserError(strWarning)

    @api.multi
    def action_print_csv(self):
        datas = {}
        datas["form"] = self.read()[0]
        return {
            "type": "ir.actions.report.xml",
            "report_name": "aeroo_reportRestaurantEtaxCSV",
            "datas": datas,
        }

    @api.multi
    def action_print_ods(self):
        datas = {}
        datas["form"] = self.read()[0]
        return {
            "type": "ir.actions.report.xml",
            "report_name": "aeroo_reportRestaurantEtaxODS",
            "datas": datas,
        }

    @api.multi
    def action_print_xls(self):
        datas = {}
        datas["form"] = self.read()[0]
        return {
            "type": "ir.actions.report.xml",
            "report_name": "aeroo_reportRestaurantEtaxXLS",
            "datas": datas,
        }

    @api.multi
    def action_print(self):
        self.ensure_one()

        if self.output_format == "csv":
            result = self.action_print_csv()
        elif self.output_format == "ods":
            result = self.action_print_ods()
        elif self.output_format == "xls":
            result = self.action_print_xls()
        else:
            raise UserError(_("No Output Format Selected"))

        return result
