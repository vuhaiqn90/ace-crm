# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models
from ...ace_accounting_vietnam_report.reports.partner_ledger_report_excel import convert_date_d_m_Y


class PartnerLedgerReportXlsx(models.AbstractModel):
    _inherit = 'report.ace_account.partner_ledger_report_excel'

    def generate_xlsx_report(self, workbook, data, objs):
        if objs.type != 'customer':
            return super(PartnerLedgerReportXlsx, self).generate_xlsx_report(workbook, data, objs)

        headerbig_format = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Times New Roman', 'font_size': 16,
            'text_wrap': True,
        })
        header_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Times New Roman', 'font_size': 10,
            'text_wrap': True,
        })
        line_format = workbook.add_format({
            'bold': 0,
            'border': 1,
            'align': 'left',
            'valign': 'vcenter',
            'font_name': 'Times New Roman', 'font_size': 10,
            'text_wrap': True,
        })
        line_center_format = workbook.add_format({
            'bold': 0,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Times New Roman', 'font_size': 10,
            'text_wrap': True,
        })
        money_format = workbook.add_format({
            'bold': 0,
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'font_name': 'Times New Roman', 'font_size': 10,
            'text_wrap': False,
            'num_format': '#,##0',
        })
        i = 7
        sheet = workbook.add_worksheet('Sheet1')
        sheet.hide_gridlines(2)
        # sheet.set_row(0, 35) #Tiêu đề
        sheet.set_column(0, 0, 25) # NVKD
        sheet.set_column(1, 1, 11) # Mã KH
        sheet.set_column(2, 2, 40) # Tên KH
        sheet.set_column(3, 3, 15) # Dư nợ đầu kỳ
        sheet.set_column(4, 4, 15) # Dư có đầu kỳ
        sheet.set_column(5, 5, 12) # Phát sinh nợ
        sheet.set_column(6, 6, 12) # Phát sinh có
        sheet.set_column(7, 7, 15) # Dư nợ cuối kỳ
        sheet.set_column(8, 8, 15) # Dư có cuối kỳ

        sheet.merge_range(0, 0, 0, 8, objs.company_id and objs.company_id.name or '',
                          workbook.add_format({
                        'bold': 1,
                        'border': 0,
                        'align': 'left',
                        'valign': 'vcenter',
                        'font_name': 'Times New Roman', 'font_size': 11,
                        'text_wrap': True,
                    }))
        sheet.merge_range(1, 0, 1, 8, objs.company_id and ', '.join([objs.company_id.street or '',
                                                         objs.company_id.city or '',
                                                         objs.company_id.country_id and
                                                         objs.company_id.country_id.name or '']) or '',
                          workbook.add_format({
                        'bold': 0,
                        'align': 'left',
                        'valign': 'vcenter',
                        'font_name': 'Times New Roman', 'font_size': 11,
                        'text_wrap': True,
                    }))
        sheet.merge_range(2, 0, 2, 8, 'MST: ' + (objs.company_id and objs.company_id.vat or ''),
                          workbook.add_format({
                        'bold': 0,
                        'align': 'left',
                        'valign': 'vcenter',
                        'font_name': 'Times New Roman', 'font_size': 10,
                    }))
        sheet.merge_range(3, 0, 3, 8, objs.name.upper(), headerbig_format)
        sheet.merge_range(4, 0, 4, 8, 'Tài khoản: ' + (objs.account_id and objs.account_id.display_name or
                                                       (objs.group_id and objs.group_id.display_name or '')),
                          workbook.add_format({
                              'bold': 1,
                              'align': 'center',
                              'valign': 'vcenter',
                              'font_name': 'Times New Roman', 'font_size': 10,
                              'text_wrap': True,
                          }))
        sheet.merge_range(5, 0, 5, 8, 'Từ ngày {} đến ngày {}'.format(convert_date_d_m_Y(objs.date_from),
                                                                      convert_date_d_m_Y(objs.date_to)),
                          workbook.add_format({
                              'italic': 1,
                              'align': 'center',
                              'valign': 'vcenter',
                              'font_name': 'Times New Roman', 'font_size': 10,
                              'text_wrap': True,
                          }))
        sheet.write(i, 0, 'Nhân viên KD', header_format)
        sheet.write(i, 1, 'Mã KH', header_format)
        sheet.write(i, 2, 'Tên KH', header_format)
        sheet.write(i, 3, 'Dư nợ đầu kỳ', header_format)
        sheet.write(i, 4, 'Dư có đầu kỳ', header_format)
        sheet.write(i, 5, 'Phát sinh nợ', header_format)
        sheet.write(i, 6, 'Phát sinh có', header_format)
        sheet.write(i, 7, 'Dư nợ cuối kỳ', header_format)
        sheet.write(i, 8, 'Dư có cuối kỳ', header_format)
        last_row = i + 1
        sheet.freeze_panes(last_row, 0)
        for row, line in enumerate(objs.line_ids):
            sheet.write(row+i+1, 0, line.user_id and line.user_id.name or '', line_format) # NHân viên KD
            sheet.write(row+i+1, 1, line.partner_code or '', line_center_format) # Mã KH
            sheet.write(row+i+1, 2, line.partner_name or '', line_format) # Tên KH
            sheet.write(row+i+1, 3, line.debit_start_balance or '', money_format) # Dư nợ đầu kỳ
            sheet.write(row+i+1, 4, line.credit_start_balance or '', money_format) # Dư có đầu kỳ
            sheet.write(row+i+1, 5, line.debit or '', money_format) # Phát sinh nợ
            sheet.write(row+i+1, 6, line.credit or '', money_format) # Phát sinh có
            sheet.write(row+i+1, 7, line.debit_end_balance or '', money_format) # Dư nợ cuối kỳ
            sheet.write(row+i+1, 8, line.credit_end_balance or '', money_format) # Dư có cuối kỳ
            last_row += 1
        sheet.merge_range(last_row, 0, last_row, 2, 'TỔNG CỘNG',
                          workbook.add_format({
                              'border': 1,
                              'bold': 1,
                              'align': 'center',
                              'valign': 'vcenter',
                              'font_name': 'Times New Roman', 'font_size': 10,
                              'text_wrap': True,
                          }))
        sheet.write(last_row, 3, sum(l.debit_start_balance for l in objs.line_ids),
                    workbook.add_format({
                        'border': 1,
                        'bold': 1,
                        'align': 'right',
                        'valign': 'vcenter',
                        'font_name': 'Times New Roman', 'font_size': 10,
                        'num_format': '#,##0',
                    }))
        sheet.write(last_row, 4, sum(l.credit_start_balance for l in objs.line_ids),
                    workbook.add_format({
                        'border': 1,
                        'bold': 1,
                        'align': 'right',
                        'valign': 'vcenter',
                        'font_name': 'Times New Roman', 'font_size': 10,
                        'num_format': '#,##0',
                    }))
        sheet.write(last_row, 5, sum(l.debit for l in objs.line_ids),
                    workbook.add_format({
                        'border': 1,
                        'bold': 1,
                        'align': 'right',
                        'valign': 'vcenter',
                        'font_name': 'Times New Roman', 'font_size': 10,
                        'num_format': '#,##0',
                    }))
        sheet.write(last_row, 6, sum(l.credit for l in objs.line_ids),
                    workbook.add_format({
                        'border': 1,
                        'bold': 1,
                        'align': 'right',
                        'valign': 'vcenter',
                        'font_name': 'Times New Roman', 'font_size': 10,
                        'num_format': '#,##0',
                    }))
        sheet.write(last_row, 7, sum(l.debit_end_balance for l in objs.line_ids),
                    workbook.add_format({
                        'border': 1,
                        'bold': 1,
                        'align': 'right',
                        'valign': 'vcenter',
                        'font_name': 'Times New Roman', 'font_size': 10,
                        'num_format': '#,##0',
                    }))
        sheet.write(last_row, 8, sum(l.credit_end_balance for l in objs.line_ids),
                    workbook.add_format({
                        'border': 1,
                        'bold': 1,
                        'align': 'right',
                        'valign': 'vcenter',
                        'font_name': 'Times New Roman', 'font_size': 10,
                        'num_format': '#,##0',
                    }))
        sheet.merge_range(last_row+3, 6, last_row+3, 8, 'Ngày {} tháng {} năm {}'.format(datetime.now().day,
                                                                                         datetime.now().month,
                                                                                         datetime.now().year),
                          workbook.add_format({
                              'italic': 1,
                              'align': 'center',
                              'valign': 'vcenter',
                              'font_name': 'Times New Roman', 'font_size': 10,
                          }))
        sheet.merge_range(last_row+4, 0, last_row+4, 2, 'Người lập biểu',
                          workbook.add_format({
                              'bold': 1,
                              'align': 'center',
                              'valign': 'vcenter',
                              'font_name': 'Times New Roman', 'font_size': 10,
                          }))
        sheet.merge_range(last_row+5, 0, last_row+5, 2, '(Ký, họ tên)',
                          workbook.add_format({
                              'italic': 1,
                              'align': 'center',
                              'valign': 'vcenter',
                              'font_name': 'Times New Roman', 'font_size': 10,
                          }))
        sheet.merge_range(last_row+12, 0, last_row+12, 2, objs.env.user.name,
                          workbook.add_format({
                              'bold': 1,
                              'italic': 1,
                              'align': 'center',
                              'valign': 'vcenter',
                              'font_name': 'Times New Roman', 'font_size': 10,
                          }))
        sheet.merge_range(last_row+4, 3, last_row+4, 5, 'Kế toán trưởng',
                          workbook.add_format({
                              'bold': 1,
                              'align': 'center',
                              'valign': 'vcenter',
                              'font_name': 'Times New Roman', 'font_size': 10,
                          }))
        sheet.merge_range(last_row+5, 3, last_row+5, 5, '(Ký, họ tên)',
                          workbook.add_format({
                              'italic': 1,
                              'align': 'center',
                              'valign': 'vcenter',
                              'font_name': 'Times New Roman', 'font_size': 10,
                          }))
        sheet.merge_range(last_row+12, 3, last_row+12, 5, '',
                          workbook.add_format({
                              'bold': 1,
                              'italic': 1,
                              'align': 'center',
                              'valign': 'vcenter',
                              'font_name': 'Times New Roman', 'font_size': 10,
                          }))
        sheet.merge_range(last_row+4, 6, last_row+4, 8, 'Giám đốc',
                          workbook.add_format({
                              'bold': 1,
                              'align': 'center',
                              'valign': 'vcenter',
                              'font_name': 'Times New Roman', 'font_size': 10,
                          }))
        sheet.merge_range(last_row+5, 6, last_row+5, 8, '(Ký, họ tên, đóng dấu)',
                          workbook.add_format({
                              'italic': 1,
                              'align': 'center',
                              'valign': 'vcenter',
                              'font_name': 'Times New Roman', 'font_size': 10,
                          }))
        sheet.merge_range(last_row+12, 6, last_row+12, 8, '',
                          workbook.add_format({
                              'bold': 1,
                              'italic': 1,
                              'align': 'center',
                              'valign': 'vcenter',
                              'font_name': 'Times New Roman', 'font_size': 10,
                          }))
