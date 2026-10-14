"""Diez guiones de Cancún (10/10/2026): noticia reciente + trasfondo histórico +
cercanía con quien vive aquí. Misma fórmula y estilo que /lotefish3.

Cada dato salió de una nota que se abrió y leyó. Lo que solo dice un medio va
atribuido en la narración ("según PorEsto"). NO se usan: los "mil" que
marcharon en el IMSS (la nota no lo dice), los "2 millones" del apagón (son
personas, no usuarios; se usa 745,533 usuarios), que el gobierno "piensa
retirar" la alerta de género (no se pudo leer la nota), ni el ranking nacional
de feminicidios (las fuentes no coinciden).

    C:\\dato-mata-gato-bot\\.venv\\Scripts\\python.exe tools\\guiones_cancun_cercania.py
"""

import json
from pathlib import Path

from guiones_historicos_cancun import cierre, ficha, foto, plano, web

ZH = "File:Zona Hotelera, Cancún, Q.R., Mexico - panoramio (106).jpg"
CENTRO = "File:Calle Margaritas, Sm. 22, Col. Centro, Cancún - panoramio.jpg"
TULUM = "File:Avenida Tulum, Cancun, Quintana Roo, Mexico 2021.jpg"
ANAPATY = "File:AnapatyPic1.jpg"

