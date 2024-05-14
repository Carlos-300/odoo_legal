# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api 
from odoo.exceptions import UserError , ValidationError
from markupsafe import Markup
from datetime import datetime, timedelta
from pytz import timezone

_logger = logging.getLogger(__name__)

# hacer report y verificar el tema de envio de correo

ESTADOS_SELECCION = [('borrador', 'Borrador'), 
           ('revision', 'Revisión'),
           ('firmados', 'Firmado'), 
           ('vigente', 'Vigente'), 
           ('vencido', 'Vencido'), 
           ('finalizado', 'Finalizado'), 
           ('cancelado', 'Cancelado')]

TIPO_CONTRATO = [('obra', 'Obra'),
            ('servidumbre', 'Servidumbre'),
            ('compraventa/promesa','Compraventa/Promesa Compraventa'),
            ('arrendamiento', 'Arrendamiento'),
            ('prestacion de servicios','Prestación de servicios')]

DURACION = [('anual', 'Anual'),
            ('mensual', 'Mensual')]

STATUS_COMPRAVENTA =[('cumplimiento','Cumplimiento de las obligaciones'),
                    ('mutuo','Mutuo acuerdo'),
                    ('incumplimiento','Incumplimiento'),
                    ('vencimiento','Vencimiento del plazo'),
                    ('causas','Resolución por causas legales'),
                    ('retracto','Retracto en ciertos casos')]


