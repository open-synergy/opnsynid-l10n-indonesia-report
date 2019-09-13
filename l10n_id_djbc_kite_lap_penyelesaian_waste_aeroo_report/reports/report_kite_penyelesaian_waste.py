# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from openerp.report import report_sxw
import pytz
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class Parser(report_sxw.rml_parse):

    # pylint: disable=locally-disabled, old-api7-method-defined
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.list_config = []
        self.localcontext.update({
            "time": time,
            "get_data": self._get_data,
            "get_date_start": self._get_date_start,
            "get_date_end": self._get_date_end,
            "convert_datetime_utc": self._convert_datetime_utc,
        })

    def set_context(self, objects, data, ids, report_type=None):
        self.form = data["form"]
        self.date_start = self.form["date_start"]
        self.date_end = self.form["date_end"]
        self.warehouse_ids = self.form["warehouse_ids"]
        _logger.info(str(self.warehouse_ids))
        return super(Parser, self).set_context(objects, data, ids, report_type)

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
            format_utc = convert_utc.strftime("%d-%m-%Y %H:%M:%S")

            return format_utc
        else:
            return "-"

    def _get_data(self):
        result = []
        obj_data = self.pool.get(
            "l10n_id.lap_kite_penyelesaian_waste")

        criteria = [
            ("tanggal", ">=", self.date_start),
            ("tanggal", "<=", self.date_end),
            ("gudang", "in", self.warehouse_ids)
        ]

        data_ids = obj_data.search(self.cr, self.uid, criteria)

        if data_ids:
            for no, data in enumerate(
                    obj_data.browse(self.cr, self.uid, data_ids)):
                res = {
                    "no": no + 1,
                    "nomor": data.nomor.name,
                    "tanggal": data.tanggal,
                    "kode_barang": data.kode_barang or "-",
                    "nama_barang": data.nama_barang,
                    "satuan": data.satuan.name,
                    "jumlah": data.jumlah,
                    "gudang": data.gudang.name,
                }
                result.append(res)
        return result
