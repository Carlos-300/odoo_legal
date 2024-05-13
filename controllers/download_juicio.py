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

ESTADOS_PRIMERA_CIVIL = [('discusion_civil','Discusión'),
                        ('prueba_civil','Prueba'),
                        ('sentencia_civil','Sentencia 1era instancia'),
                        ('recursos_civil','Recursos')]

ESTADOS_PRIMERA_MONITORIO = [('audiencia_monitorio','Audiencia Unica'),
                            ('recursos_monitorio','Recursos')]

ESTADOS_PRIMERA_APELACION = [('preparacion','Audiencia de Preparación '),
                        ('audiencia_apelacion','Audiencia de Juicio Oral'),
                        ('recursos_apelacion','Recursos')]

ESTADOS_PRIMERA_JPL = [('audiencia_jpl','Audiencia'),
                        ('sentencia_jpl','Sentencia '),
                        ('recursos_jpl','Recursos')]

ESTADOS_SEGUNDA_INSTANCIA = [('ingreso_recurso','Ingreso de Recurso'),
                            ('auto_relacion','Autos en relación'),
                            ('inclusion_tabla','Inclusión a la Tabla'),
                            ('sentencia_segunda','Sentencia 2da instancia'),
                            ('recursos_segunda','Recursos')]

ESTADOS_CORTE_SUPREMA = [('ingreso_recurso_corte','Ingreso de Recurso'),
                        ('auto_relacion_corte','Autos en relación'),
                        ('inclusion_tabla_corte','Inclusión a la Tabla'),
                        ('sentencia_final','Sentencia definitiva')]