class ControlContrato(models.Model):
    # recuerda 
    # etiqueta unicas
    # todos los many2one el nombre de la variable termina con _id
    # todos los many2many el nombre de la variable termina con _ids
    _name = "legal.contrato"
    _inherit = ['mail.thread']

    
    name = fields.Char(string="Nombre del contrato",
                       copy=False,
                       required=True)
    numero_contrato = fields.Char(string="Numero del contrato", copy=False,required=True)
    tipo_de_contrato =  fields.Selection(TIPO_CONTRATO, required=True,copy=False, string="Tipo de contrato" )

    state =  fields.Selection(selection=ESTADOS_SELECCION, default="borrador",copy=False,string="Estado",tracking=True) 

    fecha_inicio = fields.Date(string="Fecha de inicio del contrato", copy=False,required=True ,tracking=True)
    fecha_recepcion = fields.Date(string="Fecha de recepción del contrato", copy=False,required=True ,tracking=True)

    tiene_plazofijo = fields.Boolean(string="¿Tiene plazo fijo?", copy=False)
    fecha_vencimiento = fields.Date(string="Fecha de vencimiento del contrato", copy=False)

    activar_recordatorio = fields.Boolean(string="Activar recordatorio",tracking=True)
    fecha_recordatorio = fields.Date(string="Fecha de recordatorio", copy=False,tracking=True)
   
    company_id = fields.Many2one(comodel_name="res.company", 
                              string="Compañia",
                              default = lambda self : self.sudo().env.company.id ,
                              required=True,
                              readonly=True)

    concesion_id = fields.Many2one(comodel_name="sanitaria.concesion",
                                string="Concesión" ,
                                domain="[('company_id', '=', company_id)]")

    departamento_id = fields.Many2one(comodel_name="hr.department",
                                            string="Departamento",
                                            required=True)
                                            
    responsable_id = fields.Many2one(comodel_name="res.users", 
                                    string="Responsable",
                                    required=True, 
                                    domain="[('company_ids', '=', company_id),('department_id','=',departamento_id)]")
    
    
    es_empresa = fields.Boolean(string="¿Es empresa ?", copy=False)       
    nombre_contraparte = fields.Char(string="Nombre contraparte",required=True)
    rut_contraparte = fields.Char(string="Rut contraparte",required=True)


    #se adjuntan contratos por estados de este solo los doc finales de cada estado

    contrato_borrador = fields.Binary(string="Contrato Borrador",copy=False,required=True)
    contrato_borrador_filename = fields.Char()

    contrato_revision = fields.Binary(string="Contrato Revisión",copy=False,required=True)
    contrato_revision_filename = fields.Char()
    
    contrato_firmados = fields.Binary(string="Contrato Firmados",copy=False,required=True)
    contrato_firmados_filename = fields.Char()



    duracion_contrato = fields.Selection(selection=DURACION, copy=False ,tracking=True)
    #arrendamiento
    solicitud_de_termino = fields.Boolean(string="Solicitud de termino" , copy=False ,tracking=True)
    fecha_solicitud_termino =fields.Date(string="Fecha ingreso de la Solicitud" , copy=False)
    adj_termino_filename = fields.Char()
    adj_termino = fields.Binary(string="Documento de Termino del contrato" , copy=False)

    contrato_indefinido = fields.Boolean("¿Contrato Indefinido?", copy=False )

    #obra
    finalizacion_obra = fields.Boolean(string="¿Obra Finalizada?" , copy=False ,tracking=True)
    fecha_recepcion_obra = fields.Date(string="Fecha de recepción del documento",copy=False )
    adjunto_finalobra =fields.Binary(string="Certificado de Terminación de Obra",copy=False)
    adjunto_finalobra_filename = fields.Char()

    #compraventa
    finalizacion_compraventa =  fields.Boolean(string="¿Compraventa Finalizada?",copy=False ,tracking=True)
    fecha_finaliza_compraventa = fields.Date(string="Fecha de la Finalización",copy=False)
    tipo_finalizacion_compraventa = fields.Selection(STATUS_COMPRAVENTA,copy=False)
    adjunto_compraventa_final = fields.Binary(string="Documento de finalización", copy=False)
    adjunto_compraventa_filename = fields.Char()
    comentario_finalizado = fields.Char(string="Comentario por la finalización",copy=False)


    comentario_borrador = fields.Text(string="Comentario Borrador",copy=False)
    comentario_revision = fields.Text(string="Comentario Revisión",copy=False)
    comentario_firmados = fields.Text(string="Comentario Firmados",copy=False)
    comentario_vigente = fields.Text(string="Comentario Vigente",copy=False)
    comentario_vencido = fields.Text(string="Comentario Vencido",copy=False)
    comentario_finalizado = fields.Text(string="Comentario Finalizado",copy=False)


    detalle_extra_ids =  fields.One2many("legal.contrato.adjuntos.extras", "contrato_id",string="Doc. Extras",default_order="position_obj asc", tracking=True,copy=False)
   
    usuario_ids = fields.Many2many('res.users', 'legal_contrato_rel',
                                column1='contrato_id', 
                                column2='usuario_id',
                                string="Usuarios permitidos",
                                copy=False ,
                                tracking=True,
                                ondelete="cascade")
    @api.constrains('contrato_borrador')
    def _constrains_contrato_borrador(self):
        if self.contrato_borrador:
            self.check_file(file_name=self.contrato_borrador_filename)

    @api.constrains('contrato_revision')
    def _constrains_contrato_revision(self):
        if self.contrato_revision:
            self.check_file(file_name=self.contrato_revision_filename)

    @api.constrains('contrato_firmados')
    def _constrains_contrato_firmados(self):
        if self.contrato_firmados:
            self.check_file(file_name=self.contrato_firmados_filename)

    @api.constrains('adj_termino')
    def _constrains_adj_termino(self):
        if self.adj_termino:
            self.check_file(file_name=self.adj_termino_filename)
    @api.constrains('adjunto_finalobra')
    def _constrains_adjunto_finalobra(self):
        if self.adjunto_finalobra:
            self.check_file(file_name=self.adjunto_finalobra_filename)
    @api.constrains('adjunto_compraventa_final')
    def _constrains_adj_termino(self):
        if self.adjunto_compraventa_final:
            self.check_file(file_name=self.adjunto_compraventa_filename)

    @api.constrains('rut_contraparte')
    def _valida_rut(self):
        for re in self:
            if re.rut_contraparte:
                valid_rut = re.rut_contraparte
                valid_rut = valid_rut.replace('-', '').replace('.', '').replace(',', '')
            if valid_rut:
                rut = valid_rut[:-1]
                valor = rut.isdigit()
                if not valor:
                    raise ValidationError('El rut es inválido')
                digito = valid_rut[-1]
                if digito == 'k' or digito == 'K':
                    digito = 10
                
                valida_digito = 11 - sum([int(a) * int(b) for a, b in zip(str(rut).zfill(8), '32765432')]) % 11
                if valida_digito == 11:
                    valida_digito = 0
                if not (str(digito) == str(valida_digito)):
                    raise ValidationError('El rut es inválido')

    @api.onchange('tiene_plazofijo')
    def _onchange_tiene_plazofijo(self):
        if self.tiene_plazofijo:
            pass
        else:
            self.fecha_vencimiento = None

    @api.onchange('duracion_contrato')
    def _onchange_duracion_contrato(self):
        if self.duracion_contrato:
            if self.duracion_contrato == "mensual":
                self.tiene_plazofijo = True
            else: 
                self.tiene_plazofijo = False
               
    @api.onchange('tipo_de_contrato') 
    def _onchange_tipo_de_contrato(self):
        if self.tipo_de_contrato:
            validacion_tipo_contrato = ["servidumbre","prestacion de servicios","arrendamiento"]
            if self.tipo_de_contrato not in  validacion_tipo_contrato:
                self.solicitud_de_termino = False
            if self.tipo_de_contrato != "obra":
                self.finalizacion_obra =False
            if self.tipo_de_contrato != "compraventa/promesa":
                self.finalizacion_compraventa = False

    @api.onchange('contrato_indefinido')
    def _onchange_contrato_indefinido(self):
        if self.contrato_indefinido:
            self.tiene_plazofijo = False

    @api.onchange('fecha_vencimiento')
    def _onchange_fecha_vencimiento(self):
        if self.fecha_vencimiento:
            timezone_user = self._context.get('tz') or self.env.user.partner_id.tz or 'UTC'
            tz = timezone(timezone_user)
            fecha_hora_actual = datetime.now(tz=tz) 

            if self.fecha_vencimiento and self.tiene_plazofijo:
                if self.fecha_inicio and self.fecha_recepcion:
                    if self.fecha_vencimiento <= self.fecha_inicio:
                        self.fecha_vencimiento = None
                        raise UserError(f"La fecha no puede ser posterior a {self.fecha_inicio.strftime('%d-%m-%Y')}")
                    if self.fecha_vencimiento <= fecha_hora_actual.date(): 
                        mensaje = f"Se recomienda no usar fechas posteriores a la fecha actual {fecha_hora_actual.date().strftime('%d-%m-%Y')}."
                        return {'warning': {'title': 'Advertencia', 'message': mensaje}}
                else:
                    self.fecha_vencimiento = None
                    raise UserError("Verifique el ingreso de las siguiente fechas: \n Fecha de Inicio del contrato \n Fecha de recepción del contrato")
    
    @api.onchange('fecha_recordatorio')
    def _onchange_fecha_recordatorio(self):
        if self.fecha_recordatorio:
            timezone_user = self._context.get('tz') or self.env.user.partner_id.tz or 'UTC'
            tz = timezone(timezone_user)
            fecha_hora_actual = datetime.now(tz=tz) 
            for rec in self:
                if not rec.fecha_inicio :
                    raise UserError("verifique :\n -Fecha de incio del contrato.")
                
                if not rec.tipo_de_contrato :
                    raise UserError("verifique la selección de : \n -Tipo de contrato.")
                
                if rec.tiene_plazofijo and not rec.fecha_vencimiento:
                    raise UserError("verifique  : \n -fecha de vencimiento del contrato.")
                
                if rec.fecha_recordatorio <= fecha_hora_actual.date() :
                    rec.fecha_recordatorio = None
                    raise UserError(f"Solo puedes agregar fechas antes de la actual:\n {fecha_hora_actual.date().strftime('%d-%m-%Y')} ")
              
    @api.onchange('activar_recordatorio')
    def _onchange_activar_recordatorio(self):
        if self.activar_recordatorio:
            pass
        else:
            self.fecha_recordatorio = None

    def boton_revision(self):
        if not self.contrato_borrador:
            raise UserError(f"Agrege documento inicial para cambiar al siguente estado")
        else:
            self.state =  'revision'
    def boton_firmados(self):
        if not self.contrato_borrador or not self.contrato_revision:
            raise UserError(f"Confirme que los documentos esten adjuntados,\n Antes de cambiar el estado.")
        else:
            self.state =  'firmados'
    def boton_vigente(self):
        if not self.contrato_borrador or not self.contrato_revision or not self.contrato_firmados:
            raise UserError(f"Confirme que los documentos esten adjuntados,\n Antes de cambiar el estado.")
        else:
            self.state =  'vigente'
    def boton_vencido(self):
        if self.tipo_de_contrato == "arrendamiento" or not self.tiene_plazofijo or self.contrato_indefinido:
            raise UserError("No se puede pasar al estado de vencido : \n -El tipo de contrato es de 'Arrendamiento'\n -El contrato NO tiene un plazo fijo \n -El contrato es INDIFINIDO")
        if not self.contrato_borrador or not self.contrato_revision or not self.contrato_firmados:
            raise UserError(f"Confirme que los documentos esten adjuntados,\n Antes de cambiar el estado.")
        else:
            self.state =  'vencido'

    def boton_finalizado(self):
        validacion_tipo_contrato = ["servidumbre","prestacion de servicios","arrendamiento"]
        if self.tipo_de_contrato in  validacion_tipo_contrato  and not self.solicitud_de_termino:
            raise UserError("Se requiere datos de Expiración")
        if self.tipo_de_contrato == "obra" and not self.finalizacion_obra:
            raise UserError("Se requiere datos de Expiración")
        if self.tipo_de_contrato == "compraventa/promesa" and not self.finalizacion_compraventa:
            raise UserError("Se requiere datos de Expiración")
        if not self.contrato_borrador or not self.contrato_revision or not self.contrato_firmados:
            raise UserError(f"Confirme que los documentos esten adjuntados,\n Antes de cambiar el estado.")
        else:
            self.state =  'finalizado'
   
    def boton_cancelado(self):
        self.write({'state': 'cancelado'})
        return True
     
    
    def boton_borrador(self):
        self.write({'state': 'borrador'})
        return True

    def check_file(self,file_name):
        if str(file_name.split(".")[1]) != 'pdf' :
                raise ValidationError("No puedes subir archivos diferente a (.pdf)")
    
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
        return super(ControlContrato, self).write(values)
    
    def validate_recordador(self):
        timezone_user = self._context.get('tz') or self.env.user.partner_id.tz or 'UTC'
        tz = timezone(timezone_user)
        fecha_hora_actual = datetime.now(tz=tz) 
        for res in self:
            if res.fecha_recordatorio == fecha_hora_actual.date():
                res.envio_recordatorio()


    def send_mail(self,  company=None):
        """ envio email """
        group_ref = None
        group_ref = self.sudo().env.ref('l10n_cl_legal_contratos.legal_contrato_group_admin')
        #happy_birthday_template = self.sudo().env.ref('l10n_cl_controllegal.controllegal_group_admin_email')
        happy_birthday_template = self.sudo().env.ref('l10n_sanitaria_inet.sanitaria_inet_happy_birthday_email')
        assert happy_birthday_template._name == 'mail.template'

        email_to = ''
        timezone_user = self._context.get('tz') or self.env.user.partner_id.tz or 'UTC'
        tz = timezone(timezone_user)
        self_tz = self.with_context(tz=timezone_user)
        fecha_texto = fields.Datetime.context_timestamp(self_tz, datetime.now()).strftime('%d/%m/%Y')
        # agregar apartado para diferenciar recordatorio vs los q estan por vencer 
        # evaluar los dias que estan por vencer si este no se aproxima a los 30 es un recordatorio 
        subject = f'Notificación Recordatorio. {fecha_texto}'
        message = ''
        texto_base = f'Los siguientes contratos están por cumplir su fecha de vencimiento:'

        message += '<ul>'
        for registro in self:
            if not company:
                company = registro.company_id
            name = ''
            if registro.name:
                name = f'{registro.name}'
            message += f'<li>Nombre: {name} - Nº: {registro.numero_contrato} - Fecha Vencimiento: {registro.fecha_vencimiento} - Estatus : {registro.state}.</li>'
        message += '</ul>'

        if not company:
            company = self.env.company

        if group_ref:
            for user in group_ref.users.filtered(lambda userx: company.id in userx.company_ids.ids):
                if user.email:
                    if not user.omitir_acciones:
                        if email_to:
                            email_to = f'{email_to},'
                        email_to = f'{email_to}{user.email}'
                                
        email_values = {
            'subject': subject,
            'email_to': email_to,
        }
        ctx = {
            'message': Markup(message),
            'texto_base': Markup(texto_base)
        }
        company.enviar_email(happy_birthday_template, email_values, self.sudo(), data_extra=ctx)
        return True

    def run_recordatorio(self):
        res_company_obj = self.env['res.company']
        for company in res_company_obj.sudo().search([]):
            try:
                self.run_recordatorio_send(company)
            except Exception as error_x:
                _logger.error("Error en enviar correo")
                _logger.error(error_x)
                raise ValidationError("Error al enviar el correo : "+ error_x)
            
    def run_recordatorio_send(self,company):
        contratos_ids = super(ControlContrato, self).search([('company_id', '=', company.id)])
        timezone_user = self._context.get('tz') or self.env.user.partner_id.tz or 'UTC'
        tz = timezone(timezone_user)
        self_tz = self.with_context(tz=timezone_user)
        fecha_actual = fields.Datetime.context_timestamp(self_tz, datetime.now())
        dia_actual = fecha_actual.date()
        contratos_recordatorio = self.env["legal.contrato"]
        for contrato in contratos_ids:
            if contrato.activar_recordatorio:
                fecha_current = contrato.fecha_recordatorio
                if  fecha_actual.date() >= fecha_current:
                    contratos_recordatorio += contrato
            if contrato.tiene_plazofijo:
                diferencia = contrato.fecha_vencimiento - dia_actual
                if int(diferencia.days) >= 5 :
                        contratos_recordatorio += contrato
        try:
            if contratos_recordatorio:
                contratos_recordatorio.send_mail(company=company)

        except Exception as e:
            _logger.error("Error en enviar correo filtrando fecha de recordatorio")
            _logger.error(e)
            raise ValidationError("Error al enviar el correo : "+ e)
    
                


    def envio_recordatorio(self,  company=None):
        """ envio email """
        group_ref = None
        group_ref = self.sudo().env.ref('l10n_cl_legal_contratos.legal_contrato_group_admin')
        #happy_birthday_template = self.sudo().env.ref('l10n_cl_controllegal.controllegal_group_admin_email')
        happy_birthday_template = self.sudo().env.ref('l10n_sanitaria_inet.sanitaria_inet_happy_birthday_email')
        assert happy_birthday_template._name == 'mail.template'

        email_to = ''
        timezone_user = self._context.get('tz') or self.env.user.partner_id.tz or 'UTC'
        tz = timezone(timezone_user)
        self_tz = self.with_context(tz=timezone_user)
        fecha_texto = fields.Datetime.context_timestamp(self_tz, datetime.now()).strftime('%d/%m/%Y')
        # agregar apartado para diferenciar recordatorio vs los q estan por vencer 
        # evaluar los dias que estan por vencer si este no se aproxima a los 30 es un recordatorio 
        subject = f'Notificación Recordatorio. {fecha_texto}'
        message = ''
        texto_base = f'El siguiente contrato tiene un recordatorio:'

        message += '<ul>'
        for registro in self:
            if not company:
                company = registro.company_id
            name = ''
            if registro.name:
                name = f'{registro.name}'
            message += f'<li>Nombre: {name}</li>\n<li>Nº: {registro.numero_contrato}</li>\n<li>Fecha de recordatorio: {registro.fecha_recordatorio}</li>\n<li>Estatus: {registro.state}.</li>'
        message += '</ul>'

        if not company:
            company = self.env.company

        if group_ref:
            for user in group_ref.users.filtered(lambda userx: company.id in userx.company_ids.ids):
                if user.email:
                    if not user.omitir_acciones:
                        if email_to:
                            email_to = f'{email_to},'
                        email_to = f'{email_to}{user.email}'
                                
        email_values = {
            'subject': subject,
            'email_to': email_to,
        }
        ctx = {
            'message': Markup(message),
            'texto_base': Markup(texto_base)
        }
        company.enviar_email(happy_birthday_template, email_values, self.sudo(), data_extra=ctx)
        return True   
                
    


    def get_file_all(self):
        """
        Llamo al wizard y le paso al contrato_id el elemento que estoy viendo
        """
        #dejarlo invi 
        return {
            'type': 'ir.actions.act_window',
            'name': 'Impirmir Adjuntos',
            'res_model': 'legal.contrato.imprimir',
            'view_mode': 'form',
            'view_type': 'form',
            'nodestroy': True,
            'target': 'new',
            'context': {'default_contrato_id': self.id, 'dialog_size': 'medium'}
        }
            

    # def control_state(self):
    #         """ run_verificar_convenio_ato_obligacion """
    #         res_company_obj = self.env['res.company']
    #         fecha_cron = self.env.ref('l10n_cl_legal_contratos.auto_control_state').sudo().nextcall
    #         while fecha_cron <= datetime.now():
    #             for company in res_company_obj.sudo().search([]):
    #                 try:
    #                     self.control_state_company(company=company)
    #                 except Exception as error_x:
    #                     mensaje_error = f'Error cron auto_control_state control contratos legal - {error_x} - {fecha_cron} - {company.name}'
    #                     _logger.info(mensaje_error)
    #                     company.mensaje_error('l10n_cl_legal_contratos', mensaje_error, company,
    #                                                 modelo='legal.contrato', metodo='auto_control_state',
    #                                                 usuario=self.env.user, accion=f'self.auto_control_state({company.id}, "{fecha_cron}")', tipo='cron')
    #             fecha_cron += timedelta(days=1)
    #         return True


    def control_state_company(self, company):
        #si pasa la fecha de vencimiento cambiar el stado a vencido 
         # busacar el fields.date --> que saque la fecha del odoo comparar la zona horaria
        timezone_user = self._context.get('tz') or self.env.user.partner_id.tz or 'UTC'
        tz = timezone(timezone_user)
        fecha_hora_actual = datetime.now(tz=tz) 
        fecha_actual = fecha_hora_actual.date()

        
        lista_vencidos = []
        for record in  self.env["legal.contrato"].search([("state", "=","vigente"), ('company_id', '=', company.id)]): # search = vigente
            if fecha_actual > record.fecha_vencimiento and record.tipo_de_contrato != 'arrendamiento': 
                record.state = "vencido"

            diferencia = record.fecha_vencimiento - fecha_actual
            if int(diferencia.days) >= 15 and record.tipo_de_contrato != 'arrendamiento':
                lista_vencidos.append({"name":record.name,
                        "numero" : record.numero_contrato,
                        "vencimiento": record.fecha_vencimiento.strftime('%d-%m-%Y')})
                
        if len(lista_vencidos)!= 0:
            msj = ""
            for lista_v in range(len(lista_vencidos)):
                dato = lista_vencidos[lista_v]
                msj += f" --Nombre : {dato['name']} | Numero : {dato['numero']} | Fecha de vencimiento : {dato['vencimiento']} \n" 
            else:
                msj+= "Se recomienda pasar el estado a 'Finalizado'."
            mensaje = f"Estos contratos tienen 15 o más días vencidos \n {msj} "
            return {'warning': {'title': 'Advertencia', 'message': mensaje}}
        
        


   
    
