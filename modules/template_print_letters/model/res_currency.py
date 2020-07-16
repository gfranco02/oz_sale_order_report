# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class AccountLetrasPaymentManual(models.Model):
	_inherit = 'res.currency'

	leter_currency = fields.Char(u'Nombre de moneda en letras')