GUIONES = {
    "guion-cancun-mobi-camiones": {
        "titulo": "MOBI en Cancún", "gancho": "CAMIONES GRATIS", "claves": ["mobi", "transporte"],
        "fuentes": {
            "banderazo": "https://mvsnoticias.com/nacional/estados/2026/10/5/cancun-amplia-red-de-transporte-publico-mobi-con-100-autobuses-hibridos-748702.html (05/10/2026: 100 híbridos Yutong; de 38 a 138; Mara Lezama y Ana Paty Peralta; 6 rutas antes de fin de año; pruebas gratis: Ruta 17 del 19 al 26 de octubre, Villas del Mar 3-Puente Nichupté 2-9 nov, VdM3-KM0 16-23 nov, La Rehoyada-Zona Hotelera 30 nov-7 dic)",
            "estado_15_anos": "https://24horasqroo.mx/2026/05/27/transporte-publico-cancun-5/ (27/05/2026: el Congreso aprueba que el Estado controle el servicio de autobuses de Benito Juárez 15 años; operan Autocar, Maya Caribe y Alfredo V. Bonfil; la tarifa sigue en análisis)",
        },
        "evidencia": [
            web("e1", "prensa", "https://mvsnoticias.com/nacional/estados/2026/10/5/cancun-amplia-red-de-transporte-publico-mobi-con-100-autobuses-hibridos-748702.html", "MVS Noticias, 05/10/2026"),
            web("e2", "prensa", "https://24horasqroo.mx/2026/05/27/transporte-publico-cancun-5/", "24 Horas Quintana Roo, 27/05/2026"),
            web("e3", "prensa", "https://noticaribe.com.mx/2026/10/05/apuesta-mobi-por-integrar-autobuses-tts-y-mototaxis-en-un-solo-sistema-de-movilidad-ampliara-cobertura-en-cancun-y-conectara-costa-mujeres-punta-sam-y-rancho-viejo/", "Noticaribe, 05/10/2026"),
            foto("e4", "persona", ANAPATY), foto("e5", "lugar", TULUM), foto("e6", "lugar", ZH),
            ficha("f1", "5 de octubre de 2026", ["100 autobuses híbridos para MOBI", "De 38 a 138 camiones",
                  "6 rutas antes de que termine el año"], "MVS Noticias"),
            ficha("f2", "Rutas gratis de prueba", ["Ruta 17: 19 al 26 de octubre", "Villas del Mar 3 – Puente Nichupté: 2 al 9 de noviembre",
                  "Villas del Mar 3 – KM 0: 16 al 23 de noviembre", "La Rehoyada – Zona Hotelera: 30 nov al 7 dic"], "MVS Noticias"),
            ficha("f3", "Mayo de 2026", ["El Congreso aprueba que el Estado controle los camiones de Benito Juárez",
                  "Por 15 años", "La tarifa, todavía en análisis"], "24 Horas Quintana Roo"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "Este mes empiezan a circular cien camiones nuevos en Cancún. Y algunas rutas las vas a poder probar gratis.", ["f1", "e1"], "CAMIONES GRATIS"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien toma la Ruta diecisiete todos los días. Del diecinueve al veintiséis de octubre no va a pagar pasaje.", ["f2", "e5"], "RUTA 17 GRATIS"),
            plano("p02", "contexto", "El cinco de octubre, Mara Lezama y Ana Paty Peralta dieron el banderazo a cien autobuses híbridos del sistema MOBI.", ["e1", "e4"], "100 HÍBRIDOS"),
            plano("p03", "el_hecho", "MOBI pasa de treinta y ocho a ciento treinta y ocho camiones. Antes de que termine el año tendrá seis rutas.", ["f1", "e3"], "DE 38 A 138"),
            plano("p04", "bucle_abierto", "Y hay un cambio de fondo: en mayo, el Congreso aprobó que el Estado controle los camiones de Benito Juárez durante quince años.", ["f3", "e2"], "15 AÑOS"),
            plano("p05", "el_desenlace", "Hasta ahora, el servicio lo operan empresas como Autocar, Maya Caribe y Alfredo V. Bonfil.", ["e2", "e5"], "LAS DE SIEMPRE"),
            plano("p06", "contexto", "Las otras rutas gratis llegan en noviembre y diciembre: Villas del Mar tres, la Rehoyada y la Zona Hotelera.", ["f2", "e6"], "NOVIEMBRE Y DICIEMBRE"),
            plano("p07", "cierre_bucle", "Lo que todavía no se anuncia es cuánto va a costar el pasaje cuando termine la prueba gratis.", ["f3", "e1"], "¿Y DESPUÉS?"),
            cierre("Aquí el dato mata al gato. ¿Qué ruta tomas tú? Cuéntamelo en los comentarios.", "¿QUÉ RUTA TOMAS?"),
        ],
    },
    "guion-cancun-imss-citas": {
        "titulo": "IMSS en Cancún", "gancho": "TU CITA, HASTA 2027", "claves": ["imss"],
        "fuentes": {
            "citas": "https://quintanaroo.heraldodemexico.com.mx/local/2026/8/28/imss-sin-espacio-para-atencion-especializada-16486.html (28/08/2026: UMF de Benito Juárez sin espacios para cardiología y dermatología; esperar a 2027 o HGZ 18 de Playa; filas en el HGZ 3 en enero; sin citas 2026 desde octubre 2025; derechohabientes de 972 mil a 1.17 millones según el IMSS)",
            "marcha": "https://elquintanarroense.com.mx/2026/10/01/protestan-trabajadores-del-imss-en-cancun-por-falta-de-insumos-medicos-medicamentos-y-mejores-salarios/ (01/10/2026: marcha por la Kabah; cita de un trabajador)",
            "crecimiento": "https://www.economia.gob.mx/datamexico/es/profile/geo/cancun (Cancún creció 37.9% de 2010 a 2020)",
        },
        "evidencia": [
            web("e1", "prensa", "https://quintanaroo.heraldodemexico.com.mx/local/2026/8/28/imss-sin-espacio-para-atencion-especializada-16486.html", "Heraldo de México QRoo, 28/08/2026"),
            web("e2", "prensa", "https://elquintanarroense.com.mx/2026/10/01/protestan-trabajadores-del-imss-en-cancun-por-falta-de-insumos-medicos-medicamentos-y-mejores-salarios/", "El Quintanarroense, 01/10/2026"),
            web("e3", "prensa", "https://quintanaroo.heraldodemexico.com.mx/local/2026/10/1/imss-cancun-tambien-se-manifiesta-17142.html", "Heraldo de México QRoo, 01/10/2026"),
            foto("e4", "lugar", "File:Pasillos, Hospital Regional IMSS 17, Cancún. - panoramio.jpg"),
            foto("e5", "lugar", "File:Escalera, Hospital Regional 17, Cancún. - panoramio.jpg"),
            foto("e6", "lugar", TULUM),
            ficha("f1", "Clínicas familiares del IMSS · Benito Juárez", ["Sin lugares en la agenda para cardiología y dermatología",
                  "Esperar a 2027 o ir al HGZ 18 de Playa del Carmen"], "Heraldo de México QRoo, 28/08/2026"),
            ficha("f2", "Derechohabientes", ["De 972 mil a 1 millón 170 mil, según el IMSS",
                  "Sin citas para 2026 desde octubre de 2025"], "Heraldo de México QRoo"),
            ficha("f3", "1 de octubre de 2026", ["Trabajadores del IMSS marchan por la avenida Kabah",
                  "\"Nos hace falta material, nos hace falta medicamentos\""], "El Quintanarroense"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "Si hoy pides cita con el cardiólogo en una clínica del IMSS en Cancún, te pueden mandar hasta dos mil veintisiete.", ["f1", "e4"], "TU CITA, HASTA 2027"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien en agosto pidió cita de dermatología en su clínica familiar, y le dijeron que no había espacio en la agenda.", ["e1", "e5"], "NO HAY ESPACIO"),
            plano("p02", "contexto", "Según Heraldo de México, las clínicas familiares de Benito Juárez no tienen lugares para cardiología ni dermatología. O esperas a dos mil veintisiete, o vas a Playa del Carmen.", ["f1", "e1"], "O ESPERAS, O VIAJAS"),
            plano("p03", "el_hecho", "En enero hubo filas largas en el Hospital General de Zona tres. La plataforma no daba citas para dos mil veintiséis desde octubre de dos mil veinticinco.", ["f2", "e4"], "SIN CITAS DESDE 2025"),
            plano("p04", "bucle_abierto", "El IMSS reconoce que sus derechohabientes pasaron de novecientos setenta y dos mil a un millón ciento setenta mil.", ["f2", "e6"], "1 MILLÓN 170 MIL"),
            plano("p05", "el_desenlace", "Y el uno de octubre, sus propios trabajadores marcharon por la Kabah. Uno lo dijo así: nos hace falta material, nos hace falta medicamentos.", ["f3", "e2"], "FALTAN MEDICAMENTOS"),
            plano("p06", "contexto", "No es de ahora. Entre dos mil diez y dos mil veinte, la población de Cancún creció casi treinta y ocho por ciento, según DataMéxico.", ["e3", "e6"], "CASI 38% MÁS GENTE"),
            plano("p07", "cierre_bucle", "La ciudad sigue creciendo. Las citas, no.", ["e5", "f1"], "LAS CITAS, NO"),
            cierre("Aquí el dato mata al gato. ¿Cuánto tardaron en darte tu última cita? Cuéntamelo en los comentarios.", "¿CUÁNTO ESPERASTE?"),
        ],
    },
    "guion-cancun-urbi-villas-del-rey": {
        "titulo": "Urbi Villas del Rey", "gancho": "17 AÑOS SIN DRENAJE", "claves": ["urbi"],
        "fuentes": {
            "2009": "https://www.poresto.com/quintana-roo/cancun/2025/1/23/aguas-negras-una-problematica-sin-resolver-en-el-fraccionamiento-urbi-de-cancun.html (venta desde 2009 sin drenaje ni conexión a la red de agua; CAPA: abandonado antes de su conclusión; más de 5,170 familias; ~130 fraccionamientos sin municipalizar (dato del medio); fianza de casi 13 millones nunca ejecutada)",
            "inconclusos": "https://www.poresto.com/quintana-roo/cancun/2026/2/11/no-teniamos-a-donde-ir-mas-de-50-familias-de-urbi-villas-del-rey-en-cancun-habitan-en-edificios-inconclusos.html (11/02/2026: más de 50 familias en edificios inconclusos; ventas insuficientes hacia 2015)",
            "concurso": "https://expansion.mx/negocios/2014/12/02/urbi-solicita-concurso-mercantil (diciembre de 2014; pasivos cercanos a 40 mil millones)",
            "bloqueo": "https://grupoanimal.mx/quintana-roo/sociedad/lluvias-cancun-dejan-inundaciones-socavones-protestas (sábado 3/10/2026: bloqueo en la López Portillo por falta de agua)",
        },
        "evidencia": [
            web("e1", "prensa", "https://www.poresto.com/quintana-roo/cancun/2025/1/23/aguas-negras-una-problematica-sin-resolver-en-el-fraccionamiento-urbi-de-cancun.amp.html", "PorEsto, 23/01/2025"),
            web("e2", "prensa", "https://www.poresto.com/quintana-roo/cancun/2026/2/11/no-teniamos-a-donde-ir-mas-de-50-familias-de-urbi-villas-del-rey-en-cancun-habitan-en-edificios-inconclusos.amp.html", "PorEsto, 11/02/2026"),
            web("e3", "prensa", "https://expansion.mx/negocios/2014/12/02/urbi-solicita-concurso-mercantil", "Expansión, 02/12/2014"),
            web("e4", "documento", "https://grupoanimal.mx/quintana-roo/sociedad/lluvias-cancun-dejan-inundaciones-socavones-protestas", "Grupo Animal, 04/10/2026"),
            foto("e5", "lugar", CENTRO), foto("e6", "lugar", TULUM),
            ficha("f1", "Urbi Villas del Rey · 2009", ["Se vende sin drenaje", "Sin conexión a la red de agua potable",
                  "CAPA: \"abandonado antes de su conclusión\""], "PorEsto, 23/01/2025"),
            ficha("f2", "Urbi", ["Diciembre de 2014: pide concurso mercantil", "Deuda de unos 40 mil millones de pesos",
                  "Hacia 2015: bloques sin terminar"], "Expansión y PorEsto"),
            ficha("f3", "Hoy", ["Más de 50 familias viven en edificios inconclusos", "Fianza de casi 13 millones que nunca se cobró",
                  "3 de octubre: bloqueo en la López Portillo por falta de agua"], "PorEsto y Grupo Animal"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "El sábado tres de octubre, vecinos de Urbi bloquearon la López Portillo por falta de agua. El problema empezó hace diecisiete años.", ["e4", "f3"], "17 AÑOS"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien compró su casa en Urbi Villas del Rey en dos mil nueve, sin saber que el fraccionamiento no tenía drenaje.", ["f1", "e5"], "SIN DRENAJE"),
            plano("p02", "contexto", "Según PorEsto, la constructora vendió sin drenaje ni conexión a la red de agua. La CAPA dice que el proyecto fue abandonado antes de terminarse.", ["f1", "e1"], "ABANDONADO"),
            plano("p03", "el_hecho", "En diciembre de dos mil catorce, Urbi pidió concurso mercantil para reestructurar una deuda de unos cuarenta mil millones de pesos.", ["f2", "e3"], "40 MIL MILLONES"),
            plano("p04", "bucle_abierto", "Hacia dos mil quince dejó bloques sin terminar. Hoy más de cincuenta familias viven en esos edificios inconclusos.", ["f2", "e2"], "EDIFICIOS INCONCLUSOS"),
            plano("p05", "el_desenlace", "La Tesorería municipal confirmó una fianza de casi trece millones de pesos a favor del municipio. Nunca le ordenaron cobrarla.", ["f3", "e1"], "13 MILLONES SIN COBRAR"),
            plano("p06", "contexto", "Y no es el único: según PorEsto, en Cancún hay unos ciento treinta fraccionamientos sin municipalizar.", ["e1", "e6"], "130 FRACCIONAMIENTOS"),
            plano("p07", "cierre_bucle", "Diecisiete años después, el agua sigue sin llegar bien. Y los vecinos siguen saliendo a la calle.", ["e4", "f3"], "SIGUEN EN LA CALLE"),
            cierre("Aquí el dato mata al gato. ¿Tu fraccionamiento ya está municipalizado? Cuéntamelo en los comentarios.", "¿Y EL TUYO?"),
        ],
    },
    "guion-cancun-dengue-2026": {
        "titulo": "Dengue en Quintana Roo", "gancho": "CASI EL DOBLE", "claves": ["dengue"],
        "fuentes": {
            "2026": "https://www.poresto.com/quintana-roo/2026/10/5/quintana-roo-suma-336-casos-de-dengue-y-registra-26-nuevos-contagios-en-una-semana.html (05/10/2026, SINAVE: 336 casos a la semana 38; +87.7% contra 179 en 2025; 117 con signos de alarma y grave; 2 muertes; semáforo rojo en Playa del Carmen y Othón P. Blanco)",
            "2019": "https://www.lajornadamaya.mx/quintanaroo/34989/disminuyen-casos-de-dengue-en-quintana-roo (SSA: 2019, 1,950 casos y 13 muertes; 2020, 228 y 1)",
        },
        "evidencia": [
            web("e1", "prensa", "https://www.poresto.com/quintana-roo/2026/10/5/quintana-roo-suma-336-casos-de-dengue-y-registra-26-nuevos-contagios-en-una-semana.amp.html", "PorEsto, 05/10/2026"),
            web("e2", "prensa", "https://solquintanaroo.mx/dengue-sigue-tomando-fuerza-en-quintana-roo/", "Sol Quintana Roo"),
            web("e3", "prensa", "https://www.lajornadamaya.mx/quintanaroo/34989/disminuyen-casos-de-dengue-en-quintana-roo", "La Jornada Maya, 07/01/2021"),
            foto("e4", "lugar", "File:Aedes aegypti.jpg"), foto("e5", "lugar", CENTRO), foto("e6", "lugar", TULUM),
            ficha("f1", "Dengue en Quintana Roo · 2026", ["336 casos confirmados (semana 38)", "Mismo periodo de 2025: 179",
                  "87.7% más"], "Sistema Nacional de Vigilancia Epidemiológica, vía PorEsto"),
            ficha("f2", "Gravedad", ["117 con signos de alarma o graves", "2 muertes",
                  "Semáforo rojo: Playa del Carmen y Othón P. Blanco"], "PorEsto, 05/10/2026"),
            ficha("f3", "2019", ["1,950 casos y 13 muertes en Quintana Roo", "2020: bajó a 228 casos"], "Secretaría de Salud, vía La Jornada Maya"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "En Quintana Roo, los casos de dengue casi se duplicaron este año. Y las lluvias siguen.", ["f1", "e4"], "CASI EL DOBLE"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien en Cancún deja una cubeta con agua en el patio después de estas lluvias. Ahí se cría el mosquito.", ["e4", "e5"], "UNA CUBETA CON AGUA"),
            plano("p02", "contexto", "Hasta la semana treinta y ocho van trescientos treinta y seis casos confirmados. El año pasado, a esas alturas, eran ciento setenta y nueve.", ["f1", "e1"], "336 CONTRA 179"),
            plano("p03", "el_hecho", "Ciento diecisiete son dengue con signos de alarma o grave. Ya hay dos muertes.", ["f2", "e2"], "2 MUERTES"),
            plano("p04", "bucle_abierto", "Playa del Carmen y Othón P. Blanco están en semáforo rojo. En Cancún reforzaron la limpieza, la descacharrización y la fumigación.", ["f2", "e6"], "SEMÁFORO ROJO"),
            plano("p05", "el_desenlace", "No es la primera vez. En dos mil diecinueve, Quintana Roo cerró con mil novecientos cincuenta casos y trece muertes.", ["f3", "e3"], "2019: 1,950 CASOS"),
            plano("p06", "contexto", "Al año siguiente bajaron a doscientos veintiocho.", ["f3", "e4"], "2020: 228"),
            plano("p07", "cierre_bucle", "Este año ya va casi el doble que el anterior. Y el mosquito no se va con las lluvias.", ["e4", "f1"], "EL MOSQUITO SIGUE"),
            cierre("Aquí el dato mata al gato. ¿En tu colonia ya pasó la fumigación? Cuéntamelo en los comentarios.", "¿YA FUMIGARON?"),
        ],
    },
    "guion-cancun-apagones-peninsula": {
        "titulo": "Apagones en la península", "gancho": "5 APAGONES EN AÑO Y MEDIO", "claves": ["apagon", "apagones", "cfe"],
        "fuentes": {
            "cinco": "https://www.poresto.com/yucatan/2026/9/2/cinco-apagones-masivos-en-ano-y-medio-acumulan-mas-de-3-millones-de-afectaciones-en-la-peninsula-de-yucatan.html (02/09/2026: cinco apagones desde marzo 2025; 26/09/2025 2,262,000 usuarios casi 4 horas; 31/08/2026 745,533 usuarios ~7 horas, CFE: vandalismo; una sola línea de interconexión)",
            "sheinbaum": "https://www.eldiariodechihuahua.mx/nacional/2026/oct/07/tras-apagones-admite-csp-fallas-en-transmision-845127.html (07/10/2026: \"Hubo un problema en la transmisión, en una torre de transmisión\"; Emilia Calleja no se comprometió a eliminar los cortes)",
        },
        "evidencia": [
            web("e1", "prensa", "https://www.poresto.com/yucatan/2026/9/2/cinco-apagones-masivos-en-ano-y-medio-acumulan-mas-de-3-millones-de-afectaciones-en-la-peninsula-de-yucatan.amp.html", "PorEsto, 02/09/2026"),
            web("e2", "prensa", "https://www.eldiariodechihuahua.mx/nacional/2026/oct/07/tras-apagones-admite-csp-fallas-en-transmision-845127.html", "El Diario de Chihuahua, 07/10/2026"),
            web("e3", "prensa", "https://lasillarota.com/estados/2026/9/1/mega-apagon-deja-perdidas-de-100-mdp-solo-en-merida-peninsula-de-yucatan-suma-5-eventos-criticos-526885.html", "La Silla Rota, 01/09/2026"),
            foto("e4", "persona", "File:Claudia Sheinbaum 2025 (cropped).jpg"),
            foto("e5", "lugar", "File:Avenida Yaxchilan at night in Cancun, Mexico.jpg"), foto("e6", "lugar", TULUM),
            ficha("f1", "31 de agosto de 2026", ["745,533 usuarios sin luz en 4 estados", "Unas 7 horas",
                  "CFE: dos líneas de alta tensión, por vandalismo"], "PorEsto y El Diario de Chihuahua"),
            ficha("f2", "7 de octubre de 2026", ["Sheinbaum: \"un problema en una torre de transmisión\"",
                  "La CFE no se compromete a eliminar los cortes"], "El Diario de Chihuahua"),
            ficha("f3", "Cinco apagones masivos", ["Desde marzo de 2025", "26/09/2025: 2.26 millones de usuarios, casi 4 horas",
                  "La península depende de una sola línea de interconexión"], "PorEsto, 02/09/2026"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "En año y medio, la península de Yucatán ha tenido cinco apagones masivos. El último fue el treinta y uno de agosto, de noche.", ["f3", "e1"], "5 APAGONES"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien en Cancún tenía el ventilador prendido esa noche, y de pronto se apagó todo.", ["e5", "e6"], "TODO SE APAGÓ"),
            plano("p02", "contexto", "Ese apagón afectó a setecientos cuarenta y cinco mil usuarios en cuatro estados, durante unas siete horas.", ["f1", "e3"], "745 MIL USUARIOS"),
            plano("p03", "el_hecho", "La CFE dijo que salieron dos líneas de alta tensión, y lo atribuyó a vandalismo.", ["f1", "e1"], "¿VANDALISMO?"),
            plano("p04", "bucle_abierto", "El siete de octubre, Claudia Sheinbaum lo dijo distinto: hubo un problema en una torre de transmisión.", ["e4", "f2"], "UNA TORRE"),
            plano("p05", "el_desenlace", "Y la directora de la CFE, Emilia Calleja, no se comprometió a que deje de pasar.", ["f2", "e2"], "SIN COMPROMISO"),
            plano("p06", "contexto", "El fondo, según especialistas citados por PorEsto: la península depende de una sola línea de interconexión de alta tensión.", ["f3", "e1"], "UNA SOLA LÍNEA"),
            plano("p07", "cierre_bucle", "En septiembre de dos mil veinticinco ya había pasado: más de dos millones de usuarios, casi cuatro horas sin luz.", ["f3", "e5"], "YA HABÍA PASADO"),
            cierre("Aquí el dato mata al gato. ¿Cuánto tiempo te quedaste sin luz? Cuéntamelo en los comentarios.", "¿CUÁNTO SIN LUZ?"),
        ],
    },
    "guion-cancun-basura-relleno": {
        "titulo": "Basura en Cancún", "gancho": "CASI 2 MIL TONELADAS", "claves": ["basura", "relleno", "residuos"],
        "fuentes": {
            "2023": "https://www.eluniversal.com.mx/estados/gobierno-de-cancun-reabre-antiguo-deposito-de-basura-ante-clausura-de-relleno-sanitario/ (20/07/2023: clausura parcial y temporal del relleno por la PPA el 15 de julio, lixiviados; se reabre 6 meses la Parcela 1113, que operó de 2006 a 2013 y cerró por estar a menos de 300 m de casas; ~1,400 t diarias; Ana Paty Peralta: no fue fácil)",
            "abril_2026": "https://cancun.gob.mx/cancun/noticias/leer/3739 (22/04/2026: 1,975 toneladas de recepción diaria promedio)",
            "octubre_2026": "https://lucesdelsiglo.com/2026/10/05/la-basura-problema-eterno-en-cancun-local/ (Siresol: 140,156.72 t de tiraderos ilegales de enero a septiembre) y https://lucesdelsiglo.com/2026/01/14/amplian-operacion-del-relleno-sanitario-hasta-2028-local/ (titular). Atribuidos en la narración.",
        },
        "evidencia": [
            web("e1", "prensa", "https://www.eluniversal.com.mx/estados/gobierno-de-cancun-reabre-antiguo-deposito-de-basura-ante-clausura-de-relleno-sanitario/", "El Universal, 20/07/2023"),
            web("e2", "documento", "https://cancun.gob.mx/cancun/noticias/leer/3739", "Ayuntamiento de Benito Juárez, 22/04/2026"),
            web("e3", "prensa", "https://lucesdelsiglo.com/2026/10/05/la-basura-problema-eterno-en-cancun-local/", "Luces del Siglo, 05/10/2026"),
            web("e4", "prensa", "https://lucesdelsiglo.com/2026/01/14/amplian-operacion-del-relleno-sanitario-hasta-2028-local/", "Luces del Siglo, 14/01/2026"),
            foto("e5", "persona", ANAPATY), foto("e6", "lugar", CENTRO),
            ficha("f1", "Julio de 2023", ["Clausura parcial del relleno sanitario por lixiviados",
                  "Reabren 6 meses la Parcela 1113", "Cerrada en 2013: a menos de 300 m de casas"], "El Universal, 20/07/2023"),
            ficha("f2", "Basura al día", ["2023: unas 1,400 toneladas", "Abril de 2026: 1,975 toneladas en promedio"],
                  "El Universal y Ayuntamiento de Benito Juárez"),
            ficha("f3", "Enero a septiembre de 2026", ["Más de 140 mil toneladas de tiraderos ilegales al relleno",
                  "Permiso del relleno: hasta 2028"], "Luces del Siglo, con datos de Siresol"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "Cancún ya recibe casi dos mil toneladas de basura al día en su relleno. Hace tres años eran mil cuatrocientas.", ["f2", "e2"], "CASI 2 MIL TONELADAS"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien en Cancún saca su bolsa de basura en la noche y no sabe a dónde llega.", ["e6", "f2"], "¿A DÓNDE LLEGA?"),
            plano("p02", "contexto", "En julio de dos mil veintitrés, la procuraduría ambiental del estado clausuró en parte el relleno sanitario por derrames de lixiviados.", ["f1", "e1"], "CLAUSURA, 2023"),
            plano("p03", "el_hecho", "Para no quedarse sin dónde tirar, el municipio reabrió por seis meses la Parcela mil ciento trece. Se había cerrado en dos mil trece por estar a menos de trescientos metros de casas.", ["f1", "e1"], "PARCELA 1113"),
            plano("p04", "bucle_abierto", "La presidenta municipal Ana Paty Peralta dijo entonces que la decisión no fue fácil.", ["e5", "e1"], "NO FUE FÁCIL"),
            plano("p05", "el_desenlace", "En abril de dos mil veintiséis, el Ayuntamiento reportó mil novecientas setenta y cinco toneladas diarias en promedio.", ["f2", "e2"], "1,975 AL DÍA"),
            plano("p06", "contexto", "Y según Luces del Siglo, de enero a septiembre entraron al relleno más de ciento cuarenta mil toneladas recogidas de tiraderos ilegales.", ["f3", "e3"], "140 MIL TONELADAS ILEGALES"),
            plano("p07", "cierre_bucle", "El relleno de hoy tiene permiso hasta dos mil veintiocho. La basura no deja de crecer.", ["e4", "f3"], "HASTA 2028"),
            cierre("Aquí el dato mata al gato. ¿Cada cuánto pasa el camión de la basura por tu calle? Cuéntamelo en los comentarios.", "¿CADA CUÁNTO PASA?"),
        ],
    },
    "guion-cancun-pepe-tigre": {
        "titulo": "Pepe Tigre", "gancho": "UNA JAGUAR EN LA ZONA HOTELERA", "claves": ["jaguar", "profepa"],
        "fuentes": {
            "tvazteca": "https://www.tvazteca.com/aztecanoticias/pepe-tigre-cancun-quien-es-jose-juarez-gil-el-hombre-que-cuida-un-jaguar-en-la-zona/ (José Juárez Gil; restaurante en la Zona Hotelera que en los 80 atraía con tigres y jaguares; cerró por Wilma en 2005; vive con la jaguar Espesna, de 7 años; el 24/09 Profepa no pudo entrar porque él no lo permitió; \"era mi familia\")",
            "profepa": "https://www.yucatan.com.mx/mexico/2026/09/27/profepa-inspecciona-predios-por-jaguar-vinculado-con-pepe-tigre-en-cancun.html (21/09: predio en Alfredo V. Bonfil, cinco jaulas viejas, sin fauna; 24/09: Zona Hotelera; jaguar en NOM-059)",
            "protesta": "https://www.poresto.com/quintana-roo/cancun/2026/9/24/quien-es-pepe-tigre-tiene-un-jaguar-en-su-antiguo-restaurante-de-cancun-y-convocan-a-una-protesta-en-su-apoyo.html",
        },
        "evidencia": [
            web("e1", "prensa", "https://www.yucatan.com.mx/mexico/2026/09/27/profepa-inspecciona-predios-por-jaguar-vinculado-con-pepe-tigre-en-cancun.html", "Diario de Yucatán, 27/09/2026"),
            web("e2", "prensa", "https://www.poresto.com/quintana-roo/cancun/2026/9/24/quien-es-pepe-tigre-tiene-un-jaguar-en-su-antiguo-restaurante-de-cancun-y-convocan-a-una-protesta-en-su-apoyo.amp.html", "PorEsto, 24/09/2026"),
            web("e3", "prensa", "https://www.tvazteca.com/aztecanoticias/pepe-tigre-cancun-quien-es-jose-juarez-gil-el-hombre-que-cuida-un-jaguar-en-la-zona/", "TV Azteca"),
            foto("e4", "lugar", ZH), foto("e5", "lugar", "File:Zona Hotelera, Cancún, Q.R., Mexico - panoramio (116).jpg"),
            foto("e6", "lugar", "File:Zona Hotelera, Cancún, Q.R., Mexico - panoramio (28).jpg"),
            ficha("f1", "José Juárez Gil, \"Pepe Tigre\"", ["Años 80: su restaurante en la Zona Hotelera tenía tigres y jaguares",
                  "2005: el huracán Wilma lo obliga a cerrar", "Vive ahí con la jaguar Espesna, de 7 años"], "TV Azteca"),
            ficha("f2", "Septiembre de 2026 · Profepa", ["21: predio en la Alfredo V. Bonfil, jaulas viejas, sin animales",
                  "24: Zona Hotelera, no le permiten entrar"], "Diario de Yucatán y TV Azteca"),
            ficha("f3", "El jaguar", ["Especie en peligro de extinción (NOM-059)",
                  "Hubo una protesta en apoyo de Pepe Tigre"], "Diario de Yucatán y PorEsto"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "En la Zona Hotelera de Cancún vive una jaguar. Y Profepa no pudo entrar a verla.", ["f2", "e1"], "UNA JAGUAR EN LA ZONA HOTELERA"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien en los ochenta fue a cenar a la Zona Hotelera, a un restaurante que tenía tigres y jaguares.", ["f1", "e4"], "LOS OCHENTA"),
            plano("p02", "contexto", "Era el restaurante de José Juárez Gil, al que en Cancún conocen como Pepe Tigre.", ["e3", "e5"], "PEPE TIGRE"),
            plano("p03", "el_hecho", "El huracán Wilma, en dos mil cinco, lo obligó a cerrar. Él se quedó a vivir ahí, con sus animales.", ["f1", "e6"], "WILMA, 2005"),
            plano("p04", "bucle_abierto", "En septiembre circularon videos de una jaguar dentro del antiguo restaurante. Se llama Espesna y tiene siete años.", ["e2", "f1"], "ESPESNA, 7 AÑOS"),
            plano("p05", "el_desenlace", "Profepa revisó un predio en la Alfredo V. Bonfil y encontró jaulas viejas, sin animales. El veinticuatro de septiembre fue a la Zona Hotelera, y no la dejaron entrar.", ["f2", "e1"], "NO LA DEJARON ENTRAR"),
            plano("p06", "contexto", "El jaguar está en peligro de extinción. Pepe dice que es su familia, y hubo una protesta a su favor.", ["f3", "e2"], "EN PELIGRO DE EXTINCIÓN"),
            plano("p07", "cierre_bucle", "Cuarenta años después de los tigres, la pregunta sigue abierta: ¿quién debe cuidar a Espesna?", ["e3", "f3"], "¿QUIÉN LA CUIDA?"),
            cierre("Aquí el dato mata al gato. ¿Llegaste a conocer el restaurante de Pepe Tigre? Cuéntamelo en los comentarios.", "¿LO CONOCISTE?"),
        ],
    },
    "guion-cancun-rentas-vacacionales": {
        "titulo": "Rentas vacacionales en Cancún", "gancho": "¿DÓNDE SE VALE?", "claves": ["airbnb", "rentas"],
        "fuentes": {
            "pdu": "https://www.clicnoticias.com.mx/rentas-vacacionales-cancun-nuevo-pdu-zonas/ (22/09/2026, con información de 24 Horas: el nuevo PDU definirá polígonos y reglas; candidatas Centro y Zona Hotelera sin definición final; no es prohibición general; 7,025 alojamientos activos en Cancún en septiembre según AirDNA; el municipio no sabe cuántas viviendas cambiaron de uso; el Centro perdería población residente; recuperar zonas centrales y promover vivienda asequible)",
            "historia": "https://es.wikipedia.org/wiki/Canc%C3%BAn (plan de los Landa Verdugo: zona hotelera en la isla y ciudad de servicios en tierra firme con mega-manzanas habitacionales)",
        },
        "evidencia": [
            web("e1", "prensa", "https://www.clicnoticias.com.mx/rentas-vacacionales-cancun-nuevo-pdu-zonas/", "Clic Noticias, 22/09/2026"),
            web("e2", "prensa", "https://lucesdelsiglo.com/2026/02/02/endurecen-reglas-a-airbnb-en-2026-local/", "Luces del Siglo, 02/02/2026"),
            web("e3", "prensa", "https://www.clicnoticias.com.mx/rentas-vacacionales-quintana-roo-2026/", "Clic Noticias"),
            foto("e4", "lugar", CENTRO), foto("e5", "lugar", "File:Cancun, Quintana Roo, Mexico - Centro Cultural de Artes.jpg"), foto("e6", "lugar", ZH),
            ficha("f1", "Rentas vacacionales en Cancún", ["7,025 alojamientos activos en septiembre de 2026",
                  "Airbnb, Vrbo y Booking"], "AirDNA, vía Clic Noticias"),
            ficha("f2", "Nuevo Programa de Desarrollo Urbano", ["Va a definir dónde pueden operar",
                  "Candidatas: Centro y Zona Hotelera", "Sin lista final de colonias"], "Clic Noticias, 22/09/2026"),
            ficha("f3", "Años setenta", ["Hoteles en la isla", "En tierra firme, la ciudad de servicios con supermanzanas de vivienda"],
                  "Wikipedia: Cancún"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "Hay más de siete mil casas y departamentos en Cancún rentándose por aplicación. Y todavía no se decide dónde se vale.", ["f1", "e1"], "¿DÓNDE SE VALE?"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien busca rentar en el Centro de Cancún, y el departamento de al lado ya es de Airbnb.", ["e4", "e2"], "EL DE AL LADO"),
            plano("p02", "contexto", "El nuevo Programa de Desarrollo Urbano va a definir en qué zonas pueden operar las rentas vacacionales.", ["f2", "e1"], "EL NUEVO PLAN"),
            plano("p03", "el_hecho", "Las candidatas son el Centro y la Zona Hotelera. Todavía no hay una lista final de colonias ni de supermanzanas.", ["f2", "e6"], "CENTRO Y ZONA HOTELERA"),
            plano("p04", "bucle_abierto", "Según AirDNA, en septiembre había siete mil veinticinco alojamientos activos en Cancún.", ["f1", "e3"], "7,025"),
            plano("p05", "el_desenlace", "El municipio no sabe cuántas viviendas dejaron de ser casas para volverse hospedaje. Su diagnóstico sigue en proceso.", ["e1", "e5"], "NADIE SABE CUÁNTAS"),
            plano("p06", "contexto", "Y es el Centro el que pierde vecinos. La zona que en los setenta se pensó como la ciudad de servicios, con supermanzanas para vivir.", ["f3", "e4"], "LA CIUDAD DE SERVICIOS"),
            plano("p07", "cierre_bucle", "El plan dice que busca recuperar las zonas centrales y promover vivienda asequible. Falta ver dónde queda la raya.", ["f2", "e5"], "¿DÓNDE QUEDA LA RAYA?"),
            cierre("Aquí el dato mata al gato. ¿En tu edificio ya hay Airbnb? Cuéntamelo en los comentarios.", "¿YA HAY EN TU EDIFICIO?"),
        ],
    },
    "guion-cancun-feminicidios-alerta": {
        "titulo": "Feminicidios en Cancún", "gancho": "3 DE CADA 4", "claves": ["feminicidios", "alerta", "genero"],
        "fuentes": {
            "2026": "https://www.poresto.com/quintana-roo/sucesos/2026/10/9/cancun-acumula-nueve-feminicidios-concentra-cuartas-partes-casos-quintana-roo.html (09/10/2026, SESNSP: 9 feminicidios en Benito Juárez, dos en menos de cuatro días; 12 en Quintana Roo; otros 12 homicidios dolosos de mujeres; enero-agosto: 34.7% de los del país en 20 municipios, entre ellos Benito Juárez)",
            "alerta": "https://www.eluniversal.com.mx/articulo/nacion/sociedad/2017/07/7/lanzan-alerta-de-genero-en-quintana-roo/ (07/07/2017: alerta en Benito Juárez, Solidaridad y Cozumel)",
            "80": "https://lucesdelsiglo.com/2026/09/29/cumplen-80-de-recomendaciones-de-alerta-de-violencia-de-genero-local/ (titular: cumplen 80% de las recomendaciones)",
        },
        "evidencia": [
            web("e1", "prensa", "https://www.poresto.com/quintana-roo/sucesos/2026/10/9/cancun-acumula-nueve-feminicidios-concentra-cuartas-partes-casos-quintana-roo.amp.html", "PorEsto, 09/10/2026"),
            web("e2", "prensa", "https://www.eluniversal.com.mx/articulo/nacion/sociedad/2017/07/7/lanzan-alerta-de-genero-en-quintana-roo/", "El Universal, 07/07/2017"),
            web("e3", "prensa", "https://lucesdelsiglo.com/2026/09/29/cumplen-80-de-recomendaciones-de-alerta-de-violencia-de-genero-local/", "Luces del Siglo, 29/09/2026"),
            foto("e4", "lugar", CENTRO), foto("e5", "lugar", TULUM), foto("e6", "lugar", "File:Avenida Yaxchilan at night in Cancun, Mexico.jpg"),
            ficha("f1", "Feminicidios en 2026", ["Benito Juárez: 9", "Quintana Roo: 12", "Tres de cada cuatro, en Cancún"],
                  "SESNSP, vía PorEsto, 09/10/2026"),
            ficha("f2", "Además", ["12 homicidios dolosos de mujeres en Quintana Roo",
                  "Benito Juárez, entre los 20 municipios con 34.7% de los feminicidios del país"], "SESNSP, vía PorEsto"),
            ficha("f3", "7 de julio de 2017", ["Alerta de Violencia de Género", "Benito Juárez, Solidaridad y Cozumel",
                  "2026: 80% de las recomendaciones cumplidas, según Luces del Siglo"], "El Universal y Luces del Siglo"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "Este año, de cada cuatro feminicidios en Quintana Roo, tres fueron en Cancún.", ["f1", "e1"], "3 DE CADA 4"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien vive en Cancún y cada noche revisa el celular hasta saber que su hija llegó bien a casa.", ["e6", "e4"], "LLEGÓ BIEN"),
            plano("p02", "contexto", "Según el Secretariado Ejecutivo, en dos mil veintiséis van nueve feminicidios en Benito Juárez. Dos, en menos de cuatro días.", ["f1", "e1"], "9 EN BENITO JUÁREZ"),
            plano("p03", "el_hecho", "En todo el estado van doce. Y aparte, otros doce homicidios dolosos de mujeres.", ["f2", "e5"], "12 Y 12"),
            plano("p04", "bucle_abierto", "De enero a agosto, Benito Juárez estuvo entre los veinte municipios que concentran más de un tercio de los feminicidios del país.", ["f2", "e1"], "20 MUNICIPIOS"),
            plano("p05", "el_desenlace", "No es nuevo. El siete de julio de dos mil diecisiete se declaró la Alerta de Violencia de Género en Benito Juárez, Solidaridad y Cozumel.", ["f3", "e2"], "ALERTA DESDE 2017"),
            plano("p06", "contexto", "Nueve años después, según Luces del Siglo, el estado ya cumplió el ochenta por ciento de las recomendaciones.", ["f3", "e3"], "80% CUMPLIDO"),
            plano("p07", "cierre_bucle", "Ochenta por ciento cumplido. Y Cancún sigue teniendo tres de cada cuatro casos.", ["e4", "f1"], "Y SIGUE"),
            cierre("Aquí el dato mata al gato. ¿Qué crees que falta para que esto cambie? Cuéntamelo en los comentarios.", "¿QUÉ FALTA?"),
        ],
    },
    "guion-cancun-tortugas-nidos": {
        "titulo": "Tortugas en Cancún", "gancho": "10 MIL NIDOS", "claves": ["tortuga", "tortugas", "nidos"],
        "fuentes": {
            "2026": "https://www.cancunmio.com/49272717-cancun-registra-mas-de-10-mil-nidos-de-tortugas-marinas-durante-la-temporada-2026/ (08/09/2026, Ecología de Benito Juárez: 10,407 nidos; más de 1.2 millones de huevos; 203,994 crías registradas; 51 corrales; tortuga blanca 10,357, caguama 48, carey 2)",
            "veda": "https://www.dof.gob.mx/nota_detalle.php?codigo=4658226&fecha=31/05/1990 (31/05/1990: veda total e indefinida de tortugas marinas; Código Penal Federal: 1 a 9 años de prisión por capturar o dañar)",
        },
        "evidencia": [
            web("e1", "prensa", "https://www.cancunmio.com/49272717-cancun-registra-mas-de-10-mil-nidos-de-tortugas-marinas-durante-la-temporada-2026/", "Cancún Mío, 08/09/2026"),
            web("e2", "prensa", "https://lucesdelsiglo.com/2026/09/24/protegen-10-mil-500-nidos-y-1-2-millones-de-huevos-de-tortuga-en-cancun-local/", "Luces del Siglo, 24/09/2026"),
            foto("e4", "lugar", "File:Green Sea Turtle grazing seagrass.jpg"), foto("e5", "lugar", "File:Chelonia mydas 176500422.jpg"),
            foto("e6", "lugar", "File:Zona Hotelera, Cancún, Q.R., Mexico - panoramio (25).jpg"),
            ficha("f1", "Temporada 2026 en Cancún", ["10,407 nidos protegidos", "Más de 1.2 millones de huevos",
                  "203,994 crías registradas"], "Ecología de Benito Juárez, vía Cancún Mío"),
            ficha("f2", "Por especie", ["Tortuga blanca: 10,357 nidos", "Caguama: 48", "Carey: 2"], "Ecología de Benito Juárez"),
            ficha("f3", "31 de mayo de 1990", ["Veda total para todas las tortugas marinas",
                  "Hoy: de 1 a 9 años de prisión por capturar o dañar una"], "Diario Oficial y Código Penal Federal"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "Este año, en las playas de Cancún se protegieron más de diez mil nidos de tortuga marina.", ["f1", "e4"], "10 MIL NIDOS"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien camina de noche por la playa en Cancún y ve un corral en la arena. Adentro hay cientos de huevos.", ["e6", "e1"], "UN CORRAL EN LA ARENA"),
            plano("p02", "contexto", "Según la Dirección de Ecología de Benito Juárez, hay cincuenta y un corrales de protección en las playas.", ["e1", "e5"], "51 CORRALES"),
            plano("p03", "el_hecho", "Ahí se cuidaron más de un millón doscientos mil huevos. Ya se registraron más de doscientas tres mil crías.", ["f1", "e2"], "203 MIL CRÍAS"),
            plano("p04", "bucle_abierto", "Casi todos los nidos son de tortuga blanca: diez mil trescientos cincuenta y siete. De caguama, cuarenta y ocho. De carey, solo dos.", ["f2", "e5"], "CAREY: SOLO 2"),
            plano("p05", "el_desenlace", "No siempre estuvieron protegidas. El treinta y uno de mayo de mil novecientos noventa, México decretó una veda total para todas las tortugas marinas.", ["f3", "e2"], "VEDA DE 1990"),
            plano("p06", "contexto", "Hoy, capturar o dañar una tortuga se castiga con uno a nueve años de prisión.", ["f3", "e4"], "DE 1 A 9 AÑOS"),
            plano("p07", "cierre_bucle", "Más de diez mil nidos en las mismas playas de los hoteles. Si ves uno, no lo toques.", ["e6", "f1"], "SI VES UNO, NO LO TOQUES"),
            cierre("Aquí el dato mata al gato. ¿Ya viste una liberación de tortugas? Cuéntamelo en los comentarios.", "¿YA VISTE UNA?"),
        ],
    },
}

for slug, d in GUIONES.items():
    guion = {
        "_schema": {"descripcion": "Short de Dato Mata Gato: noticia reciente de Cancún con trasfondo "
                                   "histórico y cercanía. Fórmula y estilo de /lotefish3.",
                    "fuentes": d["fuentes"]},
        "titulo": d["titulo"], "gancho": d["gancho"], "claves": d.get("claves", []),
        "hashtags": ["#DatoMataGato", "#Cancun", "#QuintanaRoo"],
        "evidencia": d["evidencia"], "planos": d["planos"],
    }
    carpeta = Path(r"C:\Android_in") / slug
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / "guion.json").write_text(json.dumps(guion, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{slug}: {sum(len(p['narracion'].split()) for p in d['planos'])} palabras")
