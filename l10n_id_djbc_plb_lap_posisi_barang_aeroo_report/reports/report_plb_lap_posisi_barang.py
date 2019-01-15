# -*- coding: utf-8 -*-
# Copyright 2018 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.report import report_sxw
import logging
_logger = logging.getLogger(__name__)


class Parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            "get_data": self._get_data,
        })

    def set_context(self, objects, data, ids, report_type=None):
        self.form = data["form"]
        self.date_start = self.form["date_start"]
        self.date_end = self.form["date_end"]
        return super(Parser, self).set_context(objects, data, ids, report_type)

    def _get_data(self):
        result = []
        obj_data = self.pool.get(
            "l10n_id.djbc_lap_posisi_barang_helper_plb")
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
                ("date", ">=", self.date_start)
            ]
            cum_ids = obj_cum.search(
                self.cr, self.uid, criteria)

            if len(cum_ids) > 0:
                final_lot_ids.append(lot_id)
                index += 1
                continue

            criteria = [
                ("lot_id", "=", lot_id),
                ("date", "<=", self.date_end),
            ]
            cum_ids = obj_cum.search(
                self.cr, self.uid, criteria, order="date desc", limit=1)

            if len(cum_ids) == 0:
                index += 1
                continue
            cum = obj_cum.browse(self.cr, self.uid, cum_ids)[0]

            if cum.cummulative_qty == 0.0:
                index += 1
                continue

            index += 1
            final_lot_ids.append(lot_id)

        criteria = [
            ("in_lot_id", "in", final_lot_ids)
        ]
        index = 0
        data_ids = obj_data.search(self.cr, self.uid, criteria)
        datas = obj_data.browse(self.cr, self.uid, data_ids)
        if data_ids:
            for data in datas:
                show_bal = False
                if no == 0:
                    show_bal = True
                    no += 1
                else:
                    if datas[index].in_lot_id != datas[index-1].in_lot_id:
                        show_bal = True
                        no += 1

                res = {
                    "no": show_bal and no,
                    "in_document_type": show_bal and
                    data.in_document_type_id.name or "",
                    "in_document_number": show_bal and
                    data.in_document_id.name or "",
                    "in_document_date": show_bal and
                    data.in_document_date or "",
                    "in_picking_date": show_bal and
                    data.in_picking_date or "",
                    "in_product_code": show_bal and
                    data.in_product_code or "",
                    "in_lot_id": data.in_lot_id,
                    "in_lot_name": show_bal and
                    data.in_lot_id.name or "",
                    "in_product_name": show_bal and
                    data.in_product_id.name or "",
                    "in_quantity": show_bal and
                    data.in_quantity or "",
                    "in_uom_name": show_bal and
                    data.in_uom_id.name or "",
                    "in_cost": show_bal and
                    data.in_cost or "",
                    "out_document_type": data.out_document_type_id and
                    data.out_document_type_id.name or "",
                    "out_document_number": data.out_document_id and
                    data.out_document_id.name or "",
                    "out_document_date": data.out_document_date or "",
                    "out_picking_date": data.out_picking_date or "",
                    "out_product_code": data.out_product_code or "",
                    "out_lot_name": data.out_lot_id and
                    data.out_lot_id.name or "",
                    "out_product_name": data.out_product_id and
                    data.out_product_id.name or "",
                    "out_quantity": data.out_quantity and
                    (data.out_quantity * -1.0) or "",
                    "out_uom_name": data.out_uom_id and
                    data.out_uom_id.name or "",
                    "out_cost": data.out_cost or "",
                    "total_quantity": show_bal and
                    data.total_quantity or "",
                    "total_cost": show_bal and
                    data.total_cost or "",
                }
                result.append(res)
                index += 1

        return result
