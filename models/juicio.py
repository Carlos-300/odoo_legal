# -*- coding: utf-8 -*-
import tempfile
from odoo import models,fields,api 
from odoo.exceptions import UserError ,ValidationError
import base64
import datetime
import io,os
import re
from odoo import http, _
from PyPDF2 import PdfFileReader, PdfFileMerger
from odoo.http import HttpRequest, request, content_disposition


ESTADOS_JUCIOS = [('borrador','Borrador'),
                    ('primera','Primera Instancia'),
                    ('segunda','Corte de Apelaciones'),
                    ('cortesuprema','Corte Suprema'),
                    ('cumplimiento','Cumplimiento'),
                    ('finalizado','Finalizado'),
                    ('cancelado','Cancelado')]

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

TIPO_DE_JUICIO = [('civil','Juicio Civil'),
                  ('laboral','Juicio Laboral'),
                  ('JPL','Juicio Juzgado De Policía Local (JPL).')]

TIPO_LABORAL = [('monitorios','Monitorios'),
                ('apelacion','Apelación General')]

PETICION = [('demandate','Demandate'),
            ('demandado','Demandado')]






class ControlJuicioCivil(models.Model): 
    _name = "legal.juicio"
    _inherit = ['mail.thread']

    #report bandera estados completados
    
    bandera_primera = fields.Boolean("bandera primera",copy= False, default=False)
    bandera_segunda = fields.Boolean("bandera segunda",copy= False, default=False)
    bandera_cortesuprema = fields.Boolean("bandera corte",copy= False, default=False)
        ### Adjuntos ###
    #primera instancia
    adj_discusion_civil_ids =  fields.One2many("legal.juicio.adjuntos","juicio_id" ,string="Adjuntos", domain=[('estado_ejecutado','=','discusion_civil')], default_order="posicion_adj asc")
    adj_prueba_civil_ids =  fields.One2many("legal.juicio.adjuntos","juicio_id" ,string="Adjuntos",domain=[('estado_ejecutado','=','prueba_civil')], default_order="posicion_adj asc")
    adj_sentencia_civil_ids =  fields.One2many("legal.juicio.adjuntos","juicio_id" ,string="Adjuntos", domain=[('estado_ejecutado','=','sentencia_civil')], default_order="posicion_adj asc")
    adj_recursos_civil_ids =  fields.One2many("legal.juicio.adjuntos","juicio_id" ,string="Adjuntos",domain=[('estado_ejecutado','=','recursos_civil')], default_order="posicion_adj asc")
    
    adj_audiencia_monitorio_ids =  fields.One2many("legal.juicio.adjuntos","juicio_id" ,string="Adjuntos", domain=[('estado_ejecutado','=','audiencia_monitorio')], default_order="posicion_adj asc")
    adj_recursos_monitorio_ids =  fields.One2many("legal.juicio.adjuntos","juicio_id" ,string="Adjuntos",domain=[('estado_ejecutado','=','recursos_monitorio')], default_order="posicion_adj asc")
    
    adj_preparacion_ids =  fields.One2many("legal.juicio.adjuntos","juicio_id" ,string="Adjuntos", domain=[('estado_ejecutado','=','preparacion')], default_order="posicion_adj asc")
    adj_audiencia_apelacion_ids =  fields.One2many("legal.juicio.adjuntos","juicio_id" ,string="Adjuntos",domain=[('estado_ejecutado','=','audiencia_apelacion')], default_order="posicion_adj asc")
    adj_recursos_apelacion_ids =  fields.One2many("legal.juicio.adjuntos","juicio_id" ,string="Adjuntos", domain=[('estado_ejecutado','=','recursos_apelacion')], default_order="posicion_adj asc")
   
    adj_audiencia_jpl_ids =  fields.One2many("legal.juicio.adjuntos","juicio_id" ,string="Adjuntos",domain=[('estado_ejecutado','=','audiencia_jpl')], default_order="posicion_adj asc")
    adj_sentencia_jpl_ids =  fields.One2many("legal.juicio.adjuntos","juicio_id" ,string="Adjuntos", domain=[('estado_ejecutado','=','sentencia_jpl')], default_order="posicion_adj asc")
    adj_recursos_jpl_ids =  fields.One2many("legal.juicio.adjuntos","juicio_id" ,string="Adjuntos",domain=[('estado_ejecutado','=','recursos_jpl')], default_order="posicion_adj asc")
    
    #Corte de Apelaciones
    adj_ingreso_recurso_ids =  fields.One2many("legal.juicio.adjuntos","juicio_id" ,string="Adjuntos", domain=[('estado_ejecutado','=','ingreso_recurso')], default_order="posicion_adj asc")
    adj_auto_relacion_ids =  fields.One2many("legal.juicio.adjuntos","juicio_id" ,string="Adjuntos",domain=[('estado_ejecutado','=','auto_relacion')], default_order="posicion_adj asc")
    adj_inclusion_tabla_ids =  fields.One2many("legal.juicio.tablas","juicio_id" ,string="Adjuntos", domain=[('tabla_estate','=','inclusion_tabla')], default_order="posicion_adj asc")
    adj_sentencia_segunda_ids =  fields.One2many("legal.juicio.adjuntos","juicio_id" ,string="Adjuntos",domain=[('estado_ejecutado','=','sentencia_segunda')], default_order="posicion_adj asc")
    adj_recursos_segunda_ids =  fields.One2many("legal.juicio.adjuntos","juicio_id" ,string="Adjuntos",domain=[('estado_ejecutado','=','recursos_segunda')], default_order="posicion_adj asc")
                
    #Corte Suprema            
    adj_ingreso_recurso_corte_ids =  fields.One2many("legal.juicio.adjuntos","juicio_id" ,string="Adjuntos", domain=[('estado_ejecutado','=','ingreso_recurso_corte')], default_order="posicion_adj asc")
    adj_auto_relacion_corte_ids =  fields.One2many("legal.juicio.adjuntos","juicio_id" ,string="Adjuntos",domain=[('estado_ejecutado','=','auto_relacion_corte')], default_order="posicion_adj asc")
    adj_inclusion_tabla_corte_ids =  fields.One2many("legal.juicio.tablas","juicio_id" ,string="Adjuntos", domain=[('tabla_estate','=','inclusion_tabla_corte')], default_order="posicion_adj asc")
    adj_sentencia_final_ids =  fields.One2many("legal.juicio.adjuntos","juicio_id" ,string="Adjuntos",domain=[('estado_ejecutado','=','sentencia_final')], default_order="posicion_adj asc")
                

            ### Comentarios ###
    # ---- Primera Instancia -----
    # -- Civil
    text_discusion_civil_ids =  fields.One2many("legal.juicio.comentarios","juicio_id", size=500 ,string="Comentarios",domain=[('estado_instancia','=','discusion_civil')], default_order="create_date asc")
    text_prueba_civil_ids =  fields.One2many("legal.juicio.comentarios","juicio_id", size=500 ,string="Comentarios",domain=[('estado_instancia','=','prueba_civil')], default_order="create_date asc")
    text_sentencia_civil_ids =  fields.One2many("legal.juicio.comentarios","juicio_id", size=500 ,string="Comentarios",domain=[('estado_instancia','=','sentencia_civil')], default_order="create_date asc")
    text_recursos_civil_ids =  fields.One2many("legal.juicio.comentarios","juicio_id", size=500 ,string="Comentarios",domain=[('estado_instancia','=','recursos_civil')], default_order="create_date asc")

    # -- Monitorios
    text_audiencia_monitorio_ids = fields.One2many("legal.juicio.comentarios","juicio_id", size=500 ,string="Comentarios",domain=[('estado_instancia','=','audiencia_monitorio')], default_order="create_date asc")
    text_recursos_monitorio_ids = fields.One2many("legal.juicio.comentarios","juicio_id", size=500 ,string="Comentarios",domain=[('estado_instancia','=','recursos_monitorio')], default_order="create_date asc")
    
    # -- Apelaciones 
    text_preparacion_apelacion_ids = fields.One2many("legal.juicio.comentarios","juicio_id", size=500 ,string="Comentarios",domain=[('estado_instancia','=','preparacion')], default_order="create_date asc")
    text_audiencia_apelacion_ids = fields.One2many("legal.juicio.comentarios","juicio_id", size=500 ,string="Comentarios",domain=[('estado_instancia','=','audiencia_apelacion')], default_order="create_date asc")
    text_recursos_apelacion_ids = fields.One2many("legal.juicio.comentarios","juicio_id", size=500 ,string="Comentarios",domain=[('estado_instancia','=','recursos_apelacion')], default_order="create_date asc")

    # --JPL 
    text_audiencia_jpl_ids = fields.One2many("legal.juicio.comentarios","juicio_id", size=500 ,string="Comentarios",domain=[('estado_instancia','=','audiencia_jpl')], default_order="create_date asc")
    text_sentencia_jpl_ids = fields.One2many("legal.juicio.comentarios","juicio_id", size=500 ,string="Comentarios",domain=[('estado_instancia','=','sentencia_jpl')], default_order="create_date asc")
    text_recursos_jpl_ids = fields.One2many("legal.juicio.comentarios","juicio_id", size=500 ,string="Comentarios",domain=[('estado_instancia','=','recursos_jpl')], default_order="create_date asc")
   
    # ---- Corte de Apelaciones -----
    text_ingreso_segunda_ids = fields.One2many("legal.juicio.comentarios","juicio_id", size=500 ,string="Comentarios",domain=[('estado_instancia','=','ingreso_recurso')], default_order="create_date asc")
    text_auto_relacion_segunda_ids = fields.One2many("legal.juicio.comentarios","juicio_id", size=500 ,string="Comentarios",domain=[('estado_instancia','=','auto_relacion')], default_order="create_date asc")
    text_inclusion_tabla_segunda_ids = fields.One2many("legal.juicio.comentarios","juicio_id", size=500 ,string="Comentarios",domain=[('estado_instancia','=','inclusion_tabla')], default_order="create_date asc")
    text_sentencia_segunda_ids = fields.One2many("legal.juicio.comentarios","juicio_id", size=500 ,string="Comentarios",domain=[('estado_instancia','=','sentencia_segunda')], default_order="create_date asc")
    text_recursos_segunda_ids = fields.One2many("legal.juicio.comentarios","juicio_id", size=500 ,string="Comentarios",domain=[('estado_instancia','=','recursos_segunda')], default_order="create_date asc")
 

    # ----- Corte Suprema -----
    text_ingreso_recurso_corte_ids = fields.One2many("legal.juicio.comentarios","juicio_id", size=500 ,string="Comentarios",domain=[('estado_instancia','=','ingreso_recurso_corte')], default_order="create_date asc")
    text_auto_relacion_corte_ids = fields.One2many("legal.juicio.comentarios","juicio_id", size=500 ,string="Comentarios",domain=[('estado_instancia','=','auto_relacion_corte')], default_order="create_date asc")
    text_inclusion_tabla_corte_ids = fields.One2many("legal.juicio.comentarios","juicio_id", size=500 ,string="Comentarios",domain=[('estado_instancia','=','inclusion_tabla_corte')], default_order="create_date asc")
    text_sentencia_final_ids = fields.One2many("legal.juicio.comentarios","juicio_id", size=500 ,string="Comentarios",domain=[('estado_instancia','=','sentencia_final')], default_order="create_date asc")






    # Estados del juicio
    state =  fields.Selection(ESTADOS_JUCIOS,"Estados",copy=False,default="borrador",tracking=True) 
    state_segunda = fields.Selection(ESTADOS_SEGUNDA_INSTANCIA,"Estado Corte Apela..",default="ingreso_recurso",copy=False ,tracking=True)
    state_corte = fields.Selection(ESTADOS_CORTE_SUPREMA,"Estado Corte Suprema",default="ingreso_recurso_corte",copy=False,tracking=True) 

    # Estados extra en la primera instancia 
    state_primera_civil = fields.Selection(ESTADOS_PRIMERA_CIVIL,"Estado 1 instancia",default="discusion_civil",tracking=True) 
    state_primera_monitorio = fields.Selection(ESTADOS_PRIMERA_MONITORIO,"Estado Monitorio",default="audiencia_monitorio",tracking=True) 
    state_primera_apelacion = fields.Selection(ESTADOS_PRIMERA_APELACION,"Estado Apelación",default="preparacion",tracking=True) 
    state_primera_jpl = fields.Selection(ESTADOS_PRIMERA_JPL,"Estado JPL",default="audiencia_jpl",tracking=True) 

    #datos mínimos del juicio
    name =  fields.Char(string="Caratula",copy=False ,required=True)
    numero_juicio = fields.Char("RIT" ,copy=False,required=True)
    peticion_juicio = fields.Selection(PETICION,string="Rol Durante la Demanda",copy=False,required=True)

    #notificacion
    notificado = fields.Boolean("Notificación recibida",copy=False,tracking=True)
    fecha_notificacion = fields.Date("Fecha de la Notificación",copy=False,tracking=True)

    tipo_de_juicio = fields.Selection(TIPO_DE_JUICIO,string="Tipo de juicio",copy=False,required=True)
    tipo_laboral = fields.Selection(TIPO_LABORAL,string="Procedimiento Laboral",copy=False)
    corte = fields.Char("Corte",copy=False,required=True)
    tribunal= fields.Char("Tribunal",copy=False,required=True)

    #identificacion de las partes 
    company_id = fields.Many2one(comodel_name="res.company", string="Compañia", default = lambda self : self.sudo().env.company.id ,required=True,readonly=True)
    
    representante = fields.Char("Nombre del Representante",  copy=False,required=True)
    correo_representante = fields.Char("Corrreo del Representante",copy=False,required=True)

    nombre_contraparte = fields.Char("Nombre de la Contraparte",copy=False,required=True)
    direccion_contraparte = fields.Char("Dirección de la Contraparte",copy=False,required=True)
    correo_contraparte = fields.Char("Corrreo de la Contraparte",copy=False,required=True)
  
    #cuerpo de la demanda 
    motivo_demanda = fields.Text("Motivo de la demanda" ,copy=False,required=True, size=500)
    reclamos_legales = fields.Text("Reclamos legales" ,copy=False,required=True, size=500)
    fundamentos_legales = fields.Text("Fundamentos legales" ,copy=False,required=True, size=500)
    peticion = fields.Text("Petición de la demanda",copy=False,required=True, size=500)

    fecha_juicio = fields.Date(string="Fecha Inicio del juicio",copy=False,required=True)
    rebeldia = fields.Char(string="Comentario Rebeldía",copy=False)

    # la idea es que digo soy reconvencion apunto al juicio padre y escondo la tabla
    #si no hay hijos muestro la ventana con todos los hijos

    #soy el padre que muestro a los hijos
    hijos_reconvencion_ids = fields.One2many('legal.juicio','reconvencion_id' ,string="Reconvenciones") 

    #afirmo que soy un hijo
    es_reconvencion =  fields.Boolean("¿Es Reconvención?" ,copy=False)

    #indico a mi padre
    reconvencion_id = fields.Many2one("legal.juicio",string="Reconvención")

 
    
             ###Priemra Instancia###

    #CONCILIACIONES
    conciliacion_primera = fields.Boolean("¿hay Conciliación por ambas partes?")
    text_cociliacion_primera = fields.Text("Comentario de la Conciliación",copy=False, size=500,tracking=True)
    adjunto_conciliacion_primera = fields.Binary("Adjunto de la Conciliación",copy=False,tracking=True)
    adjunto_conciliacion_primera_filename = fields.Char(invisible=True,copy=False)

    #aplazamisento
    tiene_aplazamiento = fields.Boolean(string="Solicitud de un aplazamiento",copy=False)
    text_aplazamiento = fields.Text("Comentario del Aplazamiento",copy=False, size=500)
    fecha_aplazamiento = fields.Date(string="Fecha de Reanudación",copy=False)

    #sentencia civil 
    cumplir_sentencia = fields.Boolean("¿Sentencia sin Recursos?",copy=False,tracking=True)

    #sentencia monitorios
    cumplir_sentencia_monitorio = fields.Boolean("¿Sentencia sin Recursos?",copy=False,tracking=True)
    
    #Apelaciom
    # fecha preparacion
    fecha_oral = fields.Date("Fecha del juicio oral",copy=False)

    #oral
    solicitud_receso = fields.Boolean("Solicitud de Receso",copy=False)
    fecha_receso = fields.Date("Fecha de extensión",copy=False)
    #sentencia
    cumplir_sentencia_oral = fields.Boolean("¿Sentencia sin Recursos?",copy=False,tracking=True)
    #sentencia jpl
    cumplir_sentencia_jpl = fields.Boolean("¿Sentencia sin Recursos?",copy=False,tracking=True)

             ###Corte de Apelaciones###


    ## conciliación
    conciliacion_segunda = fields.Boolean("¿hay Conciliación por ambas partes?", copy=False,tracking=True)
    text_cociliacion_segunda = fields.Text("Comentario de la Conciliación",copy=False, size=500)
    adjunto_conciliacion_segunda = fields.Binary("Adjunto de la Conciliación",copy=False,tracking=True)
    adjunto_conciliacion_segunda_filename = fields.Char(invisible=True,copy=False)
    
    ## aplazamiento
    aplazamiento_segunda = fields.Boolean("Solicitud de un aplazamiento",copy=False,tracking=True)
    text_aplazamiento_segunda = fields.Text("Comentario del aplazamiento",copy=False, size=500)
    fecha_aplazamiento_segunda = fields.Date("Fecha de Reanudación",copy=False)


    #ingreso de recurso
    fecha_ingreso_recurso_seg = fields.Date("Fecha de Ingreso Recursos",copy=False)

    ## Inclusión de la Causa en Tabla:
    fecha_causa_tabla =  fields.Datetime(string="Fecha de Audiencia:",copy=False)
    
    ## Sentencia de Segunda Instancia:
    cumplir_sentencia_segunda = fields.Boolean("¿Sentencia sin Recursos?",copy=False,tracking=True)

           
           
            ### CORTE SUPREMA ###


    #Conciliacion
    conciliacion_corte = fields.Boolean("¿hay Conciliación por ambas partes?", copy=False,tracking=True)
    text_cociliacion_corte = fields.Text("Comentario de la Conciliación",copy=False, size=500)
    adjunto_conciliacion_corte = fields.Binary("Adjunto de la Conciliación",copy=False,tracking=True)
    adjunto_conciliacion_corte_filename = fields.Char(invisible=True,copy=False)



    #ingresod de recursos
    fecha_ingreso_recurso_corte = fields.Date("Fecha de Ingreso de Recursos",copy=False)
    
    #tabla
    fecha_tabla_corte =fields.Date("Fecha de tabla",copy=False,tracking=True)
    
    #sentencia final
    cumplir_sentencia_corte = fields.Boolean("¿Sentencia final dictada?")


    #CUMPLIMIENTO   
    cumplimiento_tiempo = fields.Boolean("Establecer una fecha para el cumplimiento", copy=False, default=False)
    fecha_inicio_cumplimiento = fields.Date("Fecha de inicio",copy=False)
    text_comentario_cumplimiento = fields.Text("Comentario del inicio del cumplimiento",copy=False, size=500)

    cumplimiento_termino = fields.Boolean("Establecer Termino",copy=False)
    fecha_termino_cumplimiento = fields.Date("Fecha de Termino", copy=False)
    text_comentario_termino = fields.Text("Comentario del termino del cumplimiento",copy=False, size=500)

    sentencia_cumplida = fields.Boolean("¿El Cumplimiento fue completado?",copy=False, default=False)
    txt_sentencia_cumplida =  fields.Text("Comentario del Cumplimieto",copy=False, size=500)


    #usuarios permitodos para ver el juicio
        
    usuario_ids = fields.Many2many('res.users', 'legal_juicio_rel',
                                column1='juicio_id', 
                                column2='usuario_id',
                                string="Usuarios permitidos",
                                copy=False ,
                                tracking=True)
    @api.model
    def create(self, values):
        if 'correo_representante' in values:
            self._valida_email(email=values.get('correo_representante'))
        if 'correo_contraparte' in values:
            self._valida_email(email=values.get('correo_contraparte'))
        if 'tipo_de_juicio'in values:
            tipo = values.get('tipo_de_juicio')
            if tipo != 'laboral':
                values['tipo_laboral'] = None
        if 'numero_juicio' in values:
            numero = values.get('numero_juicio')
            if numero == self.numero_juicio:
                raise UserError(f"El Siguiente RIT ({numero}) ya se encuentra en uso ")
        return super(ControlJuicioCivil, self).create(values)
    
    
    @api.model
    def name_get(self):
        result = []
        for record in self:
            name = record.name
            rit = record.numero_juicio
            result.append((record.id, f"{rit} - {name}"))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', ('name', operator, name), ('numero_juicio', operator, name)]
        records = self.search(domain + args, limit=limit)
        return records.name_get()

    #funcion para dar permisos al momento de identificar al usuario
    def write(self, values): 
        if 'usuario_ids' in values:
            old_users = self._origin.usuario_ids.ids 
            value_usuario_ids = values.get("usuario_ids")
            linea_datos = value_usuario_ids[0]
            linea_ids = linea_datos[2]
            new_user_ids = list(set(linea_ids) - set(old_users))
            res_users_add = self.env['res.users'].browse(new_user_ids) # este identifica el usuario y le da permisos
            grupo_lector = self.env.ref('l10n_cl_legal_contratos.legal_contrato_group_lector')
            for user in res_users_add:
                if not user.has_group('l10n_cl_legal_contratos.legal_contrato_group_lector'):
                    grupo_lector.write({'users': [(4, user.id)]})
        if 'correo_representante' in values:
            self._valida_email(email=values.get('correo_representante'))
        if 'correo_contraparte' in values:
            self._valida_email(email=values.get('correo_contraparte'))
        if 'tipo_de_juicio' in values:
            tipo = values.get('tipo_de_juicio')
            if tipo != 'laboral':
                values['tipo_laboral'] = None
        if 'numero_juicio' in values:
            numero = values.get('numero_juicio')
            if numero == self.numero_juicio:
                raise UserError(f"El Siguiente RIT ({numero}) ya se encuentra en uso ")
        return super(ControlJuicioCivil, self).write(values)
    
   
        
    def _valida_email(self, email):
        """
        Validacion del email 
        """
        if email:
            if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
                raise ValidationError("El Email ingresado no es válido")
        
    @api.onchange('cumplimiento_tiempo')
    def _onchange_cumplimiento_tiempo(self):
        if not self.cumplimiento_tiempo:
            self.cumplimiento_termino = False

    def retorno_states(self):
        """
        Devolvemos el estado actual del juicio si esta en una corte
        Devolvemos estado y instancia para la presentacion del error 
        """
        bandera_estado = None
        presentacion_state = None
        presentacion_instancia = None

        if self.state == "primera":
            presentacion_state = "Primera Instancia"
            if self.tipo_de_juicio == "civil":
                bandera_estado = self.state_primera_civil
                presentacion_instancia =', '.join(str(item[1]) for item in ESTADOS_PRIMERA_CIVIL if item[0] == self.state_primera_civil)
            elif self.tipo_de_juicio == "laboral":
                if self.tipo_laboral == "monitorios":
                    bandera_estado = self.state_primera_monitorio
                    presentacion_instancia =', '.join(str(item[1]) for item in ESTADOS_PRIMERA_MONITORIO if item[0] == self.state_primera_monitorio)
                elif self.tipo_laboral == "apelacion":
                    bandera_estado = self.state_primera_apelacion
                    presentacion_instancia =', '.join(str(item[1]) for item in ESTADOS_PRIMERA_APELACION if item[0] == self.state_primera_apelacion)
            elif self.tipo_de_juicio == "JPL":
                bandera_estado = self.state_primera_jpl
                presentacion_instancia =', '.join(str(item[1]) for item in ESTADOS_PRIMERA_JPL if item[0] == self.state_primera_jpl)
        elif self.state == "segunda":
            presentacion_state = "Corte de Apelaciones"
            bandera_estado = self.state_segunda
            presentacion_instancia =', '.join(str(item[1]) for item in ESTADOS_SEGUNDA_INSTANCIA if item[0] == self.state_segunda)
        elif self.state == "cortesuprema":
            presentacion_state = "Corte Suprema"
            bandera_estado = self.state_corte
            presentacion_instancia =', '.join(str(item[1]) for item in ESTADOS_CORTE_SUPREMA if item[0] == self.state_corte)

        return bandera_estado, presentacion_state, presentacion_instancia



    #valida que por estado al menos se encuentre un adjunto
    def validacion_adjuntos(self):
        """
        Validacion de la existencia de los adjuntos para cambiar de estado.
        """
        
        adjuntos_obj =  self.env["legal.juicio.adjuntos"]
        tablas_obj =  self.env["legal.juicio.tablas"]
        bandera_estado, presentacion_state, presentacion_instancia = self.retorno_states()

        if not bandera_estado:
            raise UserError("Solo puedes Subir Adjuntos dentro de los estados del juicio")
        
        if bandera_estado not in ("inclusion_tabla","inclusion_tabla_corte"):
            adj_estado_todos = adjuntos_obj.search([('estado_ejecutado', '=', bandera_estado),('juicio_id','=',self.id)], order="posicion_adj asc")
            if len(adj_estado_todos) < 1:
                raise UserError(f"Para cambiar de Estado tiene que 'Adjuntar' un pdf como mínimo en {presentacion_instancia} - {presentacion_state}")
        else:
            adj_tabla = tablas_obj.search([('tabla_estate', '=', bandera_estado),('juicio_id','=',self.id)], order="posicion_adj asc")
            if len(adj_tabla) < 1:
                raise UserError(f"Para cambiar de Estado tiene que 'Adjuntar' un pdf como mínimo en {presentacion_instancia} - {presentacion_state}")


    #validar por estado que por lo menos exista un comentario por estado para avanzar              
    def validate_text_table(self):
        """
        Validadción de la existencia de una comentario por estado
        """
        tabla_text_obj =  self.env['legal.juicio.comentarios']
       
        bandera_estado, presentacion_state, presentacion_instancia = self.retorno_states()

        if not bandera_estado:
            raise UserError("Solo Puedes Agregar 'Comentarios' dentro de la instancia del juicio")
        
        adj_estado_todos = tabla_text_obj.search([('estado_instancia', '=', bandera_estado),('juicio_id','=',self.id)], order="create_date asc")
        if len(adj_estado_todos) < 1:
            raise UserError(f"Para cambiar de Estado tiene que agregar un 'Comentario' como mínimo en {presentacion_instancia} - {presentacion_state}")


    #evaluamos las sentencias y las conciliaciones para ver cual esta en true 
    # de esta manera obligamos a pasar a cumplimiento y no cambie a otros estado de la instancia
    def eval_bool_state(self,restart=False):
        """
        valida si hay alguna sentencia o conciliacion activa para cambiar de estado

        Entregando restart = True 
        Cualquier sentencia o conciliacion que este en True se pasa a False
        """
        sentencias =  ["cumplir_sentencia",
                        "cumplir_sentencia_monitorio",
                        "cumplir_sentencia_oral",
                        "cumplir_sentencia_jpl",
                        "cumplir_sentencia_segunda",
                        "cumplir_sentencia_corte"]
        
        conciliaciones =  ['conciliacion_primera',
                           'conciliacion_segunda',
                           'conciliacion_corte']

        # Itera sobre las variables evaluamos cual es True
        for sentencia_eval in sentencias:
            if eval('self.'+sentencia_eval):
                if restart == False:
                    raise UserError("No puedes cambiar de Estado teniendo una Sentencia.\nSe recomienda pasar a cumplimiento.")
                else:
                    # devolvemos las salidas a false cuando salimos de cancelado a borrador
                    self[sentencia_eval] = False

        for conciliacion_eval in conciliaciones:
            if eval('self.'+conciliacion_eval):
                if restart == False:
                    raise UserError("No puedes cambiar de Estado teniendo una Conciliación.\nSe recomienda pasar a cumplimiento.")
                else:
                    # devolvemos las salidas a false cuando salimos de cancelado a borrador
                    self[conciliacion_eval] = False



    #Primera Instancia Botones state
    #civil
    def primera_discusion (self):   
        self.eval_bool_state()
        self.state_primera_civil = "discusion_civil"  

    def primera_prueba (self):   
        self.eval_bool_state()
        if self.state_primera_civil ==  "discusion_civil": 
            self.validate_text_table()
            self.validacion_adjuntos() 
        self.state_primera_civil = "prueba_civil"  
        
    def primera_sentencia (self): 
        self.eval_bool_state()
        if self.state_primera_civil ==  "prueba_civil": 
            self.validacion_adjuntos()
            self.validate_text_table() 
        self.state_primera_civil = "sentencia_civil"  

    def recurso_civil (self):  
        self.eval_bool_state()
        if self.state_primera_civil ==  "sentencia_civil": 
            self.validacion_adjuntos() 
            self.validate_text_table()
        self.state_primera_civil = "recursos_civil"   

    
    #monitorios
    def primera_audiencia_unica (self):   
        self.eval_bool_state()
        self.state_primera_monitorio = "audiencia_monitorio" 
        
    def recurso_monitorio(self):
        self.eval_bool_state()
        if self.state_primera_monitorio == "audiencia_monitorio" :
            self.validacion_adjuntos() 
            self.validate_text_table()
        self.state_primera_monitorio = "recursos_monitorio"

    
    #apelaciones
    def primera_audiencia_preparacion (self):
        self.eval_bool_state()
        self.state_primera_apelacion = "preparacion"

    def primera_audiencia_oral(self):
        self.eval_bool_state()
        if self.state_primera_apelacion == "preparacion":
            self.validacion_adjuntos() 
            self.validate_text_table()
        self.state_primera_apelacion = "audiencia_apelacion"

    def recurso_apelacion(self):
        self.eval_bool_state()
        if self.state_primera_apelacion == "audiencia_apelacion":
            self.validacion_adjuntos()
            self.validate_text_table() 
        self.state_primera_apelacion = "recursos_apelacion"
        
    #JPL
    def primera_audiencia_jpl(self):
        self.eval_bool_state()
        self.state_primera_jpl = "audiencia_jpl"

    def primera_sentencia_jpl(self):
        self.eval_bool_state()
        if self.state_primera_jpl == "audiencia_jpl":
            self.validacion_adjuntos()  
            self.validate_text_table()    
        self.state_primera_jpl = "sentencia_jpl"

    def primera_recursos_jpl(self):
        self.eval_bool_state()
        if self.state_primera_jpl == "sentencia_jpl":
            self.validacion_adjuntos() 
            self.validate_text_table()
        self.state_primera_jpl = "recursos_jpl"

    #corte de apelaciones botones state
    def btn_ingreso_recurso(self):
        self.eval_bool_state()
        self.state_segunda = "ingreso_recurso"

    def btn_auto_relacion(self):
        self.eval_bool_state()
        if self.state_segunda == "ingreso_recurso":
            self.validacion_adjuntos() 
            self.validate_text_table()
        self.state_segunda = "auto_relacion"

    def btn_inclusion_tabla(self):
        self.eval_bool_state()
        if self.state_segunda == "auto_relacion":
            self.validacion_adjuntos() 
            self.validate_text_table()
        self.state_segunda = "inclusion_tabla"

    def btn_sentencia_segunda(self):
        self.eval_bool_state()
        if self.state_segunda == "inclusion_tabla":
            self.validacion_adjuntos() 
            self.validate_text_table()
        self.state_segunda = "sentencia_segunda"

    def btn_recursos_segunda(self):
        self.eval_bool_state()
        if self.state_segunda == "sentencia_segunda":
            self.validacion_adjuntos() 
            self.validate_text_table()
        self.state_segunda = "recursos_segunda"

    #agregar el stop si este se cumple sentencia o se llega a un acuerdo 
    #corte suprema botones state
    def btn_ingreso_recurso_corte(self): 
        self.eval_bool_state()
        self.state_corte = "ingreso_recurso_corte"

    def btn_auto_relacion_corte(self):
        self.eval_bool_state()
        if self.state_corte == "ingreso_recurso_corte":
            self.validacion_adjuntos() 
            self.validate_text_table()
        self.state_corte = "auto_relacion_corte"

    def btn_inclusion_tabla_corte(self):
        self.eval_bool_state()
        if self.state_corte == "auto_relacion_corte":
            self.validacion_adjuntos() 
            self.validate_text_table()
        self.state_corte = "inclusion_tabla_corte"

    def btn_sentencia_final(self):
        self.eval_bool_state()
        if self.state_corte == "inclusion_tabla_corte":
            self.validacion_adjuntos() 
            self.validate_text_table()
        self.state_corte = "sentencia_final"

    #botones state principal
            
    def btn_primera(self):
        if self.state == "borrador" and not self.notificado and self.tipo_de_juicio != "JPL":
            raise UserError("Para cambiar de estado 'Verifiqué' que la notificación fue recibida.")
        else:
            self.state = "primera"
            self.bandera_primera = True
            self.bandera_segunda = False
            self.bandera_cortesuprema = False


    def btn_segunda(self):
        self.eval_bool_state()
        self.validacion_adjuntos() 
        self.validate_text_table()
        self.state = "segunda"
        self.bandera_segunda = True
        self.bandera_cortesuprema = False


    def btn_corte(self):
        self.validate_text_table()
        self.eval_bool_state()
        self.validacion_adjuntos() 
        self.state = "cortesuprema"
        self.bandera_cortesuprema = True


    def btn_finalizado(self):
        if not self.sentencia_cumplida:
            raise UserError("Para cambiar de estado verifique que el 'cumplimiento fue completado'")
        else:
            self.state = "finalizado"

    def state_cumplimiento(self): 
        self.validacion_adjuntos() 
        self.validate_text_table()
        self.state = "cumplimiento"
            
    def btn_borrador(self):
        if self.state == "cancelado":
            self.eval_bool_state(restart=True)
        self.state = "borrador"
        self.bandera_primera =False
        self.bandera_segunda = False
        self.bandera_cortesuprema = False

    def state_Cancelado(self):
        self.state = "cancelado"

    def get_stock_file(self):
        """
        Antes de generar el reporte de los adjuntos se comprueba:
            -Que su estado no este en borrador y cancelado
            -Que el juicio contengan algun adjunto
        """
        report = self
        if report.state in ('borrador','cancelado'):
            raise UserError(f"El siguente Juicio {report.name} aun no pasado por alguna Instancia. \nPor lo cual no se han podido encontrar archivos adjuntos.")
        
        report_adjuntos = self.env['legal.juicio.adjuntos'].sudo()
           # model de los adjuntos 

        verificador = report_adjuntos.search([('juicio_id','=',self.id)])
        if len(verificador) == 0:
            raise UserError("No se encontraron archivos disponibles para generar un documento.")
        
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        download_url = f'/legal_juicio/print_juicio/{report.id}/'
        return {
                'type' : 'ir.actions.act_url',
                "url": str(base_url) + str(download_url),
                "target": "new",
                }
    
   
