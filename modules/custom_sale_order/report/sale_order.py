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
pdfmetrics.registerFont(TTFont('Calibri', 'Calibri.ttf'))
pdfmetrics.registerFont(TTFont('Calibri-Bold', 'CalibriBold.ttf'))
p1 = ParagraphStyle('p1',alignment=TA_CENTER,fontSize=8,fontName="Calibri-Bold")
p1_1 = ParagraphStyle('p1',alignment=TA_LEFT,fontSize=8,fontName="Calibri-Bold")
p2 = ParagraphStyle('p2',alignment=TA_LEFT,fontSize=7,fontName="Calibri")
p2_1 = ParagraphStyle('p2',alignment=TA_CENTER,fontSize=7,fontName="Calibri")
p3 = ParagraphStyle('p3',alignment=TA_LEFT,fontSize=10,fontName="Calibri")
p4 = ParagraphStyle('p4',alignment=TA_RIGHT,fontSize=10,fontName="Calibri")
p5 = ParagraphStyle('p5',alignment=TA_RIGHT,fontSize=10,fontName="Calibri-Bold")
p6 = ParagraphStyle('p6',alignment=TA_LEFT,fontSize=10,fontName="Calibri-Bold")
p7 = ParagraphStyle('p7',alignment=TA_LEFT,fontSize=11,fontName="Calibri")
style = getSampleStyleSheet()["Normal"]
gray = colors.Color(red=(200.0/255),green=(200.0/255),blue=(200.0/255))


