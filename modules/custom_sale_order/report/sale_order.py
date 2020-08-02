# -*- encoding: utf-8 -*-
import base64,io,string,decimal,os
from odoo import models, fields, api
from xlsxwriter.workbook import Workbook
from datetime import datetime
from odoo.exceptions import UserError
import codecs, pprint, pytz,base64
from decimal import Decimal
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Table ,TableStyle ,SimpleDocTemplate,Image
from reportlab.lib.utils import simpleSplit,ImageReader
from reportlab.lib.enums import TA_CENTER,TA_RIGHT,TA_LEFT,TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle,getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from odoo.addons.report_it.utils import register_fonts
# global variables
wPage,hPage = (595,842)
pos_left = 20 # padding
bottom = 55
pos = hPage-96 # dynamic vertical position
wUtil = wPage-2*pos_left # Util width : Real Width - left margins
middle = wPage/2 # Center page
pos_right = middle+pos_left
col_widths0 = [float(i)/100*wUtil for i in (64,12,12,12)] # size of columns (list sum = 100%)
col_widths = [float(i)/100*wUtil for i in (7,6,5,6,4,6,12,6,6,6,6,6,6,6,6,6)] # size of columns (list sum = 100%)

col_widths1 = [float(i)/100*wUtil for i in (37,25,12)] # size of columns (list sum = 100%)
col_widths2 = [float(i)/100*wUtil for i in (7,6,6,6,6,6,7,6,6,6,6,6,7,20)] # size of columns (list sum = 100%)

separator = 12 # separador entre lineas
register_fonts(['Calibri', 'Calibri-Bold'])

p1 = ParagraphStyle('p1',alignment=TA_CENTER,fontSize=8,fontName="Calibri-Bold")
p1_1 = ParagraphStyle('p1_1',alignment=TA_LEFT,fontSize=8,fontName="Calibri-Bold")
p2 = ParagraphStyle('p2',alignment=TA_LEFT,fontSize=7,fontName="Calibri")
p2_1 = ParagraphStyle('p2_1',alignment=TA_CENTER,fontSize=7,fontName="Calibri")
p3 = ParagraphStyle('p3',alignment=TA_LEFT,fontSize=10,fontName="Calibri")
p4 = ParagraphStyle('p4',alignment=TA_RIGHT,fontSize=10,fontName="Calibri")
p5 = ParagraphStyle('p5',alignment=TA_RIGHT,fontSize=10,fontName="Calibri-Bold")
p6 = ParagraphStyle('p6',alignment=TA_LEFT,fontSize=10,fontName="Calibri-Bold")
p7 = ParagraphStyle('p7',alignment=TA_LEFT,fontSize=11,fontName="Calibri")
style = getSampleStyleSheet()["Normal"]
gray = colors.Color(red=(200.0/255),green=(200.0/255),blue=(200.0/255))

TF = ParagraphStyle('p1',alignment=TA_CENTER,fontSize=9,fontName="Calibri-Bold")
TF_1 = ParagraphStyle('p2',alignment=TA_CENTER,fontSize=9,fontName="Calibri")


