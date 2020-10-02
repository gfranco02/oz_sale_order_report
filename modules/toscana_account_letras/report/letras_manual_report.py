# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import base64
from io import BytesIO
from decimal import Decimal
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Table ,TableStyle ,SimpleDocTemplate,Image
from reportlab.lib.utils import simpleSplit,ImageReader
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle,getSampleStyleSheet
from reportlab.pdfgen import canvas
from odoo.addons.report_it.utils import register_fonts, get_encoded_image


class AccountLetrasPaymentManual(models.Model):
	_inherit = 'account.letras.payment.manual'

	def action_print_card_format_format(self):
		if not self: return
		if any(lt.partner_id.id != self[0].partner_id.id for lt in self):
			raise UserError('Las letras a imprimir deben pertenecer a un mismo cliente/partner.')

		# Formato estándard de letra
		path = self.get_reports_path()
		now = fields.Datetime.context_timestamp(self, fields.Datetime.now())
		file_name = u'Letras %s.pdf' % str(now)[:19].replace(':','_')
		path += file_name
		register_fonts(['Calibri', 'Calibri-Bold'])
		wPage, hPage = A4
		pos_left = 10
		c = canvas.Canvas(path , pagesize= (wPage, hPage))
		wUtil = wPage - 2 * pos_left # Util width : Real Width - left margins
		middle = wPage / 2 # Center page
		pos = hPage - 150
		separator = 12
		bottom = 55
		col_widths = [float(i)/100*wUtil for i in (13,16,9,12,12,13,12,13)]
		

		p1 = ParagraphStyle('p1', alignment=TA_CENTER, fontSize=8, fontName="Calibri-Bold")
		p2 = ParagraphStyle('p2', alignment=TA_LEFT, fontSize=10, fontName="Calibri")
		p3 = ParagraphStyle('p3', alignment=TA_LEFT, fontSize=10, fontName="Calibri")
		p4 = ParagraphStyle('p4', alignment=TA_RIGHT, fontSize=10, fontName="Calibri")
		p5 = ParagraphStyle('p5', alignment=TA_RIGHT, fontSize=10, fontName="Calibri-Bold")
		p6 = ParagraphStyle('p6', alignment=TA_LEFT, fontSize=10, fontName="Calibri-Bold")
		p7 = ParagraphStyle('p7', alignment=TA_LEFT, fontSize=11, fontName="Calibri")
		p8 = ParagraphStyle('p8', alignment=TA_CENTER, fontSize=12, fontName="Calibri-Bold")
		p9 = ParagraphStyle('p9', alignment=TA_CENTER, fontSize=10, fontName="Calibri-Bold")
		p10 = ParagraphStyle('p10', alignment=TA_RIGHT, fontSize=10, fontName="Calibri")
		p11 = ParagraphStyle('p11', alignment=TA_CENTER, fontSize=11, fontName="Calibri-Bold")
		p12 = ParagraphStyle('p12', alignment=TA_CENTER, fontSize=10, fontName="Calibri")
		
		style = getSampleStyleSheet()["Normal"]
		gray = colors.Color(red=(200.0/255),green=(200.0/255),blue=(200.0/255))
		blue1 = colors.Color(red=(217.0/255),green=(226.0/255),blue=(243.0/255)) 
		blue2 = colors.Color(red=(26.0/255),green=(121.0/255),blue=(189.0/255)) 

		months = {
			1: "Enero",
			2: "Febrero",
			3: "Marzo",
			4: "Abril",
			5: "Mayo",
			6: "Junio",
			7: "Julio",
			8: "Agosto",
			9: "Septiembre",
			10: "Octubre",
			11: "Noviembre",
			12: "Diciembre",
		}

		def header(c):
			com = self.env.company
			if com.logo:
				c.drawImage(ImageReader(get_encoded_image(com.logo)), pos_left, hPage-100, width=180, height=50, mask='auto')

		def header_table(c, pos):
			data=[
				[Paragraph("ESTADO DE CUENTA", p8), '', '', '', '', '', '', ''],
				[Paragraph("FECHA VENCIMIENTO", p9),Paragraph("FACTURA", p9), Paragraph("NRO LETRA", p9),Paragraph("CODIGO UNICO", p9),Paragraph("BANCO", p9), Paragraph("MONTO LETRA", p9), Paragraph("COSTO RETIRO LETRA", p9), Paragraph("MONTO TOTAL", p9)],
			]
			hTable=Table(data, colWidths=col_widths, rowHeights=(32))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0), (-1,-1),1, blue1),
				('TEXTCOLOR',(0, 1),(-1,-1), blue2),
				('SPAN', (0,0), (-1,0)),
				#('BACKGROUND',(0, 1),(-1,-1), colors.blue)
				]))
			hTable.wrapOn(c, 120, 500)
			hTable.drawOn(c, pos_left, pos)

		header(c)
		partner = self[0].partner_id
		#date_order = dt.to_string(dt.context_timestamp(self, dt.from_string()))

		date_str = f'Lima, {str(now.day).rjust(2, "0")} de {months.get(now.month)} de {now.year}'

		data = [
			['', Paragraph(date_str, p3)],
			[Paragraph(u'SEÑORES:',p6), ''],
			[Paragraph(partner.name.upper(), p6), ''],
			[Paragraph(partner.street or '', p3), ''],
			[Paragraph('Presente.',p6), ''],
			['', ''],
			[Paragraph('Por medio de la presente, les hacemos llegar su Estado de Cuenta.', p6), ''],
		]
		
		t = Table(data, colWidths=[float(i) / 100 * wUtil for i in (60, 50)], rowHeights=(separator))
		t.setStyle(TableStyle([
			('VALIGN', (0, 0), (-1,-1), 'MIDDLE'),
			('SPAN', (0,2), (1,2)),
			('SPAN', (0,3), (1,3)),
			('SPAN', (0,5), (1,5)),
		]))
		w_table,h_table=t.wrap(0,0)
		t.wrapOn(c, 120, 500)
		pos -= h_table
		t.drawOn(c,pos_left,pos)
		pos -= separator
		
		#c.setFont("Calibri", 10)
		
		#c.drawString(pos_left,pos,u'Mediante la presente nos es muy grato cotizar a continuación lo siguiente:')
		pos -= 65
		header_table(c, pos)

		total_discount = total_sub = 0.0
		for i, line in enumerate(self, 1):
			fecha_ven = str(line.expiration_date)
			invoices = line.moves_name_str
			letter_name = line.nro_letra
			cu_banco = line.cu_banco
			curr_symbol = line.currency_id.symbol
			amount_letter   = curr_symbol + ' {:,.2f}'.format(Decimal("%0.2f" % line.imp_div))
			withdrawal_cost = curr_symbol + ' {:,.2f}'.format(Decimal("%0.2f" % line.withdrawal_cost))
			amount_total    = curr_symbol + ' {:,.2f}'.format(Decimal("%0.2f" % (line.imp_div + line.withdrawal_cost)))
			banco = line.bank_id.name

			data = [
				[Paragraph(fecha_ven or '', p12), Paragraph(invoices or '', p2), Paragraph(letter_name or '', p12), 
					Paragraph(cu_banco or '', p12),Paragraph(banco or '', p2), Paragraph(amount_letter or '', p4), 
					Paragraph(withdrawal_cost or '', p4), Paragraph(amount_total or '', p4)],
			]
			t=Table(data, colWidths=col_widths)

			t_style = [
				('VALIGN',(0,0),(-1,-1),'TOP'),
			]

			if i % 2 != 0:
				t_style.append(('BACKGROUND', (0, 0), (-1, -1), blue1))

			t.setStyle(TableStyle(t_style))
			w_table, h_table=t.wrap(0,0)
			t.wrapOn(c, 120, 500)
			pos -= h_table
			if pos < bottom:
				c.showPage()
				header(c)
				pos = hPage-180
				header_table(c, pos)
				pos-=h_table
				t.drawOn(c,pos_left, pos)
			else: t.drawOn(c, pos_left, pos)

		
		data = [
			['', ''],
			[Paragraph(u'Agradeceremos mucho se sirvan las letras firmadas a nuestra dirección:',p3), ''],
			[Paragraph(self.env.company.street, p6), ''],
			['', ''],
			[Paragraph('Sin otro particular, quedamos de ustedes.',p3), ''],
			['', ''],
			[Paragraph('Atentamente.',p3), ''],
			['', ''],
			['', ''],
			['', ''],
			['', ''],
			['', ''],
			[Paragraph('____________________________________.',p11)],
			[Paragraph('ALBERTO JOSÉ CAMAIORA CHIAPPE.',p11)],
			[Paragraph('GERENTE GENERAL.',p11)],
			[Paragraph('TOSCANA IMPORT S.A.C.',p11)],
		]
		t = Table(data, colWidths=595, rowHeights=(separator))
		t.setStyle(TableStyle([
			('VALIGN', (0, 0), (-1,-1), 'MIDDLE'),
			('SPAN', (0,2), (1,2)),
			('SPAN', (0,3), (1,3)),
			('SPAN', (0,5), (1,5)),
		]))

		w_table,h_table=t.wrap(0,0)
		t.wrapOn(c, 120, 500)
		pos -= h_table
		t.drawOn(c,pos_left,pos)
		pos -= separator
		
		
		# c.drawImage(ImageReader(get_encoded_image(self.env.company.logo)), 200, 20, width=180, height=50, mask='auto')
		c.setFont("Calibri", 10)
		c.drawString(465,70,u'Calle Manuel A. Odria 268')
		c.drawString(506,60,u'LIMA -Ate -Perú')
		c.drawString(498,50,u'T+ (511) 405 2138')
		c.drawString(403,40,u'Atención al cliente: clientes@tosisac.com ')
		c.setFont("Calibri-Bold", 10)
		c.drawString(422,20,u'IMPORTADORES & DISTRIBUIDORES')


		c.showPage()
		c.setAuthor(self.env.company.name)
		c.setTitle(file_name)
		c.setSubject('Reportes')
		c.save()
		return self.export_file(path, file_name)
