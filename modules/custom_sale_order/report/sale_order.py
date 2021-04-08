# -*- encoding: utf-8 -*-
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
import os

class SaleOrder(models.Model):
	_inherit='sale.order'

	delivery_agency = fields.Char(u'Agencia de envío') # que hacía ésta mrd en letras?? 

	def build_report_pdf(self):
		if not self: return
		if any(lt.partner_id.id != self[0].partner_id.id for lt in self):
			raise UserError('User error')

		# Formato estándard de letra
		path = self.env['bo.report.base'].get_reports_path()
		now = fields.Datetime.context_timestamp(self, fields.Datetime.now())
		file_name = u'Cotizacion %s.pdf' % str(now)[:19].replace(':','_')
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
		col_widths = [float(i)/100*wUtil for i in (49,10,10,10,11,10)]

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
		##
		white = colors.Color(red=(255/255),green=(255/255),blue=(255/255))
		black = colors.Color(red=(50/255),green=(50/255),blue=(50/255))
		red = colors.Color(red=(185/255),green=(18/255),blue=(18/255))
		##
		#
		p13 = ParagraphStyle('p13', alignment=TA_LEFT, fontSize=10, fontName="Calibri-Bold", textColor=white)
		p14 = ParagraphStyle('p14', alignment=TA_LEFT, fontSize=10, fontName="Calibri-Bold", textColor=red)
		#
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
				[Paragraph("DESCRIPCIÓN", p6),Paragraph("CANTIDAD", p9), Paragraph("PRECIO UNITARIO", p9),Paragraph("DESC,%", p9),Paragraph("IMPUESTOS", p9), Paragraph("IMPORTE", p5)],
			]
			hTable=Table(data, colWidths=col_widths, rowHeights=(32))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,1), (-1,-1),1, black),
				('TEXTCOLOR',(0, 1),(-1,-1), blue2),
				('SPAN', (0,0), (0,0)),
				#
				('GRID', (0,0), (-1,-1),0.5,black),
				#
				]))
			hTable.wrapOn(c, 120, 500)
			hTable.drawOn(c, pos_left, pos)

		#####
		def black_header(c, pos,str):
			data=[
				[Paragraph(str, p13),'','','','',''],
			]
			hTable=Table(data, colWidths=col_widths, rowHeights=(15))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,1), (-1,-1),1, black),
				('TEXTCOLOR',(0, 0),(-1,-1), white),
				('SPAN', (0,0), (-1,0)),
				('BACKGROUND',(0, 0),(-1,-1), black)
				]))
			hTable.wrapOn(c, 120, 500)
			hTable.drawOn(c, pos_left, pos - 10)

		def total_table(c, pos):
			data=[
				[Paragraph("Subtotal", p14),''],
				[Paragraph("IGV en", p7),''],
				[Paragraph("Total", p13),''],
			]
			hTable=Table(data, colWidths=(70), rowHeights=(15))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0), (-1,-1),1, black),
				('TEXTCOLOR',(0, 0),(-1,-1), red),
				('SPAN', (0,0), (-1,0)),
				('BACKGROUND',(0, 2),(-1,-1), red),
				('GRID', (0,0), (-1,-1),0.5,black),
				]))
			hTable.wrapOn(c, 120, 500)
			hTable.drawOn(c, pos_left+435, pos - 10)
		#####

		c.drawImage(ImageReader(os.path.dirname(os.path.abspath(__file__))+'/img/Caratula.jpg'),0,0, width=wPage+0, height=hPage+0, mask='auto')
		c.showPage()
		header(c)
		c.setFont("Calibri", 10)
		c.drawString(360,770,u'RUC:')
		c.drawString(360,760,u'Mz. l Lote 21 Int. 2Urb. Tahuaycani(Segundo piso)')
		c.drawString(360,750,u'AREQUIPA -- AREQUIPA - SACHACA')
		partner = self[0].partner_id

		data = [
			[Paragraph(u'Fecha cotización:',p6), Paragraph(u'Consultor de ventas: ', p3)],
			[Paragraph(u'Fecha vencimiento:',p6), Paragraph(u'Plazo de pago: ', p3)],
			['', ''],
			['', ''],
			[Paragraph(u'Cliente:', p3), ''],
			['', ''],
			[Paragraph(u'RUC/DNI:', p3), ''],
			['', ''],
			[Paragraph(u'Dirección:', p3), ''],
			['', ''],
			[Paragraph(u'Contacto:', p3), ''],
			['', ''],
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

		pos -= 65
		header_table(c, pos)
		black_header(c,pos,str="Servicios de Implementación")
		black_header(c,pos-15,str="Personalizaciones")
		black_header(c,pos-28,str="Licencias de Odoo")
		black_header(c,pos-41,str="Servidores en la nube")
		total_table(c,pos-88)


		#FIXME:
		#for i, line in enumerate(self, 1):
			#data = [
				#[Paragraph('', p7), Paragraph('', p10), Paragraph('', p10), 
					#Paragraph('', p10),Paragraph('', p10), Paragraph('', p10)],
			#]
			#t=Table(data, colWidths=col_widths)

			#t_style = [
				#3('VALIGN',(0,0),(-1,-1),'TOP'),
			#]

			#if i % 2 != 0:
				#t_style.append(('BACKGROUND', (0, 0), (-1, -1), blue1))

			#t.setStyle(TableStyle(t_style))
			#w_table, h_table=t.wrap(0,0)
			#t.wrapOn(c, 120, 500)
			#pos -= h_table
			#if pos < bottom:
				#c.showPage()
				#header(c)
				#pos = hPage-180
				#header_table(c, pos)
				#pos-=h_table
				#t.drawOn(c,pos_left, pos-20)
			#else: t.drawOn(c, pos_left, pos-20)
		#


		data = [
			['', ''],
			[Paragraph(u'Cuentas Bancarias',p3), ''],
			[Paragraph('__________________', p6), ''],
			['', ''],
			[Paragraph('BBVA CC SOLES 0011-0908-01-00009648',p3), ''],
			[Paragraph('CCI SOLES 011-908-000100009648-15',p3), ''],
			['', ''],
			[Paragraph('BBVA CC DÓLARES 0011-0908-01-00009656',p3), ''],
			[Paragraph('CCI DÓLARES 011-908-000100009656-15',p3), ''],
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
		t.drawOn(c,pos_left,pos-85)
		pos -= separator



		c.showPage()
		c.drawImage(ImageReader(os.path.dirname(os.path.abspath(__file__))+'/img/reverso.jpg'),0,0, width=wPage+0, height=hPage+0, mask='auto')
		c.showPage()
		c.setAuthor(self.env.company.name)
		c.setTitle(file_name)
		c.setSubject('Reportes')
		c.save()
		#Exportación
		return self.env['bo.report.base'].export_file(path, file_name)
