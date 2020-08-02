# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from io import BytesIO
from pdf2image import convert_from_bytes
import base64

class LetterPrintPreviewWizard(models.TransientModel):
	_inherit = 'letter.print.preview.wizard'


	@api.model
	def _print_dot_matrix(self, letters):
		# TODO va a poder imprimirse todo de golpe?
		# por ahora sólo la primera
		tpl = self.env.ref('toscana_account_letras.tmpl_dotmatrix_account_letters_it')
		printer_data = tpl._render_template(tpl.body_html, 'account.letras.payment.manual', letters[0].id)
		return self.env['printer.selection.wizard'].do_print(printer_data, self.env.company)

	def _preview_dot_matrix(self, letter):
		tpl = self.env.ref('toscana_account_letras.tmpl_preview_account_letters_it')
		printer_data = tpl._render_template(tpl.body_html, 'account.letras.payment.manual', letter.id)
		self.dot_matrix_preview = printer_data
		return {"type": "ir.actions.do_nothing",}


	# A4
	def _print_a4(self, letters):
		return self.env.ref('toscana_account_letras.report_letters_a4_format').report_action(letters)

	def _preview_a4(self, letter):
		report_name = "toscana_account_letras.report_letters_a4_format"
		pdf = self.env.ref(report_name).sudo().render_qweb_pdf([letter.id])[0]
		#images = convert_from_bytes(base64.b64decode(encoded), first_page=1, last_page=1)
		images = convert_from_bytes(pdf, first_page=1, last_page=1)
		#images = convert_from_bytes(base64.b64decode(pdf), first_page=1, last_page=1)
		buffered = BytesIO()
		images[0].save(buffered, format="JPEG")
		self.a4_preview = base64.b64encode(buffered.getvalue()) # base64.encodestring(pdf)
		return {"type": "ir.actions.do_nothing",}