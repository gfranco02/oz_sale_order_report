# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base_it.utils import parse2str_dt

class AssignProductionCostWizard(models.TransientModel):
	_name = 'assign.production_cost.wizard'
	_description = 'Asignar costos de produccción'

	picking_id = fields.Many2one('stock.picking', string='Albarán')
	operation_code = fields.Many2one(related='picking_id.l10n_pe_catalog_12_id')
	type_assign = fields.Selection([
		('manual', 'Asignación manual'), 
		('from_products', 'Desde productos'),], 
		string='Tipo de asignación', default='manual')
	line_ids = fields.One2many('assign.production_cost.line.wizard', 'wizard_id', string='Líneas')


	def refresh_lines(self):
		# refresh unit cost in lines
		if self.type_assign == 'from_products':
			for line in self.line_ids:
				line.price_unit = line._get_avg_cost()
		return {
			'name':'Actualizar costo promedio para operación de producción',
			'type': 'ir.actions.act_window',
			'res_id': self.id,
			'view_id': self.env.ref('toscana_kardex.assign_production_cost_wizard_view_form').id,
			'res_model': 'assign.production_cost.wizard',
			'view_mode': 'form',
			'target': 'new',
		}


	def assign_unit_price_to_moves(self):
		# asignar precio unitario para los stock moves
		if any(l.price_unit <= 0.0 for l in self.line_ids):
			raise UserError('¡Existen líneas sin costo promedio!')

		for line in self.line_ids:
			line.move_id.price_unit = line.price_unit


class AssignProductionCostWizard(models.TransientModel):
	_name = 'assign.production_cost.line.wizard'
	_description = 'Asignar costos de produccción (Línea)'
	
	wizard_id = fields.Many2one('assign.production_cost.wizard', string='Wizard', required=True)
	picking_id = fields.Many2one(related='wizard_id.picking_id', string='Albarán')
	move_id = fields.Many2one('stock.move', string='Movimiento')
	price_unit = fields.Float('Precio unitario', digits=(12, 8), default=0.0)
	product_id = fields.Many2one(related='move_id.product_id', string="Producto", readonly=True)
	product_ids = fields.Many2many('product.product', 
		relation='assign_production_cost_wiz_product_rel', 
		string='Productos (Materia Prima)')


	def _get_avg_cost(self):
		# TODO FIXME ver qué pasará en caso usen lotes y series
		if not self.product_ids:
			raise UserError('Debe asignar algún producto(s) base para obtener un costo promedio')
		
		total_cost = 0.0 #sum(p for p in self.product_ids)
		for p in self.product_ids:
			#params = (p.id,) + 4 * (self.move_id.location_id.id,)
			# TODO FIXME en caso usen lotes, procesar con stock.move.line
			layer = self.env['kdx.valuation.layer'].sudo().get_last_valuation(self.move_id.location_id, self.move_id.product_id)
			# sql = f"""
			# 	SELECT 
			# 	kvl.avg_cost
			# 	FROM 
			# 	kdx_valuation_layer kvl
			# 	JOIN stock_move sm ON sm.id = kvl.move_id
			# 	WHERE sm.state = 'done'
			# 	AND COALESCE(sm.scrapped, false) = false
			# 	AND kvl.product_id = %s 
			# 	AND (kvl.location_id = %s or kvl.location_dest_id = %s)
			# 	AND ((kvl.is_transfer = true AND (kvl.location_id = %s AND kvl.layer_pair_id IS NULL) OR 
			# 		(kvl.location_id != %s AND layer_pair_id IS NOT NULL)) 
			# 		OR COALESCE(kvl.is_transfer, false) != true )
			# 	ORDER BY kvl.date_done DESC, kvl.is_landed_cost DESC, kvl.id DESC LIMIT 1;"""
			
			# self._cr.execute(sql, params)
			# res = self._cr.fetchone()
			# avg_cost = res and res[0] or 0.0
			#total_cost += avg_cost
			total_cost += layer and layer.current_avg_cost or 0.0

		return total_cost