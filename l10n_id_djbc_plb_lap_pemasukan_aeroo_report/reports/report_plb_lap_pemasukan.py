# -*- coding: utf-8 -*-
# Copyright 2018 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from openerp.report import report_sxw
import pytz
from datetime import datetime


class Parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.list_config = []
        self.localcontext.update({
            "time": time,
            "get_data": self._get_data,
            "get_pemilik_barang": self._get_pemilik_barang,
            "get_date_start": self._get_date_start,
            "get_date_end": self._get_date_end,
        })

    def set_context(self, objects, data, ids, report_type=None):
        self.form = data["form"]
        self.date_start = self.form["date_start"]
        self.date_end = self.form["date_end"]
        self.partner_id = self.form["partner_id"][0]
        self.pemilik_barang = self.form["partner_id"][1]
        return super(Parser, self).set_context(objects, data, ids, report_type)

    def _get_pemilik_barang(self):
        return self.pemilik_barang

    def _get_date_start(self):
        return self._convert_datetime_utc(self.date_start)

    def _get_date_end(self):
        return self._convert_datetime_utc(self.date_end)

    def _convert_datetime_utc(self, dt):
        if dt:
            obj_user = self.pool.get("res.users")
            user = obj_user.browse(self.cr, self.uid, [self.uid])[0]
            convert_dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
            if user.tz:
                tz = pytz.timezone(user.tz)
            else:
                tz = pytz.utc
            convert_utc = pytz.utc.localize(convert_dt).astimezone(tz)
            format_utc = convert_utc.strftime("%d %B %Y")

            return format_utc
        else:
            return "-"

    def _get_data(self):
        data = []
        obj_data = self.pool.get(
            "l10n_id.djbc_plb_lap_pemasukan")
        no = 1

        criteria = [
            ("tgl_penerimaan", ">=", self.date_start),
            ("tgl_penerimaan", "<=", self.date_end),
            ("pemilik_barang", "=", self.partner_id)
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
                    "nilai": data_id.nilai,
                    "pemilik_barang": data_id.pemilik_barang,
                    "kondisi_barang": "-"
                }
                data.append(res)
                no += 1

        return data