class MultipleAdjuntosEstados(models.Model):
    _name = "legal.juicio.adjuntos"
    """
    Todos los documentos del juicio lo guardamos en este modele para registrar el estado principal y el estado de la instancia
    Tambien le generamos un numero por la subida
    """
    juicio_id = fields.Many2one("legal.juicio",copy=False,string="Juicio Relacionado")
    #mantener el orden de los archivos subidos
    posicion_adj =  fields.Integer(copy=False,string="Posición de ingreso")
    estado_principal = fields.Char("Estado del jucio", copy=False, invisible=True)
    estado_ejecutado = fields.Char("Face del juicio", copy=False, invisible=True)
    adjunto = fields.Binary("adjunto",copy=False,required=True)
    adjunto_filename = fields.Char(copy=False, invisible=True)
  

    @api.model
    def create(self, values):
        adjunto_ver  = values.get("adjunto")
        juicio_id = values.get("juicio_id")
        juicio = self.env["legal.juicio"].browse(juicio_id)
        nombre_archivo = values.get("adjunto_filename")
        bandera_estado = None
        
        if juicio.state == "primera":
            if juicio.tipo_de_juicio == "civil":
                bandera_estado = juicio.state_primera_civil
            elif juicio.tipo_de_juicio == "laboral":
                if juicio.tipo_laboral == "monitorios":
                    bandera_estado = juicio.state_primera_monitorio
                elif juicio.tipo_laboral == "apelacion":
                    bandera_estado = juicio.state_primera_apelacion
            elif juicio.tipo_de_juicio == "JPL":
                bandera_estado = juicio.state_primera_jpl
        elif juicio.state == "segunda":
            bandera_estado = juicio.state_segunda
        elif juicio.state == "cortesuprema":
            bandera_estado = juicio.state_corte
        else:
            raise UserError("Solo puedes Subir Adjuntos dentro de los estados del juicio")
        extencion = str(nombre_archivo).split('.')[-1]
        if extencion != "pdf":
            raise UserError("Solo Adjuntar PDF.")
        if adjunto_ver !=False:
            last_position = self.search([('estado_ejecutado','=', bandera_estado)], order='posicion_adj desc', limit=1).posicion_adj
            if last_position<40:
                values["posicion_adj"] = last_position + 1
                values["estado_principal"] = juicio.state
                values["estado_ejecutado"] = bandera_estado
                values["adjunto_filename"] = nombre_archivo
            else:
                raise UserError("Solo se pueden adjuntar 40 pdf por estado")
        else:
            raise UserError("Tiene que adjuntar un documento en antes de Guardar")

        return super(MultipleAdjuntosEstados, self).create(values)
    
    def write(self, vals):
        if "adjunto" in vals:
            adjunto = vals.get("adjunto")
            if not adjunto:
                raise UserError("Falta un archivo adjunto")
        if 'adjunto_filename' in vals:
            nombre_archivo = vals.get("adjunto_filename")
            extencion = str(nombre_archivo).split('.')[-1]
            if extencion != "pdf":
                raise UserError("Solo Adjuntar PDF.")
        return super(MultipleAdjuntosEstados, self).write(vals)

    #si elemina un adjunto los demas modifican su posición de esta manera tenemos los numero continuos
    def unlink(self):
        
        bandera_estado = None
        delete =  self.juicio_id

        if delete.state == "primera":
            if delete.tipo_de_juicio == "civil":
                bandera_estado = delete.state_primera_civil
            elif delete.tipo_de_juicio == "laboral":
                if delete.tipo_laboral == "monitorios":
                    bandera_estado = delete.state_primera_monitorio
                elif delete.tipo_laboral == "apelacion":
                    bandera_estado = delete.state_primera_apelacion
            elif delete.tipo_de_juicio == "JPL":
                bandera_estado = delete.state_primera_jpl
        elif delete.state == "segunda":
            bandera_estado = delete.state_segunda
        elif delete.state == "cortesuprema":
            bandera_estado = delete.state_corte
        # esto me puede traer mas de una id y en el for selecciono una para poder ordenar el position
        else:
            raise UserError("Debes estar en el Estado correspondiente para eliminar un adjunto")
        for id_delete in self:
            #esto me trae todos los de la base de datos
            adj_estado_todos = self.search([('estado_ejecutado', '=', bandera_estado)], order="posicion_adj asc")
            for adjunto in adj_estado_todos:
                if adjunto.posicion_adj > id_delete.posicion_adj:
                    adjunto.posicion_adj -= 1
      
        return super(MultipleAdjuntosEstados, self).unlink()
    

        
