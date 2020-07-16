# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class AccountLetrasPaymentManual(models.Model):
	_inherit = 'account.letras.payment.manual'

	leter_currency = fields.Char()

	@api.onchange('currency_id')
	def _onchange_currency_id(self):
		print(self.currency_id)
		print(self.currency_id.leter_currency)
		self.leter_currency = self.currency_id.leter_currency
		print(self.leter_currency)
		


