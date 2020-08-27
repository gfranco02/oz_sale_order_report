# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.report_it.utils import get_excel_logo, resize_cells_widths
from xlsxwriter.workbook import Workbook

class ReportSaleCostWizard(models.TransientModel):
	_name='report.sale.cost.wizard'
	_inherit = ['report.it']
	_description = 'Reporte de costos de ventas'

	start_date = fields.Date(u'Fecha inicial', default=lambda self: fields.Date.context_today(self))
	end_date = fields.Date(u'Fecha Final', default=lambda self: fields.Date.context_today(self))

	def build_report_excel(self):
		com = self.env.company
		path = self.get_reports_path()
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
		decimal2bold = workbook.add_format({'num_format':'0.00', 'font_size': 9, 'bold': True})
		decimal2bold.set_border(style=1)
		decimal4 = workbook.add_format({'num_format':'0.0000', 'font_size': 8})
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
		x = 13

		if com.logo:
			worksheet.insert_image('B2', 'company.jpg', get_excel_logo(com.logo))

		worksheet.merge_range(1, 7, 2, 16, com.name.upper(), title)
		worksheet.merge_range(4, 7, 5, 16, "Registro de Ventas y Costos", title)

		worksheet.write(10,1, "Fecha Inicio", boldbord2)
		worksheet.write(11,1, "Fecha Fin", boldbord2)
		worksheet.write(10,2, self.start_date, fdate)
		worksheet.write(11,2, self.end_date, fdate)
		
		worksheet.set_row(x, 36)

		worksheet.write(x, 1, "FECHA EMISIÓN.", boldbord)
		worksheet.write(x, 2, "FECHA VENCIMIENTO", boldbord)
		worksheet.write(x, 3, "T.D.", boldbord)
		worksheet.write(x, 4, "SERIE", boldbord)
		worksheet.write(x, 5, "NÚMERO", boldbord)
		worksheet.write(x, 6, "TIPO DOC. PARTNER", boldbord)
		worksheet.write(x, 7, "NRO. DOCUMENTO", boldbord)
		worksheet.write(x, 8, "PARTNER", boldbord)
		worksheet.write(x, 9, "VENDEDOR", boldbord)
		worksheet.write(x, 10, "COD. PRODUCTO", boldbord)
		worksheet.write(x, 11, "PRODUCTO", boldbord)
		worksheet.write(x, 12, "CANTIDAD", boldbord)
		worksheet.write(x, 13, "UNIDAD DE MEDIDA", boldbord)
		worksheet.write(x, 14, "TOTAL SIN IMPUESTOS", boldbord)
		worksheet.write(x, 15, "IMPUESTOS (IGV)", boldbord)
		worksheet.write(x, 16, "TOTAL", boldbord)
		worksheet.write(x, 17, "MONEDA", boldbord)
		worksheet.write(x, 18, "MONTO M.E.", boldbord)
		worksheet.write(x, 19, "T.C.", boldbord)
		worksheet.write(x, 20, "CANTIDAD DESPACHADA", boldbord)
		worksheet.write(x, 21, "COSTO PROMEDIO UNIT.", boldbord)
		worksheet.write(x, 22, "COSTO PROMEDIO TOTAL", boldbord)
		x+=1

		total_untaxed = total_taxes = total_included = total_fc = 0.0

		sql = """
		SELECT 
		am.invoice_date,
		am.invoice_date_due,
		eic1.code AS type_doc,
		SUBSTRING(am.ref, 0, 5) AS serie,
		SUBSTRING(am.ref, 6, 15) AS inv_number,
		it.name AS partner_doc,
		rp.vat AS partner_vat,
		rp.name AS parner_name,
		rp2.name AS seller,
		pt.default_code AS product_code,
		pt.name AS product,
		ROUND(aml.quantity * uom_prod.factor / uom_aml.factor, 4) AS aml_qty,
		uom_prod.name AS uom,
		aml.price_subtotal * aml.tc AS total_excluded,
		aml.price_total * aml.tc AS total_included,
		(aml.price_total - aml.price_subtotal) * aml.tc AS taxes,
		CASE WHEN rc.name != 'PEN' THEN aml.price_subtotal ELSE 0.0 END AS amount_fc,
		rc.name AS currency,
		aml.tc AS tc,
		kvl.unit_cost AS cost_product,
		CASE 
			WHEN sm.product_qty IS NOT NULL THEN SUM(sm.product_qty) 
			WHEN sm2.product_qty IS NOT NULL THEN -SUM(sm2.product_qty)
			ELSE 0.0 END AS delivered_qty
		FROM 
		account_move_line aml
		JOIN account_move am ON (am.id = aml.move_id AND aml.exclude_from_invoice_tab = false)
		JOIN res_currency rc ON rc.id = am.currency_id
		JOIN account_journal aj ON aj.id = am.journal_id
		LEFT JOIN product_product pp ON pp.id = aml.product_id
		LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
		LEFT JOIN uom_uom uom_aml ON uom_aml.id = aml.product_uom_id
		LEFT JOIN uom_uom uom_prod ON uom_prod.id = pt.uom_id
		LEFT JOIN res_partner rp ON rp.id = am.partner_id
		LEFT JOIN l10n_latam_identification_type it ON it.id = rp.l10n_latam_identification_type_id
		LEFT JOIN einvoice_catalog_01 eic1 ON eic1.id = am.type_document_id
		LEFT JOIN res_users ru ON ru.id = am.invoice_user_id
		LEFT JOIN res_partner rp2 ON rp2.id = ru.partner_id
		LEFT JOIN stock_move sm ON (
			sm.kdx_invoice_line_id = aml.id 
			AND am.type = 'out_invoice' 
			AND sm.state = 'done'
			AND sm.product_id = aml.product_id) 
		LEFT JOIN stock_move sm2 ON (
			sm.kdx_invoice_refund_line_id = aml.id 
			AND am.type = 'out_refund' 
			AND sm2.kdx_catalog_12_code = '24' -- sólo dev de venta
			AND sm2.product_id = aml.product_id) 
		LEFT JOIN kdx_valuation_layer kvl ON (kvl.is_landed_cost = false AND (kvl.move_id = sm.id OR kvl.move_id = sm2.id))
		WHERE 
		am.type IN ('out_invoice', 'out_refund')
		AND am.state = 'posted'
		AND aj.type = 'sale'
		AND aj.name != 'Facturas para letras INV INI' -- FIXME
		AND am.invoice_date BETWEEN %s AND %s
		GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20, sm.product_qty, sm2.product_qty, am.ref 
		ORDER BY am.ref; """

		self._cr.execute(sql, (self.start_date, self.end_date))

		for line in self._cr.dictfetchall():
			worksheet.write(x, 1, line['invoice_date'] or '-', fdate)
			worksheet.write(x, 2, line['invoice_date_due'] or '-', fdate)
			worksheet.write(x, 3, line['type_doc'] or '-', normal)
			worksheet.write(x, 4, line['serie'] or '-', normal)
			worksheet.write(x, 5, line['inv_number'] or '-', normal)
			worksheet.write(x, 6, line['partner_doc'] or '-', normal)
			worksheet.write(x, 7, line['partner_vat'] or '-', normal)
			worksheet.write(x, 8, line['parner_name'] or '-', normal)
			worksheet.write(x, 9, line['seller'] or '-', normal)
			worksheet.write(x, 10, line['product_code'] or '-', normal)
			worksheet.write(x, 11, line['product'] or '-', normal)
			worksheet.write(x, 12, line['aml_qty'] or '-', decimal2)
			worksheet.write(x, 13, line['uom'] or '-', normal)

			excluded = line['total_excluded'] or 0.0 
			taxes = line['taxes'] or 0.0
			included = line['total_included'] or 0.0
			amount_fc = line['amount_fc'] or 0.0

			total_untaxed += excluded
			total_taxes += taxes
			total_included += included
			total_fc += amount_fc

			worksheet.write(x, 14, excluded, decimal2)
			worksheet.write(x, 15, taxes, decimal2)
			worksheet.write(x, 16, included, decimal2)
			worksheet.write(x, 17, line['currency'] or '-', normal)
			worksheet.write(x, 18, amount_fc, decimal2)
			worksheet.write(x, 19, line['tc'] or '-', decimal4)
			
			delivered_qty = line['delivered_qty'] or 0.0
			cost_product = line['cost_product'] or 0.0
			
			worksheet.write(x, 20, delivered_qty, decimal4)
			worksheet.write(x, 21, cost_product, decimal4)
			worksheet.write(x, 22, delivered_qty * cost_product, decimal4)
			x-=-1 # lol

		worksheet.write(x, 14, total_untaxed, decimal2bold)
		worksheet.write(x, 15, total_taxes, decimal2bold)
		worksheet.write(x, 16, total_included, decimal2bold)
		worksheet.write(x, 18, total_fc, decimal2bold)

		size_widths = (2, 9, 9, 4, 5, 11, 7, 10, 22, 15, 9, 25, 10, 10,) + 3 * (10,) + (5, 10, 6) + 3 * (10,)
		worksheet = resize_cells_widths(worksheet, size_widths)
		workbook.close()
		return self.export_file(path, file_name)