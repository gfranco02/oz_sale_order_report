# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class AccountLetrasPaymentManual(models.Model):
	_inherit = 'account.letras.payment.manual'

	cu_banco = fields.Char('CU Banco')