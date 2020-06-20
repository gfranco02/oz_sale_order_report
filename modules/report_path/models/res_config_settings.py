# -*- coding: utf-8 -*-
from odoo import models, fields, api
from ast import literal_eval

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	path_reports = fields.Char()

	def set_values(self):
		res = super(ResConfigSettings, self).set_values()
		self.env['ir.config_parameter'].set_param('report_path.path_reports', self.path_reports)
		return res

	@api.model
	def get_values(self):
		res = super(ResConfigSettings, self).get_values()
		with_path_reports = self.env['ir.config_parameter'].sudo()
		com_path_reports = with_path_reports.get_param('report_path.path_reports')
		res.update(
			path_reports=com_path_reports
		)
		return res
