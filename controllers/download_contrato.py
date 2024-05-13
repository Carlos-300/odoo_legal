# -*- coding: utf-8 -*-
# Created by German Contreras at 30-08-23

import logging
from odoo.exceptions import UserError
import base64
import io
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import black
from reportlab.platypus import  Paragraph
from reportlab.pdfgen import canvas
from odoo import http, _
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
import tempfile
from odoo.http import request, content_disposition
from odoo.addons.web.controllers.main import serialize_exception

_logger = logging.getLogger(__name__)



class ReportAdjuntosContratos(http.Controller):

    @http.route(['/legal_contrato/print_contrato/<int:report_id>/<string:salida_id>/'], type='http', auth="user")
    @serialize_exception
    def get_pdf_data(self , report_id, salida_id ,**post):
        """
        Se agregan todos los contratos a un solo archivo.

        Segun la opcion seleccionada antes se pueden sacar los siguentes archivos

        todo = Todos los adjuntos disponibles dentro de  este elemento
        medio = solo contrato firmado y sus documentos extras
        bajo =  solo los contratos que estaban en los estados primordiales (borrador , revisón , firmado)

        """

        report_obj = request.env['legal.contrato'].sudo().browse(report_id)
        report_adjuntos = request.env['legal.contrato.adjuntos.extras'].sudo().search([('contrato_id','=',report_obj.id)], order='position_obj asc')
        merge =  PdfFileMerger()
        
        
        if salida_id == "todo" or salida_id == "bajo":
            state_list =['borrador','revision','firmados']
            lista_doc = [report_obj.contrato_borrador, report_obj.contrato_revision, report_obj.contrato_firmados]
        elif salida_id == "medio":
            state_list =['firmados']
            lista_doc = [report_obj.contrato_firmados]

        for doc, state in zip(lista_doc,state_list):
            portada =  self.create_page_title(state)
            read_portada = PdfFileReader(portada)
            merge.append(read_portada)
            with io.BytesIO(base64.b64decode(doc)) as f: 
                read =  PdfFileReader(f)
                merge.append(read)
            if report_obj.state == state:
                break
        else:
            if len(report_adjuntos)>0 and salida_id != "bajo":
                portada =  self.create_page_title(state= False)
                read_portada = PdfFileReader(portada)
                merge.append(read_portada)
                for adj in report_adjuntos:
                    with io.BytesIO(base64.b64decode(adj.adjunto)) as f: 
                        read =  PdfFileReader(f)
                        merge.append(read)
                        
                
        temp_dir = tempfile.TemporaryDirectory()
        filename="Adjuntos_contrato.pdf"

        merge.write(temp_dir.name+"/"+filename)
        merge.close()
        pdf_file = open(temp_dir.name+"/"+filename,'rb')
        pdfhttpheaders = [('Content-Disposition', content_disposition(filename)),
                            ('Content-Type', 'application/pdf')]
        return request.make_response(pdf_file, headers=pdfhttpheaders)
        
                    
        
    def create_page_title(self,state):
        """
        Generar un documento que sirve como portada de cada estado
        """
        # Definir el título según el contador
        if state == "borrador":
            titulo = "Contrato en Estado Borrador"
        elif state == "revision":
            titulo = "Contrato en Estado Revisión"
        elif state == "firmados":
            titulo = "Contrato en Estado Firmado"
        else:
            titulo = "Documentos Extras"
            
        # Crear un PDF temporal
        temp_output = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        pdf_output_path = temp_output.name
        # Generar el documento PDF
        canva = canvas.Canvas(pdf_output_path, pagesize=letter )
        width, height = letter

        x_position =  ((width /2)/2)
        y_position = height / 2

        canva.setFont("Times-Bold",26)
        canva.drawString(x_position,y_position,titulo )
      
        canva.save()
        
        return pdf_output_path
    
