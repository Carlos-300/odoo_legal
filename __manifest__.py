# -*- coding: utf-8 -*-

{
    'name': 'Control contrato',
    'version': '3.0',
    'summary': '''Módulo legal contrato''',
    'description': '''Módulo para el control de contratos , a los trabajadores de Aguas San Pedro S.A.''',
    'category': 'Legal2',
    'author': 'Carlos Salas',
    'depends': [
        'base',
        'hr',
        'l10n_cl_base',
        'l10n_sanitaria_base'
        ],
    'data': [  
        #'data/auto_acciones.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/rules.xml',
        'report/reporte_juicio.xml',
        'report/report_contrato.xml',
        'views/base_view.xml',
        'views/views_contrato.xml',
        'views/views_juicios.xml',
        'wizard/imprimir_adjunto_contrato_view.xml',
        
    ],
    'images': [''],
    'license': 'AGPL-3',
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False
}