class DocumentosExtrasContrato(models.Model):
    _name = "legal.contrato.adjuntos.extras"
    _description = "Guardamos todos los adjuntos en este modelo"
    
    contrato_id =  fields.Many2one('legal.contrato',string="relacion contrato",copy=False)
    adjunto =  fields.Binary(string="Doc. adjunto",copy=False,required=True)
    adjunto_filename = fields.Char()
    fecha_recepcion = fields.Date(string="Fecha de recepción",copy=False, required=True)
    state_agregado = fields.Char(string="Agregado en estado",copy=False)
    position_obj = fields.Integer(copy=False,string="Posición de ingreso")

    @api.constrains('adjunto')
    def _constrains_adjunto(self):
        if self.adjunto:
            if str(self.adjunto_filename.split(".")[1]) != 'pdf' :
                raise ValidationError("No puedes subir archivos diferente a (.pdf)")

    @api.model
    def create(self, values):
        if 'contrato_id' in values:
            obj = self.env['legal.contrato'].sudo().browse(values.get('contrato_id'))
            adjunto_ver =  values.get("adjunto")

            if adjunto_ver !=False:
                last_position = self.search([('contrato_id','=',obj.id)],order='position_obj desc', limit=1).position_obj
                if last_position<40:
                    values["position_obj"] = last_position + 1
                    for ver_estado in ESTADOS_SELECCION:
                        if obj.state == ver_estado[0]:
                            values['state_agregado']=ver_estado[1]
                            break
        if "adjunto_filename" in values:
            nombre_archivo = values.get("adjunto_filename")
            extencion = str(nombre_archivo).split('.')[-1]
            if extencion != "pdf":
                raise UserError("Solo Adjuntar PDF.")
 
        return super(DocumentosExtrasContrato, self).create(values)
    

    def write(self, vals):
        adjuto = vals.get('adjunto')

        if not adjuto and not self.adjunto:
            raise UserError("Archivo adjunto faltante requerido.")
        if "adjunto_filename" in vals:
            nombre_archivo = vals.get("adjunto_filename")
            extencion = str(nombre_archivo).split('.')[-1]
            if extencion != "pdf":
                raise UserError("Solo Adjuntar PDF.")
        return super(DocumentosExtrasContrato,self).write(vals)
    

    def unlink(self):
        obj = self.env['legal.contrato.adjuntos.extras'].search([('contrato_id','=',self.contrato_id.id)], order='position_obj asc',)
        obj_delete = self.search([('id','=',self.id)])
        if not obj_delete:
            raise ValidationError("El elemento a eliminar no se pudo encontrar")
        for adjunto in obj:
            if adjunto.position_obj > obj_delete.position_obj:
                adjunto.position_obj -= 1
        return super(DocumentosExtrasContrato,self).unlink()
    
