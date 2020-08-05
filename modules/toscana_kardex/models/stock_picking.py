# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError



class StockPicking(models.Model):
	_inherit = 'stock.picking'

	def action_update_production_costs(self):
		if self.state == 'done':
			raise UserError('No es posible realizar ésta operación en albaranes realizados.')
		if self.l10n_pe_catalog_12_id.code != '19':
			raise UserError('Esta operación es exclusiva para las operaciones de tipo "Ingreso de producción" (Operación: 19)')

		wiz = self.env['assign.production_cost.wizard'].create({
			'picking_id': self.id,
			'line_ids': [(0, 0, {
				'move_id': m.id,
				'price_unit': m.price_unit,
			}) for m in self.move_lines]
		})

		return {
			'name':'Actualizar costo promedio para operación de producción',
			'type': 'ir.actions.act_window',
			'res_id': wiz.id,
			'view_id': self.env.ref('toscana_kardex.assign_production_cost_wizard_view_form').id,
			'res_model': 'assign.production_cost.wizard',
			'view_mode': 'form',
			'target': 'new',
		}


class StockMove(models.Model):
	_inherit = 'stock.move'

	def _action_done(self, cancel_backorder=False):
		todo_moves = super(StockMove, self)._action_done(cancel_backorder)
		for m in todo_moves:
			if m.picking_id.l10n_pe_catalog_12_id.code == '19' and ((m.price_unit or 0.0) <= 0.0):
				raise UserError(f'Debe establecer el costo manaulmente para  el movimiento '
								f'del producto {m.product_id.name} que es de tipo "Ingreso de producción".')
		return todo_moves