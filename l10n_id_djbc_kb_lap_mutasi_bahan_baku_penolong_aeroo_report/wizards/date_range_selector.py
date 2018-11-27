# -*- coding: utf-8 -*-
# Copyright 2018 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class KBLapMutasiBahanBakuWizard(models.TransientModel):
    _inherit = "l10n_id.kb_lap_mutasi_bahan_baku_wizard"

    @api.multi
    def action_print_xls(self):
        datas = {}
        datas['form'] = self.read()[0]
        context = {
            "date_start": self.date_start,
            "date_end": self.date_end,
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': "aeroo_reportLapMutasiBahanBakuXls",
            'datas': datas,
            'context': context,
        }

    @api.multi
    def action_print_ods(self):
        datas = {}
        datas['form'] = self.read()[0]
        context = {
            "date_start": self.date_start,
            "date_end": self.date_end,
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': "aeroo_reportLapMutasiBahanBakuOds",
            'datas': datas,
            'context': context,
        }
