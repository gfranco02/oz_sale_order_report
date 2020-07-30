# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import base64
import re 

class AccountLetrasPaymentManual(models.Model):
	_inherit = 'account.letras.payment.manual'

	leter_currency = fields.Char()
	print_letter = fields.Boolean(u'¿Imprimir?',readonly=False)
	cu_banco = fields.Char('CU Banco')


	@api.onchange('print_letter')
	def _onchange_print_letter(self):
		valor = self.print_letter
		id_line = re.findall("\d+", str(self.id)) 
		if id_line != False:
			query = """
					UPDATE account_letras_payment_manual
					SET print_letter = %s
					WHERE id = %s;
				"""%(valor,id_line[0])
			self._cr.execute(query)
			query2 = """
					UPDATE account_letras_payment_manual
					SET leter_currency = '%s'
					WHERE id = %s;
				"""%(str(self.letra_payment_id.currency_id.leter_currency),id_line[0])
			self._cr.execute(query2)
		

class AccountLetrasPayment(models.Model):
	_name = 'account.letras.payment'
	_inherit = 'account.letras.payment'

	type_impresion = fields.Selection([('ic','Impresión Continua'),('in','Impresión por Letra')],string=u'Tipo de Impresión',default='ic')


	def generate_report_file(self):
		if self.type_impresion == 'ic':
			tpl = self.env['mail.template'].search([('name', '=', 'Dot Matrix Letters')])
			# print('ic')
		if self.type_impresion == 'in':
			tpl = self.env['mail.template'].search([('name', '=', 'Dot Matrix Letters 2')])
			# print('in')
		if self.type_impresion == False:
			raise UserError(u'Debe de seleccionar un tipo de impresión')
		
		data = tpl._render_template(tpl.body_html, 'account.letras.payment', self.id)
		self.printer_data = data
		
		report_name = "print_letters.report_letters_bo_it_grupo_id_unico"
		pdf = self.env.ref(report_name).sudo().render_qweb_pdf([self.id])[0]
		self.report_layout_binary = base64.encodestring(pdf)

		form_view_id = self.env.ref('print_letters.view_document_preview_letras_bo_it_grupo').id

		return {
					'type': 'ir.actions.act_window',
					'name': u'Le recomendamos previsualizar el documento antes de imprimirlo',
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'account.letras.payment',
					'views': [[form_view_id, "form"]],
					'res_id': self.id,
					'target': 'new'
			}