class SaleOrder(models.Model):
	_inherit='sale.order'

	def build_report_pdf(self):
		if self.state == 'draft':
			name_state = u'COTIZACIÓN'
		if self.state == 'sale':
			name_state = u'ORDEN DE VENTA'
		if self.state != 'sale' and self.state != 'draft':
			name_state = u'Presupuesto-Pedido'

		path = self.env['res.config.settings'].search([('path_reports','!=',False)],limit=1).path_reports
		now = fields.Datetime.context_timestamp(self,datetime.now())
		name = name_state
		file_name = u'S.0. %s %s.pdf'%(name,str(now)[:19].replace(':','_'))
		if path == False:
			raise UserError('Ingrese a Configuración > Reportes > Path y verifique que tiene una ruta de descarga')
		path += file_name
		c = canvas.Canvas(path , pagesize=(595,842))
		pos = hPage - 90
		

		def header_table1(c,pos):
			src_path = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')
			header_path=src_path+'/Toscana_logo.JPG'
			header_logo=ImageReader(header_path)
			c.drawImage(header_logo,20,pos-10,width=230,height=60,mask='auto')

			data= [[name_state],
			['Numero: %s'%(self.name)],
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
			data=[[Paragraph(u"Cliente:",p1_1),Paragraph(u"%s"%(self.partner_id.name or ' '),p2)],]
			hTable=Table(data,colWidths=170,rowHeights=(15))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0),(-1,-1),1,colors.black)
				]))
			hTable.wrapOn(c,120,500)
			hTable.drawOn(c,pos_left,pos-50)

			data=[[Paragraph(u"Contacto:",p1_1),Paragraph(u"%s"%(self.partner_order_id.name or ' '),p2)],]
			hTable=Table(data,colWidths=170,rowHeights=(15))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0),(-1,-1),1,colors.black)
				]))
			hTable.wrapOn(c,120,500)
			hTable.drawOn(c,pos_left,pos-65)

			data=[[Paragraph(u"DNI O RUC:",p1_1),Paragraph(u"%s"%(self.partner_id.vat or ' '),p2),Paragraph(u"Codigo:",p1_1),Paragraph(u"%s"%(self.partner_id.ref or ' '),p2)],]
			hTable=Table(data,colWidths=85,rowHeights=(15))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0),(-1,-1),1,colors.black)
				]))
			hTable.wrapOn(c,120,500)
			hTable.drawOn(c,pos_left,pos-80)

			data=[[Paragraph(u"Dirección:",p1_1),Paragraph(u"%s"%(self.partner_id.street or ' '),p2)],]
			hTable=Table(data,colWidths=170,rowHeights=(15))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0),(-1,-1),1,colors.black)
				]))
			hTable.wrapOn(c,120,500)
			hTable.drawOn(c,pos_left,pos-95)

			data=[[Paragraph(u"Ciudad:",p1_1),Paragraph(u"%s-%s-%s"%(self.partner_id.state_id.name or ' ',self.partner_id.province_id.name or ' ',self.partner_id.district_id.name or ' '),p2)],]
			hTable=Table(data,colWidths=170,rowHeights=(15))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0),(-1,-1),1,colors.black)
				]))
			hTable.wrapOn(c,120,500)
			hTable.drawOn(c,pos_left,pos-110)

			data=[[Paragraph(u"Telefono:",p1_1),Paragraph(u"%s"%(self.partner_id.phone or ' '),p2)],]
			hTable=Table(data,colWidths=170,rowHeights=(15))
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
			['%s'%(self.user_id.name)]]
			hTable=Table(data,colWidths=106,rowHeights=(15))
			hTable.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0),(-1,-1),1,colors.black),
				('FONT',(0,0),(-1,-1),'Calibri-Bold'),
				('FONTSIZE',(0,0),(-1,-1),8)
				]))
			
			hTable.wrapOn(c,120,500)
			hTable.drawOn(c,360,pos-95)

			data= [['Dscto Alt:'],
			['%s'%(self.date_order)]]
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
			['%s'%(self.validity_date)]]
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
			['%s'%(self.user_id.partner_id.ref)]]
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
			['%s'%(self.pricelist_id.name)]]
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
			data=[[Paragraph(u"Codigo.",p1),Paragraph(u"Item.",p1),Paragraph(u"Bodega U.M.",p1),Paragraph(u"Cantidad",p1),Paragraph(u"Precio Unit.",p1),Paragraph(u"Dscto",p1),Paragraph(u"Subtotal",p1),Paragraph(u"IVA %",p1)],]
			Table_lines=Table(data,colWidths=69,rowHeights=(20))
			Table_lines.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0),(-1,-1),1,colors.black)
				]))
			Table_lines.wrapOn(c,120,500)
			Table_lines.drawOn(c,pos_left,pos-160)
		
		header_table3(c,pos)
		
		# self._cr.execute(self.get_query_1(),(self.start_date,self.end_date,))
		# results = self._cr.dictfetchall()
		#print(results)
		lista =[]
		for line in self.order_line:
			codigo_producto   = str(line.product_id.default_code or ' ')
			producto   = str(line.product_id.name or ' ')
			cantidad   = str(line.product_uom_qty or ' ')
			precio   = str(line.price_unit or ' ')
			# descuento   = str(line.discount or ' ')
			suntotal   = str(line.price_subtotal or ' ')
			iva   = str(line.tax_id.name or ' ')

			data = [[Paragraph(codigo_producto,p2_1),Paragraph(producto,p2_1),Paragraph(self.warehouse_id.name,p2_1),Paragraph(cantidad,p2_1),Paragraph(precio,p2_1),Paragraph(u'descuento',p2_1),Paragraph(suntotal,p2_1),Paragraph(iva,p2_1)],]
			t=Table(data,colWidths=69,rowHeights=(20))
			t.setStyle(TableStyle([
			('VALIGN',(0,0),(-1,-1),'TOP'),
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
				('BOX',(0,0),(-1,-1),1,colors.black)
				]))
			Table_lines.wrapOn(c,120,500)
			Table_lines.drawOn(c,pos_left,(pos-170)-40)

			data=[[Paragraph(str(self.amount_total),p2_1),Paragraph(u"Descuento.",p2_1),Paragraph(str(self.amount_untaxed),p2_1),Paragraph(str(self.amount_tax),p2_1),Paragraph(str(self.amount_total),p2_1)],]
			Table_lines=Table(data,colWidths=110.4,rowHeights=(15))
			Table_lines.setStyle(TableStyle([
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('BOX',(0,0),(-1,-1),1,colors.black)
				]))
			Table_lines.wrapOn(c,120,500)
			Table_lines.drawOn(c,pos_left,(pos-170)-55)

			
			c.setFont("Calibri", 10)
			c.drawString(90,(pos-170)-110, str(self.create_uid.name))
			c.setFont("Calibri-Bold", 10)
			c.drawString(90,(pos-170)-130, "ELABORADO")

			partner_confirm = self.env['res.users'].sudo().browse([self.partner_confirm_id]).partner_id.name
			c.setFont("Calibri", 10)
			c.drawString(260,(pos-170)-110, str(partner_confirm or ''))
			c.setFont("Calibri-Bold", 10)
			c.drawString(260,(pos-170)-130, "APROBADO")

			c.setFont("Calibri", 10)
			c.drawString(420,(pos-170)-110, str(self.partner_id.name))
			c.setFont("Calibri-Bold", 10)
			c.drawString(420,(pos-170)-130, "RECIBIDO")

			
			
			c.setFont("Calibri-Bold", 10)
			c.drawString(20,(pos-170)-185, "CUENTAS BANCARIAS TOSCANA IMPORT S.A.C.")
			
			src_path = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')
			cuentas=src_path+'/Cuentas_bancarias.JPG'
			cuentas_ban=ImageReader(cuentas)
			c.drawImage(cuentas_ban,20,(pos-170)-350,width=325,height=150,mask='auto')

			c.setFont("Calibri-Bold", 10)
			c.drawString(20,(pos-170)-370, "LA COTIZACIÓN ES VALIDA 14 DIAS DE HABERSE EMITIDO")

		header_table4(c,pos)

		c.showPage()
		c.setTitle(file_name)
		c.setSubject('Reportes')
		c.save()
		with open(path,'rb') as file:
			export = self.env['export.file.manager'].create({
				'file_name': file_name,
				'content_type':'application/pdf',
				'file': base64.b64encode(file.read()),	
			})
		return export.export_file(clear=True,path=path)

	# def get_query_1(self):
	# 	return """
		
	# 	"""
