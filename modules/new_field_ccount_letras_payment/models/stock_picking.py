# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	delivery_agency = fields.Many2one('res.partner',u'Agencia de envío')