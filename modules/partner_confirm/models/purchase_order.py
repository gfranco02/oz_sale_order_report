# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	partner_confirm_id = fields.Integer()

	def button_confirm(self):
		res = super(PurchaseOrder, self).button_confirm()
		self.partner_confirm_id = self.env.uid
		return res

