Descripción del Módulo:
Comienza por proporcionar una descripción general del módulo. Esto incluye su propósito, funcionalidad principal y cualquier otro detalle relevante que los usuarios o desarrolladores deban saber.

    Modulo de Control legal sobre los contratos y los juicios que hay bajo aguas san pedro.


Instalación:
Detalla los pasos necesarios para instalar el módulo en una instancia de Odoo. Esto puede incluir la descarga desde un repositorio, la instalación de dependencias, etc.

    Se ocuparon los siguentes dependencias para la creacion de este modulo:
        'base',
        'hr',
        'l10n_cl_base',
        'l10n_sanitaria_base' 

Configuración:
Describe cómo configurar y personalizar el módulo una vez instalado. Esto puede implicar ajustes de configuración en Odoo, como la activación de características específicas o la asignación de permisos.

    Luego de la instalación del módulo se tienen que dar permisos a los usuarios.
    Donde podremos encontrar los siguientes:
        - Lector: Usuario de visita que solo podrá ver el progreso del contrato o juicio en el cual haya sido mencionado.
        - Editor: Usuario que tendrá el control del módulo (Creación,Edición y Eliminación) de contratos y juicios, también podrás mencionar usuarios para que puedan ver el progreso de un contrato o juicio.


Uso:
Proporciona instrucciones detalladas sobre cómo utilizar las diferentes características y funcionalidades del módulo. Esto puede incluir capturas de pantalla o ejemplos para una comprensión más clara.

    Dentro del modulo se podran tener informacion más detallada de los contratos tanto como su duracion, personas relacionada, fechas, comentarios, doc. Extras y generar recordatorios para enviar por correo.
    
    Para el caso de la pestaña "Usuario" se podra seleccionar a distintos usurios para que puedan ver el progreso de dicho contrato.
    
    Tambien se podra generar un pdf con los documentos ingresado con las siguentes opciones:
        - "Todos los Documentos disponibles": Esto genera un PDF con todos los documentos existentes. Tanto como "doc Borrador", "doc Revision", "doc Firmados" y "doc extras".
        -"Doc firmado y sus doc extras": Como dice la opción se genera un  pdf con el contrato firmado por ambas partes y los doc. extras existente. Tambien cabe destacar si NO HAY DOC. EXTRAS solo saldra el doc firmado.
        -"Solo Contratos(Borrador,Revisión,Firmados)": Se genera un pdf con los contratos ya mencionados.

    En el caso de los juicios se busco tener un control por los estados tanto como el principal que inicia y finaliza el juicio. Como las instancias que tienen sus propios estados en la cual el usurio tendra que ingresar informacion como (Fechas, Comentarios y adjuntos) para poder avanzar por las instancias.
    Tambien cabe destacar que los juicios tienen reconveciones las cuales apuntan de donde se originaron.

Estructura del Código:
Explica la estructura del código del módulo. Esto incluye la organización de los archivos, los diferentes componentes del módulo y cómo están interconectados.

    En el codigo del contrato.py la estructura de del modulo quedo de la siguiente manera:
        - declaracion de variables.
        - funciones constreins.
        - funciones onchange.
        - funciones de validaciones.
        - funciones de envio de correo.
        - función de descarga de pdf.
        - modelo "Clase" para guardar los Doc. Extras.

    Por parte del juicio.py:
        - declaracion de variables.
        - funciones onchange.
        - funciones de validaciones.
        - función de descarga de pdf.
        - "Clase" para guardar los Adjuntos.
        - "Clase" para guardar los Comentarios.

 
Modelos de Datos:
Documenta los modelos de datos definidos por el módulo, incluyendo sus campos, relaciones y restricciones.

    Para la organizacion de este modulo en el apartado de contratos en los "Doc. Extras":
        -Se opto crear una clase que guarde dichos documentos con los siguente atributos
            -Adjunto : El archivo en PDF
            -Fecha de recepción: Fecha en la cual el documento fue recibido.
            -Agregado en el estado: en que estado estaba el contrato cuando el adjunto fue agregado.
            -position_obj: el cual nos dice el orden que fueron agregados.

    Para el caso de los juicios se aplico lo mismo que los contratos y tambien se creo otra class que pueda contener todos los comentarios
        la unica diferencia en esta clase en vez de pedir un adjunto se pide un texto(Comentario).


Vistas:
Describe las vistas creadas por el módulo, como formularios, listas y vistas kanban, junto con cualquier lógica asociada a ellas.




Controladores y Procesos:
Explica cualquier controlador personalizado o procesos definidos en el módulo, así como su propósito y funcionamiento.

    En auto_acciones.xml se generaron 2 controloes para que puedan llamar a las funciones de los contratos:
        1.- auto_control_vencimientos: Examina que contratos estan por llegar a su fecha de vencimiento y envia un correo.
        2.- auto_control_recordatorio: Examina los contratos que tienen un recordatorio y tengan la misma fecha.


Vistas y Plantillas:
Documenta cualquier vista o plantilla personalizada creada por el módulo, incluyendo su propósito y cómo se utilizan.


Seguridad:
Describe cualquier configuración de seguridad implementada por el módulo, como grupos de usuarios y permisos.

APIs y Servicios Externos:
Si el módulo interactúa con servicios externos o API, documenta cómo se realiza esta interacción y cualquier configuración necesaria.

Pruebas:
Proporciona instrucciones sobre cómo realizar pruebas unitarias o de integración para el módulo, junto con ejemplos si es posible.

    No se genero carpeta con pruebas unitarias 

Compatibilidad y Requisitos:
Especifica cualquier requisito de versión de Odoo u otros módulos necesarios para que el módulo funcione correctamente.

FAQ y Problemas Conocidos:
Incluye una sección de preguntas frecuentes y problemas conocidos junto con sus soluciones si es posible. Esto puede ayudar a los usuarios a solucionar problemas comunes por sí mismos.

Contacto y Soporte:
Proporciona información de contacto para el desarrollador o el equipo de soporte del módulo, para que los usuarios puedan obtener ayuda adicional si es necesario.