# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class KitePemasukanBahanBakuWizard(models.TransientModel):
    _inherit = "l10n_id.kite_pemasukan_bahan_baku_wizard"

    @api.multi
    def action_print_xls(self):
        datas = {}
        datas["form"] = self.read()[0]
        return {
            "type": "ir.actions.report.xml",
            "report_name": "aeroo_reportKitePemasukanBahanBakuXls",
            "datas": datas,
        }

    @api.multi
    def action_print_ods(self):
        datas = {}
        datas["form"] = self.read()[0]
        return {
            "type": "ir.actions.report.xml",
            "report_name": "aeroo_reportKitePemasukanBahanBakuOds",
            "datas": datas,
        }
