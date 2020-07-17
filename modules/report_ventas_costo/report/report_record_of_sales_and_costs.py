# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base_it.utils import parse2str_dt
from odoo.addons.report_it.utils import get_excel_logo, resize_cells_widths
from xlsxwriter.workbook import Workbook
import base64
import collections

class ReportRecordOfSalesAndCosts(models.TransientModel):
	_name='report.record.of.sales.and.costs'

	period_ini = fields.Date(u'Fecha inicial',default=lambda self: fields.Date.context_today(self))
	period_end = fields.Date(u'Fecha Final',default=lambda self: fields.Date.context_today(self))

	def build_report_excel(self):
		com = self.env.company
		path = self.env['report.it'].get_reports_path()
		file_name = 'Registro de Venta y Costos.xlsx'
		path += file_name
		workbook = Workbook(path)
		worksheet = workbook.add_worksheet("Registro de Venta y Costos")
		bold = workbook.add_format({'bold': True})
		normal = workbook.add_format()
		normal.set_border(style=1)
		normal.set_font_size(8)
		boldbord = workbook.add_format({'bold': True})
		boldbord.set_border(style=1)
		boldbord.set_align('center')
		boldbord.set_align('vcenter')
		boldbord.set_text_wrap()
		boldbord.set_font_size(9)
		boldbord.set_bg_color('#bfbfbf')
		boldbord2 = workbook.add_format({'bold': True})
		boldbord2.set_border(style=1)
		boldbord2.set_align('center')
		boldbord2.set_align('vcenter')
		boldbord2.set_text_wrap()
		boldbord2.set_font_size(9)
		decimal2 = workbook.add_format({'num_format':'0.00', 'font_size': 8})
		decimal2.set_border(style=1)	
		decimal4 = workbook.add_format({'num_format':'0.000000', 'font_size': 8})
		decimal4.set_border(style=1)
		decimal6 = workbook.add_format({'num_format':'0.000000', 'font_size': 8})
		decimal6.set_border(style=1)
		bord = workbook.add_format()
		bord.set_border(style=1)
		bord.set_text_wrap()
		title = workbook.add_format({'bold': True})
		title.set_align('center')
		title.set_align('vcenter')
		title.set_text_wrap()
		title.set_font_size(20)
		fdatetime = workbook.add_format({'num_format': 'dd/mm/yyyy hh:mm','border':1, 'font_size': 8})
		fdate = workbook.add_format({'num_format': 'dd/mm/yyyy','border':1, 'font_size': 8})
		worksheet.set_row(10, 40)
		x = 10
		size_widths = tuple()

		worksheet.merge_range(1, 1, 2, 18, com.name.upper(), title)
		worksheet.merge_range(4, 1, 5, 18, "Registro de Venta y Costos", title)

		worksheet.write(7,1, "Fecha Inicio", boldbord2)
		worksheet.write(8,1, "Fecha Fin", boldbord2)
				
		worksheet.write(x,1, "FECHA EMISION.", boldbord)
		worksheet.write(x,2, "FECHA VENCIMIENTO", boldbord)
		worksheet.write(x,3, "TD", boldbord)
		worksheet.write(x,4, "SERIE", boldbord)
		worksheet.write(x,5, "NÚMERO", boldbord)
		worksheet.write(x,6, "TDP", boldbord)
		worksheet.write(x,7, "RUC", boldbord)
		worksheet.write(x,8, "PARTNER", boldbord)
		worksheet.write(x,9, "CP", boldbord)
		worksheet.write(x,10, "PRODUCTO", boldbord)
		worksheet.write(x,11, "CANTIDAD", boldbord)
		worksheet.write(x,12, "VENTA TOTAL SIN IMPUESTO", boldbord)
		worksheet.write(x,13, "IGV", boldbord)
		worksheet.write(x,14, "TOTAL", boldbord)
		worksheet.write(x,15, "MON", boldbord)
		worksheet.write(x,16, "MONTO ME", boldbord)
		worksheet.write(x,17, "TC", boldbord)
		worksheet.write(x,18, "COSTO PROMEDIO PONDERADO", boldbord)
		x+=1


		facturas_total = self.env['account.move'].sudo().search([('invoice_date', '>', self.period_ini),('invoice_date', '<', self.period_end),('type', '=', 'out_invoice'),('state', '=', 'posted')])

		facturas_list = []
		for facturas_to in facturas_total:
			print(facturas_to)
			facturas_list.extend(facturas_to.invoice_line_ids.ids)
		print(facturas_list)
		
		facturas = self.env['account.move.line'].sudo()
		# print(facturas)

		pedido_venta = self.env['sale.order'].sudo()

		for item in facturas:
			if item.id in facturas_list:
				worksheet.write(x,1, item.move_id.invoice_date or '', fdatetime)
				worksheet.write(x,2, item.move_id.invoice_date_due or '', fdatetime)
				worksheet.write(x,3, item.move_id.type_document_id.code or '', normal)
				if item.move_id.ref == False:
					worksheet.write(x,4, '', normal)
					worksheet.write(x,5, '', normal)
				else:
					ref = item.move_id.ref.split('-')
					if len(ref) == 1:
						worksheet.write(x,4, ref[0] or '', normal)
						worksheet.write(x,5, '', normal)
					else:
						worksheet.write(x,4, ref[0] or '', normal)
						worksheet.write(x,5, ref[1] or '', normal)
				worksheet.write(x,6, item.move_id.partner_id.l10n_latam_identification_type_id.name or '', normal)
				worksheet.write(x,7, item.move_id.partner_id.vat or '', normal)
				worksheet.write(x,8, item.move_id.partner_id.name or '', normal)
				worksheet.write(x,9, item.product_id.default_code or '', normal)
				worksheet.write(x,10, item.product_id.name or '', normal)
				worksheet.write(x,11, item.quantity or '', normal)
				worksheet.write(x,12, (item.quantity*item.price_unit)*item.move_id.currency_rate or '', normal)
				impuestos = item.tax_ids
				lista_impuestos = []
				for impuesto in impuestos:
					lista_impuestos.append(impuesto.amount)
				worksheet.write(x,13, ((sum(lista_impuestos)/100) *item.quantity*item.price_unit)*item.move_id.currency_rate  or '', normal)
				worksheet.write(x,14, item.move_id.amount_total*item.move_id.currency_rate  or '', normal)
				worksheet.write(x,15, item.move_id.currency_id.name  or '', normal)
				worksheet.write(x,16, item.move_id.amount_total  or '', normal)
				worksheet.write(x,17, item.move_id.currency_rate  or '', normal)

				print(item.move_id.name)
				print(item.move_id.invoice_origin)
				pv_fac = pedido_venta.search([('name','=',item.move_id.invoice_origin)],limit=1)
				print(pv_fac)



				x+=1
				# print(item.move_id.ref[:9])


		size_widths = (2, 13, 13, 5, 7, 11, 11, 13, 20, 5, 20, 8, 8,) + 3 * (8,) + (8, 8, 8)

		worksheet = resize_cells_widths(worksheet, size_widths)
		workbook.close()

		return self.env['report.it'].export_file(path, file_name)