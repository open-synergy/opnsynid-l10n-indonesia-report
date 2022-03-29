# -*- coding: utf-8 -*-
# Copyright 2018 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

import pytz
from openerp.report import report_sxw


class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update(
            {
                "get_data": self._get_data,
                "convert_datetime_utc": self._convert_datetime_utc,
            }
        )

    def set_context(self, objects, data, ids, report_type=None):
        self.form = data["form"]
        self.date_start = self.form["date_start"]
        self.date_end = self.form["date_end"]
        return super(Parser, self).set_context(objects, data, ids, report_type)

    def _get_data(self):
        result = []
        obj_lot = self.pool.get("stock.production.lot")
        obj_cum = self.pool.get("stock.stock_move_lot_cummulative")
        no = 0
        final_lot_ids = []

        lot_criteria = [
            ("product_id.djbc_plb_ok", "=", True),
        ]
        lot_ids = obj_lot.search(self.cr, self.uid, lot_criteria)

        index = 0
        for lot_id in lot_ids:
            criteria = [
                ("lot_id", "=", lot_id),
                ("date", "<=", self.date_end),
                ("date", ">=", self.date_start),
            ]
            cum_ids = obj_cum.search(self.cr, self.uid, criteria)

            if len(cum_ids) > 0:
                final_lot_ids.append(lot_id)
                index += 1
                continue

            criteria = [
                ("lot_id", "=", lot_id),
                ("date", "<=", self.date_end),
            ]
            cum_ids = obj_cum.search(
                self.cr, self.uid, criteria, order="date desc", limit=1
            )

            if len(cum_ids) == 0:
                index += 1
                continue
            cum = obj_cum.browse(self.cr, self.uid, cum_ids)[0]

            if cum.cummulative_qty == 0.0:
                index += 1
                continue

            index += 1
            final_lot_ids.append(lot_id)

        criteria = [("in_lot_id", "in", final_lot_ids)]
        index = 0

        # TODO: Refactor
        if len(final_lot_ids) == 0:
            tup_final_lot_ids = "(Null)"
        elif len(final_lot_ids) == 1:
            tup_final_lot_ids = "(%s)" % (final_lot_ids[0])
        else:
            tup_final_lot_ids = str(tuple(final_lot_ids))
        # pylint: disable=locally-disabled, sql-injection
        sql = """
        SELECT  a.document_type_id AS in_document_type_id,
                a.document_type_name AS in_document_type_name,
                a.document_id AS in_document_id,
                a.document_name AS in_document_name,
                a.document_date AS in_document_date,
                a.picking_date AS in_picking_date,
                a.product_code AS in_product_code,
                a.lot_id AS in_lot_id,
                a.lot_name AS in_lot_name,
                a.product_id AS in_product_id,
                a.product_name AS in_product_name,
                a.uom_id AS in_uom_id,
                a.uom_name AS in_uom_name,
                a.quantity AS in_quantity,
                a.cost AS in_cost,
                b.document_type_id AS out_document_type_id,
                b.document_type_name AS out_document_type_name,
                b.document_id AS out_document_id,
                b.document_name AS out_document_name,
                b.document_date AS out_document_date,
                b.picking_date AS out_picking_date,
                b.product_code AS out_product_code,
                b.lot_id AS out_lot_id,
                b.lot_name AS out_lot_name,
                b.product_id AS out_product_id,
                b.product_name AS out_product_name,
                b.uom_id AS out_uom_id,
                b.uom_name AS out_uom_name,
                b.quantity AS out_quantity,
                b.cost AS out_cost,
                (a.quantity -
                    (CASE
                        WHEN c.total_qty IS NOT NULL
                        THEN -1.0 * c.total_qty
                        ELSE 0.0
                    END)) as total_quantity,
                (a.cost -
                    (CASE
                        WHEN c.total_cost IS NOT NULL THEN c.total_cost
                        ELSE 0.0
                    END)) as total_cost
        FROM l10n_id_djbc_lap_posisi_barang_helper_in_common AS a
        LEFT JOIN (
            SELECT *
            FROM l10n_id_djbc_lap_posisi_barang_helper_out_common AS b1
            WHERE b1.picking_date <= '{}'
        ) AS b ON a.lot_id = b.lot_id
        LEFT JOIN (
            SELECT c1.lot_id,
                    SUM(c1.cost) AS total_cost,
                    SUM(c1.quantity) AS total_qty
            FROM l10n_id_djbc_lap_posisi_barang_helper_out_common AS c1
            WHERE c1.picking_date <= '{}'
            GROUP BY c1.lot_id
        ) AS c
            ON a.lot_id = c.lot_id
        WHERE a.lot_id IN {}
        """.format(
            self.date_end,
            self.date_end,
            tup_final_lot_ids,
        )
        # pylint: disable=locally-disabled, sql-injection
        self.cr.execute(sql)
        datas = self.cr.dictfetchall()
        if len(datas) > 0:
            for data in datas:
                show_bal = False
                if no == 0:
                    show_bal = True
                    no += 1
                else:
                    if datas[index]["in_lot_id"] != datas[index - 1]["in_lot_id"]:
                        show_bal = True
                        no += 1

                in_picking_date = (
                    data["in_picking_date"]
                    and self._convert_datetime_utc(data["in_picking_date"])
                    or ""
                )

                out_picking_date = (
                    data["out_picking_date"]
                    and self._convert_datetime_utc(data["out_picking_date"])
                    or ""
                )

                res = {
                    "no": show_bal and no,
                    "in_document_type": show_bal
                    and data["in_document_type_name"]
                    or "",
                    "in_document_number": show_bal and data["in_document_name"] or "",
                    "in_document_date": show_bal and data["in_document_date"] or "",
                    "in_picking_date": show_bal and in_picking_date,
                    "in_product_code": show_bal and data["in_product_code"] or "",
                    "in_lot_id": data["in_lot_id"],
                    "in_lot_name": show_bal and data["in_lot_name"] or "",
                    "in_product_name": show_bal and data["in_product_name"] or "",
                    "in_quantity": show_bal and data["in_quantity"] or "",
                    "in_uom_name": show_bal and data["in_uom_name"] or "",
                    "in_cost": show_bal and data["in_cost"] or "",
                    "out_document_type": data["out_document_type_name"] or "",
                    "out_document_number": data["out_document_name"] or "",
                    "out_document_date": data["out_document_date"] or "",
                    "out_picking_date": out_picking_date or "",
                    "out_product_code": data["out_product_code"] or "",
                    "out_lot_name": data["out_lot_name"] or "",
                    "out_product_name": data["out_product_name"] or "",
                    "out_quantity": data["out_quantity"]
                    and (data["out_quantity"] * -1.0)
                    or "",
                    "out_uom_name": data["out_uom_name"] or "",
                    "out_cost": data["out_cost"] or "",
                    "total_quantity": show_bal and data["total_quantity"] or 0.0,
                    "total_cost": show_bal and data["total_cost"] or 0.0,
                }
                result.append(res)
                index += 1

        return result

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
            format_utc = convert_utc.strftime("%Y-%m-%d %H:%M:%S")

            return format_utc
        else:
            return "-"
