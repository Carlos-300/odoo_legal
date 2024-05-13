# -*- coding: utf-8 -*-
from odoo import models,fields,api


#from odoo.http import Response 
from odoo.exceptions import UserError 


OPCION_IMPRIMIR = [('todo','Todo los Documentos disponibles'),
                   ('medio','Doc. Firmado y sus Doc. Extras'), 
                   ('bajo','Solo Contratos (Borrador,Revisión,Firmado)')]


class ImprimirDocumentosContrato(models.TransientModel):
    _name= "legal.contrato.imprimir"

    """
    Antes de generar los archivos genero las consultas para ver que este disponible para las opciones.
    Envías el elemento correspondientes para generar la Descarga.
    """

    contrato_id = fields.Many2one("legal.contrato",copy=False,required=True,string="Compilación de Doc. del Contrato")
    opcion = fields.Selection(OPCION_IMPRIMIR,copy=False, string="Opcion de salida", invisible=True)

    def get_file_contrato(self):

        report = self.env['legal.contrato'].sudo().search([('id','=',self.contrato_id.id)])
        
   
        if not report.contrato_borrador and report.state == "borrador":
            raise UserError("El Contrato de borrador NO se pudo encontrar") 
         
        if self.opcion == "todo" and report.state in ['borrador','revision','firmados']:
            raise UserError("El contrato tiene que estas en estado vigente para poder descargar sus extras")
        
        elif self.opcion == "medio" and report.state in ['borrador','revision','firmados']:
            raise UserError("El contrato tiene que estas en estado vigente para poder descargar sus extras")
        
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        download_url = f'/legal_contrato/print_contrato/{report.id}/{self.opcion}/'

        return {
                'type' : 'ir.actions.act_url',
                "url": str(base_url) + str(download_url),
                "target": "new",
                }
    
    
    @api.onchange('opcion')
    def _onchange_opcion(self):
        if self.opcion:
            if not self.contrato_id :
                raise UserError("Seleccione un contrato antes.")

            report_adjuntos = self.env['legal.contrato.adjuntos.extras'].sudo().search([('contrato_id','=',self.contrato_id.id)])

            if self.opcion == 'medio' and len(report_adjuntos) < 1:
                mensaje = "No se encontraron Documentos Extra para el siguente contrato. \nSolo se imprimirá el contrato Firmado" 
                return {'warning': {'title': 'Advertencia', 'message': mensaje}}