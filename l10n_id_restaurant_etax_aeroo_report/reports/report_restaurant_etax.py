# -*- coding: utf-8 -*-
# Copyright 2018 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from datetime import datetime

import pytz
from openerp.report import report_sxw
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.total = 0.00
        self.localcontext.update(
            {
                "time": time,
                "get_data": self._get_data,
            }
        )

    def set_context(self, objects, data, ids, report_type=None):
        self.form = data["form"]
        self.date_start = self.form["date_start"]
        self.date_end = self.form["date_end"]
        self.config_ids = self.form["config_ids"]
        return super(Parser, self).set_context(objects, data, ids, report_type)

    def _convert_datetime_to_utc(self, dt):
        obj_user = self.pool.get("res.users")
        user = obj_user.browse(self.cr, self.uid, [self.uid])[0]
        convert_dt = datetime.strptime(dt, DEFAULT_SERVER_DATETIME_FORMAT)

        if user.tz:
            tz = pytz.timezone(user.tz)
        else:
            tz = pytz.utc

        convert_tz = tz.localize(convert_dt)
        convert_utc = convert_tz.astimezone(pytz.utc)
        format_utc = datetime.strftime(convert_utc, DEFAULT_SERVER_DATETIME_FORMAT)

        return format_utc

    def _convert_datetime_from_utc(self, dt):
        obj_user = self.pool.get("res.users")
        user = obj_user.browse(self.cr, self.uid, [self.uid])[0]
        convert_dt = datetime.strptime(dt, DEFAULT_SERVER_DATETIME_FORMAT)

        if user.tz:
            tz = pytz.timezone(user.tz)
        else:
            tz = pytz.utc

        convert_utc = pytz.utc.localize(convert_dt).astimezone(tz)
        format_utc = convert_utc.strftime("%Y-%m-%d")

        return format_utc

    def _get_data(self):
        data = []
        obj_pos_order = self.pool.get("pos.order")
        date_start_utc = self._convert_datetime_to_utc(self.date_start + " 00:00:00")
        date_end_utc = self._convert_datetime_to_utc(self.date_end + " 23:59:59")

        criteria = [
            ("session_id.config_id", "in", self.config_ids),
            ("date_order", ">=", date_start_utc),
            ("date_order", "<=", date_end_utc),
            ("state", "in", ["paid", "done"]),
        ]

        data_ids = obj_pos_order.search(self.cr, self.uid, criteria)

        if data_ids:
            for data_id in obj_pos_order.browse(self.cr, self.uid, data_ids):
                tgl_transaksi = self._convert_datetime_from_utc(data_id.date_order)
                am_total = data_id.amount_total
                am_tax = data_id.amount_tax
                amount = am_total - am_tax

                res = {
                    "tgl_transaksi": tgl_transaksi,
                    "sales_no": data_id.pos_reference,
                    "amount": amount,
                    "service_charge": 0,
                    "receipt_no": data_id.pos_reference,
                }
                data.append(res)
        return data