class InclusionTabla(models.Model):
    _name = "legal.juicio.tablas"
    """
        Todos los documentos de tablas los guardo en un modelo diferente por que este puede subir aun despues que pase su estado.
    """

    juicio_id = fields.Many2one("legal.juicio",copy=False,string="Juicio Relacionado")
    #mantener el orden de los archivos subidos
    posicion_adj =  fields.Integer(copy=False,string="Posición de ingreso")
    tabla_estate = fields.Char("Estado de ingreso",copy=False, invisible=True)
    adjunto = fields.Binary("adjunto",copy=False, invisible=True)
    adjunto_filename = fields.Char(copy=False, invisible=True)

    @api.model
    def create(self, values):
        adjunto_ver  = values.get("adjunto")
        juicio_id = values.get("juicio_id")
        juicio = self.env["legal.juicio"].browse(juicio_id)
        nombre_archivo = values.get("adjunto_filename")
        tipo_tabla = None
        nombre_archivo = values.get("adjunto_filename")
        extencion = str(nombre_archivo).split('.')[-1]
        if extencion != "pdf":
            raise UserError("Solo Adjuntar PDF.")
        
        if juicio.state == "segunda":
            tipo_tabla = "inclusion_tabla"
        elif juicio.state == "cortesuprema":
            tipo_tabla = "inclusion_tabla_corte"
        else:
            raise UserError("Solo se pueden agregar Tablas en los siguentes estados ['Corte de apelaciones', 'Corte Suprema']")
    
        if adjunto_ver !=False:
            #traemos el ultimo elemento de la lista para sacar su posición
            last_position = self.search([('tabla_estate','=', tipo_tabla)], order='posicion_adj desc', limit=1).posicion_adj
            if last_position <=40:    
                values["posicion_adj"] = last_position + 1
                values["tabla_estate"] = tipo_tabla
                values["adjunto_filename"] = nombre_archivo
            else:
                raise UserError("Solo se pueden adjuntar 40 pdf por estado")
        else:
            raise UserError(f"Tiene que adjuntar un documento en {tipo_tabla} antes de Guardar")

        return super(InclusionTabla, self).create(values)
    
    def write(self, vals):
        if "adjunto" in vals:
            adjunto = vals.get("adjunto")
            if not adjunto:
                raise UserError("Falta un archivo adjunto")
        if "adjunto_filename" in vals:
            nombre_archivo = vals.get("adjunto_filename")
            extencion = str(nombre_archivo).split('.')[-1]
            if extencion != "pdf":
                raise UserError("Solo Adjuntar PDF.")
        return super(MultipleAdjuntosEstados, self).write(vals)

    #si elemina un adjunto los demas modifican su posición de esta manera tenemos los numero continuos
    def unlink(self):
        
        tabla = self.tabla_estate
        state_juicio = self.juicio_id
        juicio = self.env["legal.juicio"].browse(state_juicio)
        if juicio.state in ("segunda","cortesuprema"):
            #esto me trae todos los de la base de datos
            adj_estado_todos = self.search([('tabla_estate', '=', tabla)], order="posicion_adj asc")
            for adjunto in adj_estado_todos:
                if adjunto.posicion_adj > self.posicion_adj:
                    adjunto.posicion_adj -= 1
        else:
            raise UserError("Debes estar en el Estado correspondiente para eliminar un adjunto")

        return super(InclusionTabla, self).unlink()
    

