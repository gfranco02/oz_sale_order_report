# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import Warning

class AccountLetrasPaymentManual(models.Model):
	_inherit= 'account.letras.payment.manual'

	@api.onchange('nro_letra')
	def onchange_cu_banco(self):
		same_nro_letra = self.env['account.letras.payment.manual'].search([('nro_letra','=',self.nro_letra)])

		letras=[]
		for letra_name in same_nro_letra:
			letras.append(letra_name.nro_letra)
		
		if self.nro_letra in letras:
			raise Warning('Ya existe una letra con ese nombre en el sistema, coloque un nombre diferente.')

