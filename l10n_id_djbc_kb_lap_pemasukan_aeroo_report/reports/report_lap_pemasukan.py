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
            "l10n_id.djbc_kb_lap_pemasukan")
        no = 1

        criteria = [
            ("tgl_penerimaan", ">=", self.date_start),
            ("tgl_penerimaan", "<=", self.date_end),
            ("warehouse_id", "in", self.warehouse_ids)
        ]

        data_ids = obj_data.search(self.cr, self.uid, criteria)

        if data_ids:
            for data_id in obj_data.browse(self.cr, self.uid, data_ids):
                res = {
                    "no": no,
                    "jenis_dokumen": data_id.jenis_dokumen,
                    "no_dokumen": data_id.no_dokumen,
                    "tgl_dokumen": data_id.tgl_dokumen,
                    "no_penerimaan": data_id.no_penerimaan,
                    "tgl_penerimaan": data_id.tgl_penerimaan,
                    "pengirim": data_id.pengirim,
                    "kode_barang": data_id.kode_barang,
                    "nama_barang": data_id.nama_barang,
                    "jumlah": data_id.jumlah,
                    "satuan": data_id.satuan,
                    "nilai": data_id.nilai
                }
                data.append(res)
                no += 1

        return data