class MultiplesComentariosEstados(models.Model):
    _name= "legal.juicio.comentarios"
    _description = "Se guardaran todos los comentarios por (titulo, comentario ,estado, instancia, hora y creador)"

    juicio_id = fields.Many2one("legal.juicio",copy=False,string="Juicio Relacionado", readonly=True)
    comentario = fields.Char(string="Comentario", copy=False, size=500 ) # se cambio el campo de text a char para que la tabla no se desborde
    estado_principal = fields.Char("Estado principal", copy=False, readonly=True)
    estado_instancia = fields.Char("Estado Instancia" , copy=False, readonly=True)
    
    
    @api.model
    def create(self, values):
        comentario  = values.get("comentario")
        juicio_id = values.get("juicio_id")
        juicio = self.env["legal.juicio"].browse(juicio_id)
        bandera_estado = None
        
        if juicio.state == "primera":
            if juicio.tipo_de_juicio == "civil":
                bandera_estado = juicio.state_primera_civil
            elif juicio.tipo_de_juicio == "laboral":
                if juicio.tipo_laboral == "monitorios":
                    bandera_estado = juicio.state_primera_monitorio
                elif juicio.tipo_laboral == "apelacion":
                    bandera_estado = juicio.state_primera_apelacion
            elif juicio.tipo_de_juicio == "JPL":
                bandera_estado = juicio.state_primera_jpl
        elif juicio.state == "segunda":
            bandera_estado = juicio.state_segunda
        elif juicio.state == "cortesuprema":
            bandera_estado = juicio.state_corte
        else:
            raise UserError("Solo puedes agregar comentarios dentro de los estados del juicio")
        
        if comentario !=False:
            values["estado_principal"] = juicio.state
            values["estado_instancia"] = bandera_estado
            
        else:
            raise UserError("Tiene que poner un Comentario antes de Guardar")

        return super(MultiplesComentariosEstados, self).create(values)  
    

    def unlink(self):
        return super(MultiplesComentariosEstados, self).unlink()