# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class KardexValuationLayer(models.Model):
	_inherit = 'kdx.valuation.layer'


	def _compute_operation_19(self, previus_layer=None):
		# TODO debería entrar siempre a una ubicación de stock
		if self.location_dest_id.usage != 'internal':
			raise UserError('La ubicación destino en las operaciones de tipo "19" debe ser de tipo interno.')
		previus_layer = previus_layer or self._get_previus_layer(self.location_dest_id)
		unit_cost = self.move_id.price_unit
		return previus_layer, self.product_qty, unit_cost