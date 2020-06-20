# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	partner_confirm_id = fields.Integer()

	def action_confirm(self):
		res = super(SaleOrder, self).action_confirm()
		self.partner_confirm_id = self.env.uid
		return res

