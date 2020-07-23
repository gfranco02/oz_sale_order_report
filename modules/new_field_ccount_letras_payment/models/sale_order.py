# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	delivery_agency = fields.Many2one('res.partner',u'Agencia de envío')