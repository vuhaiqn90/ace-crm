# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from odoo.addons import decimal_precision as dp


class ACEStockReport(models.TransientModel):
    _inherit = 'ace.stock.report'

    @api.multi
    def get_report(self):
        # wh = self.env['stock.location'].browse(12).get_warehouse()
        self.line_ids = False
        product_condition = main_product_condition = """"""
        category_condition = """"""
        wh_condition = child_wh_condition = sign = group_by = """"""
        if self.product_ids:
            product_condition = len(self.product_ids) == 1 and """ AND pp.id = {}""".format(self.product_ids.id) or \
                                """ AND pp.id IN {}""".format(tuple(self.product_ids.ids))
            main_product_condition = len(self.product_ids) == 1 and """ AND p.id = {}""".format(self.product_ids.id) or \
                                """ AND p.id IN {}""".format(tuple(self.product_ids.ids))
        if self.product_category_ids:
            category_ids = self.env['product.category'].search([('id', 'child_of', self.product_category_ids.ids)])
            category_condition= len(category_ids) == 1 and """ AND pc.id = {}""".format(category_ids.id) or \
                                """ AND pc.id IN {}""".format(tuple(category_ids.ids))
        if self.warehouse_id:
            wh_condition = """ AND get_warehouse(sq.location_id) = {}""".format(self.warehouse_id.id)
            child_wh_condition = """ 
                AND (get_warehouse(sm.location_id) = {} OR get_warehouse(sm.location_dest_id) = {})
               -- AND COALESCE(get_warehouse(sm.location_id), 0) != COALESCE(get_warehouse(sm.location_dest_id), 0)""".format(
                self.warehouse_id.id, self.warehouse_id.id)
            sign = """ * CASE WHEN spt.code = 'internal' AND get_warehouse(sm.location_dest_id) = {} THEN -1 ELSE 1 END""".format(self.warehouse_id.id)
            group_by = """, spt.code, sm.location_dest_id"""
        cr = self._cr
        # Create function get_warehouse
        cr.execute("""
            CREATE OR REPLACE FUNCTION get_warehouse(loc INT) RETURNS INT AS $$
            BEGIN
               RETURN (
                WITH RECURSIVE nodes(id,location_id,name) AS (
                    SELECT s1.id, s1.location_id, sw.id AS name
                    FROM stock_location s1
                        LEFT JOIN stock_warehouse sw ON sw.view_location_id = s1.id AND sw.active = TRUE
                    WHERE s1.id = loc
                    UNION
                    SELECT s2.id, s2.location_id, sw.id AS name
                    FROM stock_location s2
                        LEFT JOIN stock_warehouse sw ON sw.view_location_id = s2.id AND sw.active = TRUE
                    JOIN nodes s1 ON s2.id = s1.location_id
                )
                SELECT name FROM nodes ORDER BY name LIMIT 1);
            END; $$ LANGUAGE plpgsql;
        """)

        # Create function get_price_average
        cr.execute("""
            -- DROP FUNCTION get_price_average(integer,timestamp without time zone,integer);
            CREATE OR REPLACE FUNCTION get_price_average(product INT, dt VARCHAR, company INT) RETURNS FLOAT AS $$
            BEGIN
               RETURN (
                WITH RECURSIVE nodes(cost) AS (
                    SELECT cost
                    FROM product_price_history
                    WHERE datetime < CASE WHEN COALESCE(dt, '') = '' THEN NOW() ELSE dt::TIMESTAMP END
                        AND company_id = company
                        AND product_id = product
                    ORDER BY datetime DESC, id DESC
                    LIMIT 1
                )
                SELECT cost FROM nodes);
            END; $$ LANGUAGE plpgsql;	
        """)

        # Opening Stock
        sql = """
            DROP TABLE IF EXISTS opening_stock;
            CREATE TEMP TABLE opening_stock AS
            SELECT p.id AS product_id,
                   CASE WHEN ipm.value_text = 'fifo' AND ipv.value_text = 'real_time' THEN SUM(rl.quantity) 
                        ELSE COALESCE(B.qty_available, 0) END qty_available,
                   CASE WHEN ipm.value_text IN ('standard', 'average') 
                            THEN COALESCE(B.qty_available, 0) * get_price_average(p.id, '%s', %s) 
                        WHEN ipv.value_text = 'manual_periodic' THEN mn.value
                        ELSE SUM(rl.value) END AS value
            FROM product_product p
                JOIN product_template pt ON pt.id = p.product_tmpl_id
                JOIN product_category pc ON pc.id = pt.categ_id
                JOIN ir_property ipv ON ipv.name = 'property_valuation' AND SUBSTRING(ipv.res_id FROM POSITION(',' IN ipv.res_id)+1)::INT = pc.id
                JOIN ir_property ipm ON ipm.name = 'property_cost_method' AND SUBSTRING(ipm.res_id FROM POSITION(',' IN ipm.res_id)+1)::INT = pc.id
                JOIN ir_property ipa ON ipa.name = 'property_stock_valuation_account_id' AND SUBSTRING(ipa.res_id FROM POSITION(',' IN ipa.res_id)+1)::INT = pc.id
                LEFT JOIN (
                    SELECT aml.product_id, aml.account_id, (SUM(aml.debit) - SUM(aml.credit)) %s AS value, 
                            SUM(quantity) %s AS quantity, am.stock_move_id
                    FROM account_move_line AS aml, account_move am, stock_move sm, stock_picking_type spt
                    WHERE aml.move_id = am.id AND am.stock_move_id = sm.id AND sm.picking_type_id = spt.id AND aml.product_id IS NOT NULL 
                        AND aml.company_id = %s AND aml.date <= '%s' AND am.stock_move_id IS NOT NULL %s
                    GROUP BY aml.product_id, aml.account_id, am.stock_move_id%s
                ) rl ON rl.product_id = p.id AND rl.account_id = SUBSTRING(ipa.value_reference FROM POSITION(',' IN ipa.value_reference)+1)::INT
                LEFT JOIN (
                    SELECT sm.product_id, SUM(COALESCE(sm.value, 0.0)) AS value
                    FROM stock_location AS sl, stock_location AS sld, stock_move sm
                    WHERE sm.location_dest_id = sld.id AND sm.location_id = sl.id
                            AND sm.date <= '%s' AND  sm.state = 'done' %s 
                            AND (
                                ((sl.company_id IS NULL OR (sl.usage in ('inventory', 'production')  AND  sl.company_id = %s)) AND sld.company_id = %s)
                                OR (sl.company_id = %s AND (sld.company_id IS NULL OR (sld.usage in ('inventory', 'production') AND sld.company_id = %s)))) 
                            AND (sm.company_id IS NULL OR sm.company_id in (%s))
                    GROUP BY sm.product_id
                ) mn ON mn.product_id = p.id
                LEFT JOIN
                  (SELECT product_id,
                          SUM(total) - SUM(in_qty) + SUM(out_qty) AS qty_available
                   FROM
                     (SELECT sq.product_id,
                             SUM(sq.quantity) total,
                             0 AS in_qty,
                             0 AS out_qty
                      FROM product_product pp
                          JOIN stock_quant sq ON sq.product_id = pp.id
                          JOIN stock_location sl ON sl.id = sq.location_id
                      WHERE 1=1 AND get_warehouse(sq.location_id) IS NOT NULL %s %s
                      GROUP BY sq.product_id
                      UNION ALL 
                      SELECT sm.product_id,
                                       0 AS total,
                                       0 AS in_qty,
                                       SUM(sm.product_qty) out_qty
                      FROM product_product pp
                          JOIN stock_move sm ON sm.product_id = pp.id
                      WHERE sm.date::DATE > '%s'
                        AND sm.state = 'done'
                        AND get_warehouse(sm.location_id) IS NOT NULL 
                        AND get_warehouse(sm.location_dest_id) IS NULL
                        %s
                        %s
                      GROUP BY sm.product_id
                      UNION ALL 
                      SELECT sm.product_id,
                                       0 AS total,
                                       SUM(sm.product_qty) in_qty,
                                       0 AS out_qty
                      FROM product_product pp
                          JOIN stock_move sm ON sm.product_id = pp.id
                      WHERE sm.date::DATE > '%s'
                        AND sm.state = 'done'
                         AND get_warehouse(sm.location_dest_id) IS NOT NULL 
                         AND get_warehouse(sm.location_id) IS NULL
                        %s
                        %s
                      GROUP BY sm.product_id) A
                   GROUP BY product_id) B ON B.product_id = p.id
            WHERE 1=1 %s %s
            GROUP BY p.id, B.qty_available, ipm.value_text, ipv.value_text, mn.value;
        """ % (self.date_from, self.env.user.company_id.id, sign, sign, self.env.user.company_id.id, self.date_from, child_wh_condition, group_by,
               self.date_from, child_wh_condition, self.env.user.company_id.id, self.env.user.company_id.id, self.env.user.company_id.id,
               self.env.user.company_id.id, self.env.user.company_id.id, wh_condition, product_condition,
               self.date_from,
               self.warehouse_id and """AND get_warehouse(sm.location_id) = %s""" % self.warehouse_id.id or """""",
               product_condition,
               self.date_from,
               self.warehouse_id and """AND get_warehouse(sm.location_dest_id) = %s""" % self.warehouse_id.id or """""",
               product_condition, category_condition, main_product_condition)
        # print(sql)
        cr.execute(sql)
        # Closing Stock
        sql = """
            DROP TABLE IF EXISTS closing_stock;    
            CREATE TEMP TABLE closing_stock AS
            SELECT p.id AS product_id,
                   CASE WHEN ipm.value_text = 'fifo' AND ipv.value_text = 'real_time' THEN SUM(rl.quantity) 
                   ELSE COALESCE(B.qty_available, 0) END qty_available,
                   CASE WHEN ipm.value_text IN ('standard', 'average') THEN COALESCE(B.qty_available, 0) * get_price_average(p.id, '%s', %s) 
                        WHEN ipv.value_text = 'manual_periodic' THEN mn.value
                   ELSE SUM(rl.value) END AS value
            FROM product_product p
                JOIN product_template pt ON pt.id = p.product_tmpl_id
                JOIN product_category pc ON pc.id = pt.categ_id
                JOIN ir_property ipv ON ipv.name = 'property_valuation' AND SUBSTRING(ipv.res_id FROM POSITION(',' IN ipv.res_id)+1)::INT = pc.id
                JOIN ir_property ipm ON ipm.name = 'property_cost_method' AND SUBSTRING(ipm.res_id FROM POSITION(',' IN ipm.res_id)+1)::INT = pc.id
                JOIN ir_property ipa ON ipa.name = 'property_stock_valuation_account_id' AND SUBSTRING(ipa.res_id FROM POSITION(',' IN ipa.res_id)+1)::INT = pc.id
                LEFT JOIN (
                    SELECT aml.product_id, aml.account_id, (SUM(aml.debit) - SUM(aml.credit)) %s AS value, SUM(quantity) %s AS quantity, am.stock_move_id
                    FROM account_move_line AS aml, account_move am, stock_move sm, stock_picking_type spt
                    WHERE aml.move_id = am.id AND am.stock_move_id = sm.id AND sm.picking_type_id = spt.id AND aml.product_id IS NOT NULL 
                        AND aml.company_id = %s AND aml.date <= '%s' AND am.stock_move_id IS NOT NULL %s
                    GROUP BY aml.product_id, aml.account_id, am.stock_move_id%s
                ) rl ON rl.product_id = p.id AND rl.account_id = SUBSTRING(ipa.value_reference FROM POSITION(',' IN ipa.value_reference)+1)::INT
                LEFT JOIN (
                    SELECT sm.product_id, SUM(COALESCE(sm.value, 0.0)) AS value
                    FROM stock_location AS sl, stock_location AS sld, stock_move sm
                    WHERE sm.location_dest_id = sld.id AND sm.location_id = sl.id
                            AND sm.date <= '%s' AND  sm.state = 'done' %s 
                            AND (
                                ((sl.company_id IS NULL OR (sl.usage in ('inventory', 'production')  AND  sl.company_id = %s)) AND sld.company_id = %s)
                                OR (sl.company_id = %s AND (sld.company_id IS NULL OR (sld.usage in ('inventory', 'production') AND sld.company_id = %s)))) 
                            AND (sm.company_id IS NULL OR sm.company_id in (%s))
                    GROUP BY sm.product_id
                ) mn ON mn.product_id = p.id
                LEFT JOIN
                  (SELECT product_id,
                          SUM(total) - SUM(in_qty) + SUM(out_qty) AS qty_available
                   FROM
                     (SELECT sq.product_id,
                             SUM(sq.quantity) total,
                             0 AS in_qty,
                             0 AS out_qty
                      FROM product_product pp
                          JOIN stock_quant sq ON sq.product_id = pp.id
                          JOIN stock_location sl ON sl.id = sq.location_id
                      WHERE 1=1 AND get_warehouse(sq.location_id) IS NOT NULL %s %s
                      GROUP BY sq.product_id
                      UNION ALL 
                      SELECT sm.product_id,
                                       0 AS total,
                                       0 AS in_qty,
                                       SUM(sm.product_qty) out_qty
                      FROM product_product pp
                        JOIN stock_move sm ON sm.product_id = pp.id
                      WHERE sm.date::DATE >= '%s'
                        AND sm.state = 'done'
                        AND get_warehouse(sm.location_id) IS NOT NULL 
                        AND get_warehouse(sm.location_dest_id) IS NULL
                        %s
                        %s
                      GROUP BY sm.product_id
                      UNION ALL 
                      SELECT sm.product_id,
                                       0 AS total,
                                       sum(sm.product_qty) in_qty,
                                       0 AS out_qty
                      FROM product_product pp
                          JOIN stock_move sm ON sm.product_id = pp.id
                      WHERE sm.date::DATE >= '%s'
                        AND sm.state = 'done'
                         AND get_warehouse(sm.location_dest_id) IS NOT NULL 
                         AND get_warehouse(sm.location_id) IS NULL
                        %s
                        %s
                      GROUP BY sm.product_id) A
                   GROUP BY product_id) B ON B.product_id = p.id
            WHERE 1=1 %s %s
            GROUP BY p.id, B.qty_available, ipm.value_text, ipv.value_text, mn.value;
        """ % (self.date_to, self.env.user.company_id.id, sign, sign, self.env.user.company_id.id, self.date_to, child_wh_condition, group_by,
               self.date_to, child_wh_condition, self.env.user.company_id.id, self.env.user.company_id.id, self.env.user.company_id.id,
               self.env.user.company_id.id, self.env.user.company_id.id, wh_condition, product_condition,
               self.date_to,
               self.warehouse_id and """AND get_warehouse(sm.location_id) = %s""" % self.warehouse_id.id or """ """,
               product_condition,
               self.date_to,
               self.warehouse_id and """AND get_warehouse(sm.location_dest_id) = %s""" % self.warehouse_id.id or """ """,
               product_condition, category_condition, main_product_condition)
        # print(sql)
        cr.execute(sql)
        # Incoming Stock
        sql = """
            DROP TABLE IF EXISTS incoming_stock;    
            CREATE TEMP TABLE incoming_stock AS
            SELECT sm.product_id, SUM(sm.product_qty) in_qty, SUM(sm.value) AS value
            FROM product_product pp
                JOIN product_template pt ON pt.id = pp.product_tmpl_id
                JOIN product_category pc ON pc.id = pt.categ_id
                JOIN stock_move sm ON sm.product_id = pp.id
            WHERE sm.date::DATE <= '%s' AND sm.date::DATE >= '%s'
                AND sm.state = 'done' 
                AND get_warehouse(sm.location_dest_id) IS NOT NULL
                AND (get_warehouse(sm.location_id) IS NULL OR get_warehouse(sm.location_id) != get_warehouse(sm.location_dest_id)) 
                %s
                %s
                %s
            GROUP BY sm.product_id;
        """ % (self.date_to, self.date_from,
               self.warehouse_id and """AND get_warehouse(sm.location_dest_id) = %s""" % self.warehouse_id.id or """""",
               product_condition, category_condition)
        # print(sql)
        cr.execute(sql)
        # Outgoing Stock
        sql = """
            DROP TABLE IF EXISTS outgoing_stock;    
            CREATE TEMP TABLE outgoing_stock AS
            SELECT sm.product_id, SUM(sm.product_qty) out_qty, SUM(sm.value) AS value
            FROM product_product pp
                JOIN product_template pt ON pt.id = pp.product_tmpl_id
                JOIN product_category pc ON pc.id = pt.categ_id
                JOIN stock_move sm ON sm.product_id = pp.id
            WHERE sm.date::DATE <= '%s' AND sm.date::DATE >= '%s'
                AND sm.state = 'done'
                AND get_warehouse(sm.location_id) IS NOT NULL 
                AND (get_warehouse(sm.location_dest_id) IS NULL OR get_warehouse(sm.location_id) != get_warehouse(sm.location_dest_id))
                %s
                %s
                %s
            GROUP BY sm.product_id;
        """ % (self.date_to, self.date_from,
               self.warehouse_id and """AND get_warehouse(sm.location_id) = %s""" % self.warehouse_id.id or """""",
               product_condition, category_condition)
        # print(sql)
        cr.execute(sql)
        # Summary
        sql = """  
            INSERT INTO ace_stock_report_line 
                (create_uid, write_uid, create_date, write_date, report_id, product_id, product_category_id,
                 product_code, product_name, uom_id, opening_stock, opening_value, closing_stock, closing_value, 
                 qty_received, in_value, qty_delivery, out_value)
                SELECT %s, %s, now(), now(), %s, pp.id, pt.categ_id, pt.default_code, pt.name, pt.uom_id,
                        SUM(COALESCE(os.qty_available, 0)) AS opening_stock,
                        ROUND(SUM(COALESCE(os.value, 0))) AS opening_value,
                        SUM(COALESCE(cs.qty_available, 0)) AS closing_stock, 
                        ROUND(SUM(COALESCE(cs.value, 0))) AS closing_value, 
                        SUM(COALESCE(ins.in_qty, 0)) AS in_qty, 
                        SUM(COALESCE(ins.value, 0)) AS in_value, 
                        SUM(COALESCE(outs.out_qty, 0)) AS out_qty,
                        SUM(COALESCE(outs.value, 0)) AS out_value
                FROM product_product pp
                    JOIN product_template pt ON pt.id = pp.product_tmpl_id
                    JOIN product_category pc ON pc.id = pt.categ_id
                    LEFT JOIN opening_stock os ON os.product_id = pp.id
                    LEFT JOIN closing_stock cs ON cs.product_id = pp.id
                    LEFT JOIN incoming_stock ins ON ins.product_id = pp.id
                    LEFT JOIN outgoing_stock outs ON outs.product_id = pp.id
                WHERE 1=1 %s %s
                GROUP BY pp.id, pt.categ_id, pt.default_code, pt.name, pt.uom_id
                %s""" % (self._uid, self._uid, self.id, product_condition, category_condition,
                        self.available and """HAVING SUM(COALESCE(os.qty_available, 0)) != 0 
                                                        OR SUM(COALESCE(cs.qty_available, 0)) != 0
                                                        OR SUM(COALESCE(ins.in_qty, 0)) != 0 
                                                        OR SUM(COALESCE(outs.out_qty, 0)) != 0""" or """""")
        # print(sql)
        cr.execute(sql)

    @api.multi
    def export_excel(self):
        # datas = {'ids': self and self.ids or []}
        # datas['model'] = 'ace.stock.report'
        # datas['form'] = self.sudo().read()[0]
        # for field in datas['form'].keys():
        #     if isinstance(datas['form'][field], tuple):
        #         datas['form'][field] = datas['form'][field][0]
        # return {'type': 'ir.actions.report',
        #         'report_name': 'truongan_module.export_ace_stock_report',
        #         'report_type': 'xlsx',
        #         'data': datas,
        #         'name': 'Sale Order Report',
        #         'report_file': 'ace_stock_report',
        #         }
        return self.env.ref('ace_accounting_vietnam_report.ace_stock_report_py3o').with_context(
            opening_qty=self.line_ids and sum(line.opening_stock for line in self.line_ids) or 0,
            opening_value=self.line_ids and sum(line.opening_value for line in self.line_ids) or 0,
            in_qty=self.line_ids and sum(line.qty_received for line in self.line_ids) or 0,
            in_value=self.line_ids and sum(line.in_value for line in self.line_ids) or 0,
            out_qty=self.line_ids and sum(line.qty_delivery for line in self.line_ids) or 0,
            out_value=self.line_ids and sum(line.out_value for line in self.line_ids) or 0,
            closing_qty=self.line_ids and sum(line.closing_stock for line in self.line_ids) or 0,
            closing_value=self.line_ids and sum(line.closing_value for line in self.line_ids) or 0
        ).report_action(self)