class SaleOrder(models.Model):
	_inherit='sale.order'

	delivery_agency = fields.Char(u'Agencia de envío') # que hacía ésta mrd en letras?? 

	def build_report_pdf(self):
		if self.state == 'draft':
			name_state = u'COTIZACIÓN'
		if self.state == 'sale':
			name_state = u'ORDEN DE VENTA'
		if self.state != 'sale' and self.state != 'draft':
			name_state = u'Presupuesto-Pedido'

		path = self.env['report.it'].get_reports_path()
		# path = self.env['res.config.settings'].search([('path_reports','!=',False)],limit=1).path_reports
		now = fields.Datetime.context_timestamp(self,datetime.now())
		name = name_state
		file_name = u'S.0. %s %s.pdf'%(name,str(now)[:19].replace(':','_'))
		path += file_name
		c = canvas.Canvas(path , pagesize=(595,842))
		pos = hPage - 90
		

		def header_table1(c,pos):
			src_path = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')
			header_path=src_path+'/Toscana_logo.JPG'
			header_logo=ImageReader(header_path)
			c.drawImage(header_logo,20,pos-10,width=330,height=70,mask='auto')

			data= [[name_state],
			['Numero: %s'%(self.name or ' ')],
			['Fecha: %s'%(str(self.date_order)[0:10])]]
			Table_1=Table(data)
			Table_1.setStyle(TableStyle([
				('ALIGN',(0,-1),(-1,-1),'CENTER'),
				('BOX',(0,0),(-1,-1),1,colors.black),
				('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
				('VALIGN',(0,0),(-1,-1),'TOP'),
				('ALIGN',(0,-1),(-1,-1),'RIGHT'),
				('FONT',(0,0),(-1,-1),'Calibri-Bold'),
				('FONTSIZE',(0,0),(-1,-1),10)
				]))
			
			Table_1.wrapOn(c,120,500)
			Table_1.drawOn(c,444,pos)
		
		header_table1(c,pos)

		def header_table2(c,pos):
			data=[[Paragraph(u"Cliente: %s"%(self.partner_id.name or ' '),p1_1)],]
			hTable=Table(data,colWidths=340,rowHeights=(15))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0),(-1,-1),1,colors.black)
				]))
			hTable.wrapOn(c,120,500)
			hTable.drawOn(c,pos_left,pos-50)

			data=[[Paragraph(u"Contacto: %s"%(self.contact_order_id.name or ' '),p1_1)],]
			hTable=Table(data,colWidths=340,rowHeights=(15))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0),(-1,-1),1,colors.black)
				]))
			hTable.wrapOn(c,120,500)
			hTable.drawOn(c,pos_left,pos-65)

			data=[[Paragraph(u"DNI O RUC:",p1_1),Paragraph(u"%s"%(self.partner_id.vat or ' '),p1_1),Paragraph(u"Codigo:",p1_1),Paragraph(u"%s"%(self.partner_id.ref or ' '),p1_1)],]
			hTable=Table(data,colWidths=85,rowHeights=(15))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0),(-1,-1),1,colors.black)
				]))
			hTable.wrapOn(c,120,500)
			hTable.drawOn(c,pos_left,pos-80)

			data=[[Paragraph(u"Dirección: %s"%(self.partner_id.street or ' '),p1_1)],]
			hTable=Table(data,colWidths=340,rowHeights=(15))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0),(-1,-1),1,colors.black)
				]))
			hTable.wrapOn(c,120,500)
			hTable.drawOn(c,pos_left,pos-95)

			data=[[Paragraph(u"Ciudad: %s-%s-%s"%(self.partner_id.state_id.name or ' ',self.partner_id.province_id.name or ' ',self.partner_id.district_id.name or ' '),p1_1)],]
			hTable=Table(data,colWidths=340,rowHeights=(15))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0),(-1,-1),1,colors.black)
				]))
			hTable.wrapOn(c,120,500)
			hTable.drawOn(c,pos_left,pos-110)

			data=[[Paragraph(u"Telefono: %s"%(self.partner_id.phone or ' '),p1_1)],]
			hTable=Table(data,colWidths=340,rowHeights=(15))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0),(-1,-1),1,colors.black)
				]))
			hTable.wrapOn(c,120,500)
			hTable.drawOn(c,pos_left,pos-125)


			data= [['Forma de Pago:'],
			['%s'%(self.payment_term_id.name or ' ')]]
			hTable=Table(data,colWidths=106,rowHeights=(15))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0),(-1,-1),1,colors.black),
				('FONT',(0,0),(-1,-1),'Calibri-Bold'),
				('FONTSIZE',(0,0),(-1,-1),8)
				]))
			
			hTable.wrapOn(c,120,500)
			hTable.drawOn(c,360,pos-65)

			data= [['Vendedor:'],
			['%s'%(self.user_id.name or ' ')]]
			hTable=Table(data,colWidths=106,rowHeights=(15))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0),(-1,-1),1,colors.black),
				('FONT',(0,0),(-1,-1),'Calibri-Bold'),
				('FONTSIZE',(0,0),(-1,-1),8)
				]))
			
			hTable.wrapOn(c,120,500)
			hTable.drawOn(c,360,pos-95)

			descuento_list = []
			for line in self.order_line:
				descuento   = str(line.discount)
				descuento_list.append(descuento)

			if len(descuento_list)==len(set(descuento_list)): 
				descuento_total = ''
			else:
				descuento_total = descuento_list[0]

			data= [['Dscto Alt:'],
			['%s'%(descuento_total or ' ')]]
			hTable=Table(data,colWidths=106,rowHeights=(15))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0),(-1,-1),1,colors.black),
				('FONT',(0,0),(-1,-1),'Calibri-Bold'),
				('FONTSIZE',(0,0),(-1,-1),8)
				]))
			
			hTable.wrapOn(c,120,500)
			hTable.drawOn(c,360,pos-125)

			data= [['Fecha Vcto:'],
			['%s'%(self.validity_date or ' ')]]
			hTable=Table(data,colWidths=106,rowHeights=(15))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0),(-1,-1),1,colors.black),
				('FONT',(0,0),(-1,-1),'Calibri-Bold'),
				('FONTSIZE',(0,0),(-1,-1),8)
				]))
			
			hTable.wrapOn(c,120,500)
			hTable.drawOn(c,466,pos-65)

			data= [['Codigo:'],
			['%s'%(self.user_id.partner_id.ref or ' ')]]
			hTable=Table(data,colWidths=106,rowHeights=(15))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0),(-1,-1),1,colors.black),
				('FONT',(0,0),(-1,-1),'Calibri-Bold'),
				('FONTSIZE',(0,0),(-1,-1),8)
				]))
			
			hTable.wrapOn(c,120,500)
			hTable.drawOn(c,466,pos-95)

			data= [['Moneda:'],
			['%s'%(self.pricelist_id.name or ' ')]]
			hTable=Table(data,colWidths=106,rowHeights=(15))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0),(-1,-1),1,colors.black),
				('FONT',(0,0),(-1,-1),'Calibri-Bold'),
				('FONTSIZE',(0,0),(-1,-1),8)
				]))
			
			hTable.wrapOn(c,120,500)
			hTable.drawOn(c,466,pos-125)

		header_table2(c,pos)


		def header_table3(c,pos):
			data=[[Paragraph(u"Codigo.",p1),Paragraph(u"Item.",p1),Paragraph(u"Item.",p1),Paragraph(u"Bodega U.M.",p1),Paragraph(u"Cantidad",p1),Paragraph(u"Precio Unit.",p1),Paragraph(u"Dscto",p1),Paragraph(u"Subtotal",p1),Paragraph(u"IVA %",p1)],]
			Table_lines=Table(data,colWidths=61,rowHeights=(20))
			Table_lines.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('SPAN',(2,-1),(1,-1)),
				('BOX',(0,0),(-1,-1),1,colors.black)
				]))
			Table_lines.wrapOn(c,120,500)
			Table_lines.drawOn(c,pos_left,pos-160)
		
		header_table3(c,pos)
		
		# self._cr.execute(self.get_query_1(),(self.start_date,self.end_date,))
		# results = self._cr.dictfetchall()
		#print(results)
		lista =[]
		precios_s_descuento =[]
		for line in self.order_line:
			codigo_producto   = str(line.product_id.default_code or ' ')
			producto   = str(line.product_id.name or ' ')
			cantidad   = str(line.product_uom_qty or ' ')
			precio   = str(line.price_unit or ' ')
			descuento   =  str( '% ' +str(line.discount) or ' ')
			suntotal   = str(line.price_subtotal or ' ')


			iva   =  str('% '+str(line.tax_id.amount) or ' ')

			precios_s_descuento.append(line.product_uom_qty*line.price_unit)

			data = [[Paragraph(codigo_producto,p2_1),Paragraph(producto,p2_1),Paragraph(producto,p2_1),Paragraph(self.warehouse_id.name,p2_1),Paragraph(cantidad,p2_1),Paragraph(precio,p2_1),Paragraph(descuento,p2_1),Paragraph(suntotal,p2_1),Paragraph(iva,p2_1)],]
			t=Table(data,colWidths=61,rowHeights=(20))
			t.setStyle(TableStyle([
			('VALIGN',(0,0),(-1,-1),'TOP'),
			('SPAN',(2,-1),(1,-1)),
			]))
			w_table,h_table=t.wrap(0,0)
			t.wrapOn(c,120,500)
			pos-=h_table
			
			lista.append(1)
			
			if pos < bottom:
				c.showPage()
				pos = hPage-90
				header_table1(c,pos)
				header_table2(c,pos)
				header_table3(c,pos)
				pos-=h_table
				t.drawOn(c,pos_left,pos-170)
			else: 
				t.drawOn(c,pos_left,pos-170)
		pos-=3
		

		def header_table4(c,pos):

			data=[[Paragraph(u"Total Bruto.",p1),Paragraph(u"Descuento.",p1),Paragraph(u"Subtotal",p1),Paragraph(u"Vir Impuestos",p1),Paragraph(u"Total",p1)],]
			Table_lines=Table(data,colWidths=110.4,rowHeights=(15))
			Table_lines.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('GRID',(0,0),(-1,-1),1,colors.black),
				('BOX',(0,0),(-1,-1),1,colors.black)
				]))
			Table_lines.wrapOn(c,120,500)
			Table_lines.drawOn(c,pos_left,(pos-170)-70)

			descuento = round((sum(precios_s_descuento)-float(self.amount_untaxed)),2)

			moneda=str(self.currency_id.symbol)

			data=[[Paragraph(moneda + str(sum(precios_s_descuento)) or '',p2_1),Paragraph(moneda + str(descuento)or '',p2_1),Paragraph(moneda + str(self.amount_untaxed),p2_1),Paragraph(moneda + str(self.amount_tax),p2_1),Paragraph(moneda + str(self.amount_total),p2_1)],]
			Table_lines=Table(data,colWidths=110.4,rowHeights=(15))
			Table_lines.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('GRID',(0,0),(-1,-1),1,colors.black),
				('BOX',(0,0),(-1,-1),1,colors.black)
				]))
			Table_lines.wrapOn(c,120,500)
			Table_lines.drawOn(c,pos_left,(pos-170)-85)

			
			partner_confirm = self.env['res.users'].sudo().browse([self.partner_confirm_id]).partner_id.name

			data2=[[Paragraph(str(self.create_uid.name or ' '),TF_1),Paragraph(str(partner_confirm or ''),TF_1),Paragraph(str(self.partner_id.name or ''),TF_1)],]
			Table_lines2=Table(data2,colWidths=184,rowHeights=(15))
			Table_lines2.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				]))
			Table_lines2.wrapOn(c,120,500)
			Table_lines2.drawOn(c,pos_left,(pos-200)-100)

			data2=[[Paragraph("ELABORADO",TF),Paragraph("APROBADO",TF),Paragraph("RECIBIDO",TF)],]
			Table_lines2=Table(data2,colWidths=184,rowHeights=(15))
			Table_lines2.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				]))
			Table_lines2.wrapOn(c,120,500)
			Table_lines2.drawOn(c,pos_left,(pos-200)-130)
			
			
			c.setFont("Calibri-Bold", 10)
			c.drawString(20,(pos-170)-190, "CUENTAS BANCARIAS TOSCANA IMPORT S.A.C.")
			
			src_path = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')
			cuentas=src_path+'/Cuentas_bancarias.JPG'
			cuentas_ban=ImageReader(cuentas)
			c.drawImage(cuentas_ban,20,(pos-170)-300,width=225,height=100,mask='auto')

			c.setFont("Calibri-Bold", 10)
			c.drawString(20,(pos-170)-315, "LA COTIZACION ES VALIDA DESDE SU EMISION HASTA EL " + str(self.validity_date))

		header_table4(c,pos)

		c.showPage()
		c.setTitle(file_name)
		c.setSubject('Reportes')
		c.save()
		return self.env['report.it'].export_file(path, file_name)

	# def get_query_1(self):
	# 	return """
		
	# 	"""