class ReportAdjuntos(http.Controller):

    @http.route(['/legal_juicio/print_juicio/<int:report_id>/'], type='http', auth="user")
    @serialize_exception
    def get_pdf_data(self , report_id, **post):
        """
        Obtenemos todos los documentos adjuntados del elemento seleccionado
            Generamos una portada por instancia y se entregan todos los elementos en un documento
        """
        report_obj = request.env['legal.juicio'] 
        report = report_obj.sudo().browse(report_id) # model del juicio con su id
        report_adjuntos = request.env['legal.juicio.adjuntos'].sudo()
        report_tablas = request.env['legal.juicio.tablas'].sudo()
         

        verificador = report_adjuntos.search([('juicio_id','=',report_id)])
        if len(verificador) == 0:
            raise UserError("No se encontraron archivos disponibles para generar un documento.")
        
        merger = PdfFileMerger()
        temp_dir = tempfile.TemporaryDirectory()
        # todos los estados de los juicios
        state_primera= None
        segunda_all = None
        corte_all = None
        # datos actuales del juicio
        instancias1 = None
        instancias2 = None
        instancias3 = None

        #bandera me permite saber que estado tiene datos
        if report.bandera_primera:
            if report.tipo_de_juicio == 'civil':
                state_primera = ESTADOS_PRIMERA_CIVIL   
                instancias1 = {("state_actual_primera",report.state_primera_civil), 
                               ("sentencia_cumplida_primera",report.cumplir_sentencia),
                               ("adjunto_conciliacion_primera",report.conciliacion_primera)}

            elif report.tipo_de_juicio == 'laboral':
                if report.tipo_laboral == 'monitorios':
                    state_primera =ESTADOS_PRIMERA_MONITORIO
                    instancias1 = {("state_actual_primera",report.state_primera_monitorio), 
                                    ("sentencia_cumplida_primera",report.cumplir_sentencia_monitorio),
                                    ("adjunto_conciliacion_primera",report.conciliacion_primera)}
                else:
                    state_primera = ESTADOS_PRIMERA_APELACION
                    instancias1 = {("state_actual_primera",report.state_primera_apelacion), 
                                    ("sentencia_cumplida_primera",report.cumplir_sentencia_oral),
                                    ("adjunto_conciliacion_primera",report.conciliacion_primera)}
            elif report.tipo_de_juicio == 'JPL':
                state_primera =ESTADOS_PRIMERA_JPL
                instancias1 = {("state_actual_primera",report.state_primera_jpl), 
                                ("sentencia_cumplida_primera",report.cumplir_sentencia_jpl),
                                ("adjunto_conciliacion_primera",report.conciliacion_primera)}

        if report.bandera_segunda:
            segunda_all = ESTADOS_SEGUNDA_INSTANCIA
            instancias2 = {("state_actual_segunda",report.state_segunda), 
                            ("sentencia_cumplida_segunda",report.cumplir_sentencia_segunda),
                            ("adjunto_conciliacion_segunda",report.conciliacion_segunda)}
        if report.bandera_cortesuprema:
            corte_all = ESTADOS_CORTE_SUPREMA 
            instancias3 = {("state_actual_corte",report.state_corte), 
                            ("sentencia_cumplida_corte",report.cumplir_sentencia_corte),
                            ("adjunto_conciliacion_corte",report.conciliacion_corte)}
        
        bandera = False #bandera para salir del for
        bandera_conciliacion = " " # en caso de tener una conciliacion 
        contador = 0 
  
        for juicio_state, instancia in zip([state_primera, segunda_all , corte_all],[instancias1,instancias2,instancias3]):
            if juicio_state != None and not bandera :
                contador+=1 
                for xprimera in juicio_state:
                    dato1 , dato2 = xprimera 
                    stop = self.stop_pdf(instancia,dato1)
                    bandera_conciliacion = stop
                    adjuntos =  report_adjuntos.search([('estado_ejecutado', '=', dato1),('juicio_id','=',report_id)],order="posicion_adj asc")
                    for x in adjuntos:
                        print(x.posicion_adj)
                    if adjuntos:
                        documentacion_state = self.agregar_doc(adjuntos,dato2,contador)
                        read_pdf = PdfFileReader(documentacion_state)
                        merger.append(read_pdf)

                    elif "tabla" in dato1:
                        if contador == 2:
                            tipo_tabla = "inclusion_tabla"
                        else:
                            tipo_tabla = "inclusion_tabla_corte"
                        #las tablas se pueden agregar despues de pasar su propio estado pero solo en las corte de apelaciones y la suprema
                        adj_tablas =  report_tablas.search([('tabla_estate','=', tipo_tabla),('juicio_id','=',report_id)],order="posicion_adj asc")
                        if adj_tablas:  
                            documentacion_state = self.agregar_doc(adj_tablas,dato2,contador)
                            read_pdf = PdfFileReader(documentacion_state)
                            merger.append(read_pdf)

                    if "pass" not in stop :
                        bandera = True
                        break
                
            else:
                break
            
        #agregar al final la conciliacion
        if "adjunto" in bandera_conciliacion:
            if contador == 1:
                adjunto_llamar = report.adjunto_conciliacion_primera
            elif contador == 2: 
                adjunto_llamar = report.adjunto_conciliacion_segunda
            elif contador == 3: 
                adjunto_llamar = report.adjunto_conciliacion_corte

            if adjunto_llamar:
                doc_title = self.create_page_title("Conciliación",contador)
                read_title = PdfFileReader(doc_title)
                merger.append(read_title)
                with io.BytesIO(base64.b64decode(adjunto_llamar)) as f: 
                    read_conciliacion = PdfFileReader(f)
                    merger.append(read_conciliacion)
           

        filename = f"Adjuntos-{report.name}.pdf"
        merger.write(temp_dir.name+"/"+filename)
        merger.close()
        pdf_file = open(temp_dir.name+"/"+filename,'rb')
        pdfhttpheaders = [('Content-Disposition', content_disposition(filename)),
                            ('Content-Type', 'application/pdf')]
        return request.make_response(pdf_file, headers=pdfhttpheaders)

    def stop_pdf(self,instancia,states):
        """
        validamos las posibles salidas como sentencia , conciliacion , state
        """
        for x in instancia:
            if "adjunto" in x[0]:
                res_conciliacion = x
            elif "state" in x[0]:
                res_state = x
            elif "sentencia" in x[0]:
                res_sentencia = x 

        if res_sentencia[1] and res_state[1] == states: # teniendo la sentencia pongo bandera
            stop = "="
        elif res_conciliacion[1] and res_state[1] == states: # teniendo conciliacion pongo bandera
            stop = res_conciliacion[0]
        elif res_state[1] == states and "recursos" not in res_state[1]:#llego al estado actual pongo bandera
            stop = "="
        else:
            stop = "pass"
        
        return stop


    def create_page_title(self,texto, contador):
        """
        Generar un documento que sirve como portada de cada estado
        """
        # Definir el título según el contador
        if contador == 1:
            titulo = "Primera Instancia"
        elif contador == 2:
            titulo = "Corte de Apelaciones"
        elif contador == 3:
            titulo = "Corte Suprema"
        else:
            titulo = "Título Desconocido"

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
        canva.setFont("Times-Bold",20)
        canva.drawString(x_position,y_position-50,texto )
        canva.save()
        
        return pdf_output_path
    

    def agregar_doc(self, documentos, dato2, contador):
        """
        Generamos el documento que obtiene la instancia entera 
        """
        temp_output = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        pdf_output_path = temp_output.name
        merge =  PdfFileMerger()
        #agrego portada con la instancia y la corte 
        doc_title = self.create_page_title(str(dato2),contador)
        merge.append(doc_title)
        #se agregan los docuentos despues de la portada
        for doc in documentos:
            with io.BytesIO(base64.b64decode(doc.adjunto)) as f: 
                read =  PdfFileReader(f)
                merge.append(read)

        merge.write(pdf_output_path)
        merge.close()
        return pdf_output_path
    