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

	# def _get_previus_layer(self, location_id,product_id,date_done):
	# 	# -> Obtener último movimento de product_id en location_id
	# 	# -> Ordenamiento por fecha, si es gasto vinculado y id
	# 	# -> Si hubieran 2 compras con gastos vinculados exactamente 
	# 	# -> en la misma hora, salen primero las compras y luego todos 
	# 	# -> los GV asociados a ellas.
	# 	# ****
		
	# 	date_done = parse2str_dt(date_done)
	# 	start_date = '%s-01-01 00:00:00' % date_done[:4]

	# 	params = (start_date, date_done, product_id) + 4 * (location_id,)
	# 	self.flush()
	# 	sql = f"""
	# 	SELECT ARRAY_AGG(T.id)
	# 	FROM (
	# 		SELECT 
	# 		kvl.id
	# 		FROM 
	# 		kdx_valuation_layer kvl
	# 		JOIN stock_move sm ON sm.id = kvl.move_id
	# 		WHERE sm.state = 'done'
	# 		AND COALESCE(sm.scrapped, false) = false
	# 		AND kvl.date_done >= %s 
	# 		AND kvl.date_done <= %s 
	# 		AND kvl.product_id = %s 
	# 		AND (kvl.location_id = %s or kvl.location_dest_id = %s)
	# 		AND ((kvl.is_transfer = true AND (kvl.location_id = %s AND kvl.layer_pair_id IS NULL) OR 
	# 			(kvl.location_id != %s AND layer_pair_id IS NOT NULL)) 
	# 			OR COALESCE(kvl.is_transfer, false) != true )
	# 		ORDER BY kvl.date_done DESC, kvl.is_landed_cost DESC, kvl.id DESC 
	# 	)T;"""
		
	# 	self._cr.execute(sql, params)
	# 	arr_values = self._cr.fetchone()[0]
	# 	index = arr_values.index(self.id) + 1
	# 	prev_layer_id = arr_values[index : index + 1] or False
	# 	return self.browse(prev_layer_id)
	
	
	
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

		worksheet.merge_range(1, 1, 2, 20, com.name.upper(), title)
		worksheet.merge_range(4, 1, 5, 20, "Registro de Venta y Costos", title)

		worksheet.write(7,1, "Fecha Inicio", boldbord2)
		worksheet.write(8,1, "Fecha Fin", boldbord2)
		worksheet.write(7,2, self.period_ini, fdatetime)
		worksheet.write(8,2, self.period_end, fdatetime)
				
		worksheet.write(x,1, "FECHA EMISION.", boldbord)
		worksheet.write(x,2, "FECHA VENCIMIENTO", boldbord)
		worksheet.write(x,3, "TD", boldbord)
		worksheet.write(x,4, "SERIE", boldbord)
		worksheet.write(x,5, "NÚMERO", boldbord)
		worksheet.write(x,6, "TDP", boldbord)
		worksheet.write(x,7, "RUC", boldbord)
		worksheet.write(x,8, "PARTNER", boldbord)
		worksheet.write(x,9, "VENDEDOR", boldbord)
		worksheet.write(x,10, "CP", boldbord)
		worksheet.write(x,11, "PRODUCTO", boldbord)
		worksheet.write(x,12, "CANTIDAD", boldbord)
		worksheet.write(x,13, "VENTA TOTAL SIN IMPUESTO", boldbord)
		worksheet.write(x,14, "IGV", boldbord)
		worksheet.write(x,15, "TOTAL", boldbord)
		worksheet.write(x,16, "MON", boldbord)
		worksheet.write(x,17, "MONTO ME", boldbord)
		worksheet.write(x,18, "TC", boldbord)
		worksheet.write(x,19, "CANTIDAD DESPACHADA", boldbord)
		worksheet.write(x,20, "COSTO PROMEDIO PONDERADO", boldbord)
		worksheet.write(x,21, "COSTO PROMEDIO PONDERADO TOTAL", boldbord)
		x+=1

		from datetime import datetime, timedelta
		una_fecha = str(self.period_end)
		fecha_dt = datetime.strptime(una_fecha, '%Y-%m-%d')
		plus_date = fecha_dt + timedelta(days=1)

		facturas_total = self.env['account.move'].sudo().search([('invoice_date', '>', self.period_ini),('invoice_date', '<', plus_date),('type', 'in', ('out_invoice','out_refund')),('state', '=', 'posted')])

		facturas_total_rectificativas = self.env['account.move'].sudo().search([('invoice_date', '>', self.period_ini),('invoice_date', '<', plus_date),('type', '=', 'out_refund'),('state', '=', 'posted')])

		facturas_list = []
		for facturas_to in facturas_total:
			facturas_list.extend(facturas_to.invoice_line_ids.ids)

		facturas_rectificativas_list = []
		for facturas_to_2 in facturas_total_rectificativas:
			facturas_rectificativas_list.extend(facturas_to_2.invoice_line_ids.ids)
		
		pedido_venta = self.env['sale.order'].sudo()

		for item in self.env['account.move.line'].browse(facturas_list):
			
			

			if item.id in facturas_list and item.journal_id.name == 'Facturas de cliente':
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
				worksheet.write(x,9, item.move_id.invoice_user_id.name or '', normal)
				worksheet.write(x,10, item.product_id.default_code or '', normal)
				worksheet.write(x,11, item.product_id.name or '', normal)
				worksheet.write(x,12, item.quantity or '', normal)
				precio_cantidad = item.price_subtotal
				
				if item.id in facturas_rectificativas_list:
					precio_producto = precio_cantidad*item.move_id.currency_rate
					worksheet.write(x,13, -precio_producto or '', normal)
					impuestos = item.price_total - precio_cantidad
					worksheet.write(x,14, -(impuestos*item.move_id.currency_rate)  or '', decimal2)
					worksheet.write(x,15,-(precio_producto+impuestos*item.move_id.currency_rate)  or '', decimal2)
				else:
					precio_producto = precio_cantidad*item.move_id.currency_rate
					worksheet.write(x,13, precio_producto or '', normal)
					impuestos = item.price_total - precio_cantidad
					worksheet.write(x,14, impuestos*item.move_id.currency_rate  or '', decimal2)
					worksheet.write(x,15, precio_producto+impuestos*item.move_id.currency_rate  or '', decimal2)

				worksheet.write(x,16, item.move_id.currency_id.name  or '', decimal2)
				if item.move_id.currency_id.name == 'PEN':
					me = 0
				else:
					tot = precio_producto+impuestos*item.move_id.currency_rate
					tc= item.move_id.currency_rate
					me = tot/tc
				worksheet.write(x,17, me  or '', decimal2)
				worksheet.write(x,18, item.move_id.currency_rate  or '', normal)
				pv_fac = pedido_venta.search([('name','=',item.move_id.invoice_origin)],limit=1)


				cantidad_entregada_list = []
				almacen_list=[]
				fechas_list=[]
				worksheet.write(x,19, 0.00, decimal2)
				for entrega in pv_fac.picking_ids:
					if entrega.state == 'done' and entrega.origin == item.move_id.invoice_origin:
						almacen_list.append(entrega.location_id.id)
						fechas_list.append(entrega.date_done)
						for linea_entrega in entrega.move_line_ids_without_package:
							if linea_entrega.product_id.id == item.product_id.id:
								cantidad_entregada_list.append(linea_entrega.qty_done)
								worksheet.write(x,19, sum(cantidad_entregada_list) or 0.00, decimal2)

				worksheet.write(x,20, 0.00, decimal2)
				worksheet.write(x,21, 0.00, decimal2)
				if item.product_id.id != False and item.date != False:
					query = """select unit_cost,product_id,avg_cost,to_char(date_done,'YYYY-MM-DD')
					from kdx_valuation_layer 
					where product_id= %s
					and date_done = '%s'
					and location_id = %s
					ORDER BY date_done DESC, is_landed_cost DESC, id DESC 
					"""%(item.product_id.id,fechas_list[0],almacen_list[0])
					self._cr.execute(query)
					results = self._cr.dictfetchall()
					for item_for in results:
						worksheet.write(x,20, item_for['unit_cost'] or 0.00, decimal2)
						y = x+1
						worksheet.write_formula('V%s'%y, '=T%s*U%s'%(y,y), decimal2)
				x+=1


		size_widths = (2, 13, 13, 5, 7, 11, 11, 13, 20,20, 5, 20, 8, 8,) + 3 * (8,) + (8, 8, 8)

		worksheet = resize_cells_widths(worksheet, size_widths)
		workbook.close()

		return self.env['report.it'].export_file(path, file_name)