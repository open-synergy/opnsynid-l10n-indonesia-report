# -*- coding: utf-8 -*-
# Copyright 2018 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from openerp.report import report_sxw


class Parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.list_config = []
        self.localcontext.update({
            "time": time,
            "get_data": self._get_data,
        })

    def set_context(self, objects, data, ids, report_type=None):
        self.form = data["form"]
        self.date_start = self.form["date_start"]
        self.date_end = self.form["date_end"]
        self.warehouse_ids = self.form["warehouse_ids"]
        return super(Parser, self).set_context(objects, data, ids, report_type)

    def _get_data(self):
        data = []
        obj_data = self.pool.get(
            "l10n_id.djbc_kb_lap_mutasi_bahan_baku_penolong")
        no = 1

        criteria = [
            ("warehouse_id", "in", self.warehouse_ids)
        ]

        data_ids = obj_data.search(self.cr, self.uid, criteria)

        if data_ids:
            context = {
                "date_start": self.date_start,
                "date_end": self.date_end
            }
            for data_id in obj_data.browse(
                    self.cr, self.uid, data_ids, context):
                product_id = data_id.product_id
                product_name = product_id and product_id.name or "-"

                uom_id = data_id.uom_id
                uom_name = uom_id and uom_id.name or "-"

                res = {
                    "no": no,
                    "kode_barang": data_id.kode_barang,
                    "nama_barang": product_name,
                    "sat": uom_name,
                    "saldo_awal": data_id.saldo_awal,
                    "pemasukan": data_id.pemasukan,
                    "pengeluaran": data_id.pengeluaran,
                    "penyesuaian": data_id.penyesuaian,
                    "stock_opname": data_id.stock_opname,
                    "saldo_akhir": data_id.saldo_akhir,
                    "selisih": data_id.selisih,
                    "keterangan": data_id.keterangan
                }
                data.append(res)
                no += 1

        return data
