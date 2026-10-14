"""Seis guiones de Cancún: noticia reciente con trasfondo histórico (05/10/2026).

Misma fórmula y estilo que /lotefish3 (gancho, "te imaginas a", lugar exacto,
evidencia real, cierre en bucle). Cada dato salió de una fuente que se abrió y
leyó; lo que solo dice un medio va atribuido en la narración. Las cifras que
no se pudieron confirmar (p. ej. 15,600 m2 / 530 cuartos en Punta Nizuc, la
caída del 20% del Tren Maya, que era de 2024) NO se usan.

    C:\\dato-mata-gato-bot\\.venv\\Scripts\\python.exe tools\\guiones_historicos_cancun.py
"""

import json
from pathlib import Path


def plano(pid, seccion, narracion, evidencia, texto):
    return {"id": pid, "seccion": seccion, "narracion": narracion,
            "visual": {"tipo": "archivo_historico", "evidencia": evidencia,
                       "prompt_ia": "", "busqueda_medios": ""},
            "texto_en_pantalla": texto}


def cierre(narracion, texto):
    return {"id": "p08", "seccion": "identidad_cierre", "narracion": narracion,
            "visual": {"tipo": "grafico_movimiento", "descripcion": "Cartel de cierre del canal.",
                       "prompt_ia": "", "busqueda_medios": ""},
            "texto_en_pantalla": texto}


def ficha(fid, titulo, renglones, fuente):
    return {"id": fid, "tipo": "ficha", "titulo": titulo, "renglones": renglones, "fuente": fuente}


def web(eid, tipo, url, fuente):
    return {"id": eid, "tipo": tipo, "url": url, "fuente": fuente}


def foto(eid, tipo, archivo):
    return {"id": eid, "tipo": tipo, "wikimedia": archivo}


GUIONES = {
    # 1 ---------------------------------------------------------------------
    "guion-cancun-aeropuerto-1970": {
        "titulo": "Aeropuerto de Cancún", "gancho": "MENOS VUELOS QUE NUNCA",
        "fuentes": {
            "286_operaciones": "https://www.reportur.com/aerolineas/2026/09/17/cancun-record-negativo-con-menor-cifra-de-vuelos-en-20-anos/ (ASUR: martes 15/09/2026, 286 operaciones; la menor en 20 años salvo pandemia y huracanes; récord ~715)",
            "caida": "https://www.yucatan.com.mx/mexico/2026/09/15/aeropuerto-de-cancun-registra-seis-meses-de-caida-en-pasajeros-internacionales-pierde-845-mil.html (ASUR: agosto -15% internacional; enero-agosto -845,714 internacionales; STARC Anáhuac menciona la crisis de Spirit Airlines)",
            "historia": "https://es.wikipedia.org/wiki/Canc%C3%BAn (estudio de Antonio Enríquez Savignac, 1967; Banco de México e INFRATUR; máquinas desde el 20/04/1970; antes vivían tres familias)",
        },
        "evidencia": [
            web("e1", "prensa", "https://www.yucatan.com.mx/mexico/2026/09/15/aeropuerto-de-cancun-registra-seis-meses-de-caida-en-pasajeros-internacionales-pierde-845-mil.html", "Diario de Yucatán, 15/09/2026"),
            web("e2", "prensa", "https://www.reportur.com/aerolineas/2026/09/17/cancun-record-negativo-con-menor-cifra-de-vuelos-en-20-anos/", "Reportur, 17/09/2026"),
            web("e3", "prensa", "https://solquintanaroo.mx/cancun-pierde-turistas-extranjeros-ante-la-caida-de-vuelos-internacionales/", "Sol Quintana Roo"),
            foto("e4", "lugar", "File:Cancún International Airport 2024a.jpg"),
            foto("e5", "lugar", "File:Zona Hotelera, Cancún, Q.R., Mexico - panoramio (106).jpg"),
            foto("e6", "lugar", "File:Cancún International Airport 2024b.jpg"),
            ficha("f1", "Martes 15 de septiembre de 2026", ["286 operaciones en el aeropuerto de Cancún",
                  "La cifra más baja en 20 años, salvo pandemia y huracanes", "Récord: unas 715"], "ASUR, vía Reportur"),
            ficha("f2", "Pasajeros internacionales", ["Agosto de 2026: 15% menos",
                  "Enero a agosto: 845,714 menos que en 2025"], "ASUR, vía Diario de Yucatán"),
            ficha("f3", "20 de abril de 1970", ["El Banco de México empieza a construir Cancún",
                  "Antes vivían ahí tres familias", "Una ciudad hecha para el turismo"], "Wikipedia: Cancún"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "El quince de septiembre, el aeropuerto de Cancún tuvo su día con menos vuelos en veinte años.", ["f1", "e2"], "MENOS VUELOS QUE NUNCA"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien trabaja en un hotel de la Zona Hotelera viendo cada vez menos maletas. De ese avión depende su quincena.", ["e5", "e4"], "DE ESE AVIÓN DEPENDES"),
            plano("p02", "contexto", "Cancún no creció solo. En mil novecientos sesenta y siete, un estudio de Antonio Enríquez Savignac convenció al Banco de México de crear destinos turísticos.", ["f3", "e5"], "1967"),
            plano("p03", "el_hecho", "El veinte de abril de mil novecientos setenta entraron las primeras máquinas. Antes, ahí vivían tres familias.", ["f3"], "20 DE ABRIL DE 1970"),
            plano("p04", "bucle_abierto", "Ese martes hubo doscientas ochenta y seis operaciones, según ASUR. Hace unos años llegó a haber setecientas quince.", ["f1", "e2"], "286 CONTRA 715"),
            plano("p05", "el_desenlace", "En agosto, los pasajeros internacionales bajaron quince por ciento. De enero a agosto fueron ochocientos cuarenta y cinco mil menos.", ["f2", "e1"], "845 MIL MENOS"),
            plano("p06", "contexto", "Una de las razones que señalan los analistas es la crisis de la aerolínea Spirit.", ["e1", "e6"], "LA CRISIS DE SPIRIT"),
            plano("p07", "cierre_bucle", "Una ciudad que nació para recibir aviones hoy recibe menos. Y eso termina llegando a tu quincena.", ["e4", "f2"], "NACIÓ PARA RECIBIR AVIONES"),
            cierre("Aquí el dato mata al gato. ¿En tu trabajo ya se nota? Cuéntamelo en los comentarios.", "¿YA SE NOTA? COMENTA"),
        ],
    },
    # 2 ---------------------------------------------------------------------
    "guion-cancun-huracan-wilma": {
        "titulo": "Huracanes en Cancún", "gancho": "21 AÑOS DE WILMA",
        "fuentes": {
            "wilma": "https://es.wikipedia.org/wiki/Hurac%C3%A1n_Wilma (21/10/2005, categoría 4; más de 70 horas de vientos de huracán en zonas de la península; 882 hPa, récord que superó a Gilberto 1988 con 888; al menos 8 muertos en México, 1 en Cancún por una ventana)",
            "temporada": "https://quintanaroo.heraldodemexico.com.mx/local/2026/10/3/cuando-termina-la-temporada-de-huracanes-2026-lo-que-falta-para-quintana-roo-17172.html (03/10/2026: termina el 30 de noviembre; 8 tormentas con nombre, ninguna huracán)",
        },
        "evidencia": [
            web("e1", "prensa", "https://quintanaroo.heraldodemexico.com.mx/local/2026/10/3/cuando-termina-la-temporada-de-huracanes-2026-lo-que-falta-para-quintana-roo-17172.html", "Heraldo de México QRoo, 03/10/2026"),
            web("e2", "prensa", "https://www.aztecaquintanaroo.com/noticias/video-hoy-se-cumplen-20-anos-del-paso-del-huracan-wilma-en-cancun/", "Azteca Quintana Roo"),
            foto("e3", "lugar", "File:Hurricane Wilma damage Cancun (59103773).jpg"),
            foto("e4", "lugar", "File:Zona Hotelera, Cancún, Q.R., Mexico - panoramio (116).jpg"),
            foto("e5", "lugar", "File:Avenida Tulum, Cancun, Quintana Roo, Mexico 2021.jpg"),
            ficha("f1", "21 de octubre de 2005 · Wilma", ["Toca tierra como categoría 4",
                  "Más de 70 horas de vientos de huracán en zonas de la península"], "Wikipedia: Huracán Wilma"),
            ficha("f2", "Récord de presión", ["Wilma: 882 hPa", "Superó a Gilberto (1988): 888 hPa"], "Wikipedia: Huracán Wilma"),
            ficha("f3", "Temporada 2026", ["8 tormentas con nombre al 3 de octubre",
                  "Ninguna llegó a huracán", "Termina el 30 de noviembre"], "Heraldo de México QRoo, 03/10/2026"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "Este veintiuno de octubre se cumplen veintiún años de Wilma. Y la temporada de huracanes todavía no termina.", ["e3", "f3"], "21 AÑOS DE WILMA"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien en octubre de dos mil cinco pasó días encerrado en su casa en Cancún, escuchando el viento.", ["e3", "e5"], "DÍAS ENCERRADOS"),
            plano("p02", "contexto", "Wilma tocó tierra el veintiuno de octubre como categoría cuatro. Su ojo pasó por Cozumel.", ["f1", "e2"], "CATEGORÍA 4"),
            plano("p03", "el_hecho", "En zonas de la península hubo vientos de huracán por más de setenta horas seguidas.", ["f1", "e4"], "MÁS DE 70 HORAS"),
            plano("p04", "bucle_abierto", "Su presión, ochocientos ochenta y dos hectopascales, rompió el récord de Gilberto, el huracán de mil novecientos ochenta y ocho.", ["f2", "e3"], "RÉCORD: 882 hPa"),
            plano("p05", "el_desenlace", "En México murieron al menos ocho personas. Una, en Cancún, por una ventana que reventó el viento.", ["e2", "e3"], "AL MENOS 8 MUERTOS"),
            plano("p06", "contexto", "Este año ya van ocho tormentas con nombre en el Atlántico. Ninguna llegó a huracán.", ["f3", "e1"], "8 TORMENTAS"),
            plano("p07", "cierre_bucle", "La temporada termina el treinta de noviembre. Wilma llegó a finales de octubre.", ["e1", "e3"], "TERMINA EL 30 DE NOVIEMBRE"),
            cierre("Aquí el dato mata al gato. ¿Dónde estabas cuando pasó Wilma? Cuéntamelo en los comentarios.", "¿DÓNDE ESTABAS? COMENTA"),
        ],
    },
    # 3 ---------------------------------------------------------------------
    "guion-cancun-punta-nizuc-tajamar": {
        "titulo": "Punta Nizuc y Tajamar", "gancho": "YA PASÓ ANTES",
        "fuentes": {
            "punta_nizuc": "https://www.yucatan.com.mx/mexico/2026/09/09/vecinos-y-ambientalistas-alertan-por-remocion-de-vegetacion-en-predio-de-punta-nizuc-cancun.html y https://solquintanaroo.mx/punta-nizuc-bajo-presion-ambiental/ (Lote 3, Manzana 61; desmonte casi total; colinda con el Parque Nacional Costa Occidental de Isla Mujeres; amparo de 2008 lo sacó del área Manglares de Nichupté; sin irregularidad determinada)",
            "asur": "https://www.poresto.com/quintana-roo/cancun/2026/10/2/asur-tala-vegetacion-en-63-hectareas-para-ampliar-el-aeropuerto-de-cancun.html (63 ha, Terminal 4, Semarnat 2025; Fernando Haro, director de Ecología municipal: restauración de 15 ha en Nichupté)",
            "tajamar": "https://es.wikipedia.org/wiki/Destrucci%C3%B3n_del_manglar_Tajamar_en_2016 (enero de 2016, Fonatur, centro comercial y condominios; cancelación anunciada en junio de 2019). Fecha exacta y hectáreas discrepan entre fuentes: no se dicen.",
        },
        "evidencia": [
            web("e1", "prensa", "https://www.yucatan.com.mx/mexico/2026/09/09/vecinos-y-ambientalistas-alertan-por-remocion-de-vegetacion-en-predio-de-punta-nizuc-cancun.html", "Diario de Yucatán, 09/09/2026"),
            web("e2", "prensa", "https://www.poresto.com/quintana-roo/cancun/2026/10/2/asur-tala-vegetacion-en-63-hectareas-para-ampliar-el-aeropuerto-de-cancun.amp.html", "PorEsto, 02/10/2026"),
            web("e3", "prensa", "https://www.eluniversal.com.mx/articulo/estados/2016/01/20/suspenden-temporalmente-relleno-de-manglares-en-cancun/", "El Universal, 20/01/2016"),
            web("e4", "documento", "https://solquintanaroo.mx/punta-nizuc-bajo-presion-ambiental/", "Sol Quintana Roo, 07/09/2026"),
            foto("e5", "lugar", "File:Punta Nizuc, Cancún, México (34264152672).jpg"),
            foto("e6", "lugar", "File:Tajamar, Cancún. - panoramio.jpg"),
            foto("e7", "lugar", "File:LAGUNA NICHUPTE - panoramio.jpg"),
            ficha("f1", "Punta Nizuc · Lote 3, Manzana 61", ["Septiembre de 2026: desmonte casi total del predio",
                  "Ambientalistas piden revisar si sigue dentro de lo autorizado",
                  "En 2008, un amparo lo sacó del área protegida de Nichupté"], "Diario de Yucatán y Sol Quintana Roo"),
            ficha("f2", "Aeropuerto · 2 de octubre de 2026", ["ASUR taló 63 hectáreas para la Terminal 4",
                  "Permiso de Semarnat en 2025", "Compensación: restaurar 15 hectáreas en Nichupté"], "PorEsto, 02/10/2026"),
            ficha("f3", "Enero de 2016 · Tajamar", ["Máquinas de Fonatur arrasan el manglar",
                  "Para un centro comercial y condominios", "El proyecto se cancela en 2019"], "Wikipedia y El Universal"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "En menos de un mes, Cancún perdió vegetación en Punta Nizuc y junto al aeropuerto. Y ya pasó antes.", ["e5", "e2"], "YA PASÓ ANTES"),
            plano("p01", "hook_tercera_persona", "Te imaginas a los vecinos de Punta Nizuc que en septiembre vieron máquinas dejar casi pelón el lote tres de la manzana sesenta y uno.", ["f1", "e1"], "LOTE 3, MANZANA 61"),
            plano("p02", "contexto", "Ese predio colinda con el Parque Nacional Costa Occidental de Isla Mujeres. En dos mil ocho, un amparo lo sacó del área protegida de los manglares de Nichupté.", ["e4", "e7"], "AMPARO DE 2008"),
            plano("p03", "el_hecho", "Los ambientalistas piden revisar si el desmonte se queda dentro de lo autorizado. La autoridad no ha dicho que haya algo irregular.", ["f1", "e5"], "¿DENTRO DE LO AUTORIZADO?"),
            plano("p04", "bucle_abierto", "Y el dos de octubre se supo que ASUR taló sesenta y tres hectáreas para ampliar la Terminal cuatro, con permiso de Semarnat.", ["f2", "e2"], "63 HECTÁREAS"),
            plano("p05", "el_desenlace", "El director de Ecología municipal, Fernando Haro, dijo que a cambio se restaurarán quince hectáreas de manglar en Nichupté.", ["f2", "e7"], "63 POR 15"),
            plano("p06", "contexto", "No es la primera vez. En enero de dos mil dieciséis, máquinas de Fonatur arrasaron el manglar Tajamar, para un centro comercial y condominios.", ["f3", "e3", "e6"], "TAJAMAR, 2016"),
            plano("p07", "cierre_bucle", "Ese proyecto se canceló hasta dos mil diecinueve. Para entonces, el manglar ya no estaba.", ["e6", "f3"], "EL MANGLAR YA NO ESTABA"),
            cierre("Aquí el dato mata al gato. ¿Qué lugar de Cancún has visto desaparecer? Cuéntamelo en los comentarios.", "¿QUÉ HAS VISTO DESAPARECER?"),
        ],
    },
    # 4 ---------------------------------------------------------------------
    "guion-cancun-sargazo-record": {
        "titulo": "Sargazo en Quintana Roo", "gancho": "RÉCORD OTRA VEZ",
        "fuentes": {
            "record": "https://www.clicnoticias.com.mx/sargazo-qroo-record-133-mil-toneladas-2026/ (29/09/2026, datos de la SEMA: 133,646 t en 2026; ~98,000 en 2025; Cancún 32,179.09 t; Marina 57,497.24 t; hoteleros estiman ~150 millones de dólares al año)",
            "historia": "https://www.uv.mx/cienciauv/blog/el-sargazo-en-las-costa-mexicanas/ y https://www.researchgate.net/publication/339800164 (primeras llegadas masivas al Caribe en 2011; desde 2015, constante en el Caribe mexicano)",
            "nasa": "https://www.poresto.com/quintana-roo/2026/9/21/nasa-advierte-que-el-sargazo-en-el-caribe-mexicano-es-preocupante.html",
        },
        "evidencia": [
            web("e1", "prensa", "https://www.clicnoticias.com.mx/sargazo-qroo-record-133-mil-toneladas-2026/", "Clic Noticias, 29/09/2026"),
            web("e2", "prensa", "https://www.poresto.com/quintana-roo/2026/9/21/nasa-advierte-que-el-sargazo-en-el-caribe-mexicano-es-preocupante.amp.html", "PorEsto, 21/09/2026"),
            web("e3", "documento", "https://www.uv.mx/cienciauv/blog/el-sargazo-en-las-costa-mexicanas/", "Universidad Veracruzana, Ciencia UV"),
            foto("e4", "lugar", "File:Retiro de sargazo en playa de Puerto Morelos.jpg"),
            foto("e5", "lugar", "File:Alga. Praia do hotel Bahía Príncipe - Quintana Roo - México.jpg"),
            foto("e6", "lugar", "File:Zona Hotelera, Cancún, Q.R., Mexico - panoramio (28).jpg"),
            ficha("f1", "Sargazo recogido en 2026", ["Quintana Roo: 133,646 toneladas",
                  "2025: unas 98,000", "Récord por segundo año seguido"], "SEMA, vía Clic Noticias"),
            ficha("f2", "Solo en Cancún", ["32,179 toneladas en 2026"], "SEMA, vía Clic Noticias"),
            ficha("f3", "Desde cuándo", ["2011: primeras llegadas masivas al Caribe",
                  "2015: se vuelve constante en el Caribe mexicano"], "Universidad Veracruzana"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "Este año llegó más sargazo a Quintana Roo que nunca. Y es el segundo año seguido que pasa.", ["f1", "e4"], "RÉCORD OTRA VEZ"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien fue a la playa en Cancún este verano y en lugar de arena blanca encontró una franja café.", ["e5", "e6"], "UNA FRANJA CAFÉ"),
            plano("p02", "contexto", "Hasta finales de septiembre se recogieron ciento treinta y tres mil seiscientas cuarenta y seis toneladas en el estado.", ["f1", "e1"], "133,646 TONELADAS"),
            plano("p03", "el_hecho", "En dos mil veinticinco fueron unas noventa y ocho mil. Este año se rebasó por más de un tercio.", ["f1", "e4"], "MÁS DE UN TERCIO"),
            plano("p04", "bucle_abierto", "Solo en Cancún se retiraron más de treinta y dos mil toneladas.", ["f2", "e6"], "32 MIL EN CANCÚN"),
            plano("p05", "el_desenlace", "Y esto no siempre fue así. Las primeras llegadas masivas de sargazo al Caribe se registraron en dos mil once.", ["f3", "e3"], "DESDE 2011"),
            plano("p06", "contexto", "Desde dos mil quince, verlo en estas playas se volvió costumbre. Según los hoteleros, quitarlo cuesta unos ciento cincuenta millones de dólares al año.", ["f3", "e2"], "150 MILLONES DE DÓLARES"),
            plano("p07", "cierre_bucle", "Dos récords seguidos. Y el sargazo todavía no se va.", ["e4", "f1"], "DOS RÉCORDS SEGUIDOS"),
            cierre("Aquí el dato mata al gato. ¿Cómo estuvo tu playa este año? Cuéntamelo en los comentarios.", "¿CÓMO ESTUVO TU PLAYA?"),
        ],
    },
    # 5 ---------------------------------------------------------------------
    "guion-cancun-laguna-nichupte": {
        "titulo": "Laguna Nichupté", "gancho": "LO QUE HAY BAJO EL PUENTE",
        "fuentes": {
            "barcos": "https://www.poresto.com/quintana-roo/cancun/2026/9/24/retiran-14-embarcaciones-abandonadas-de-la-laguna-nichupte-tras-anos-de-reclamos.html (24/09/2026: 14 retiradas; 45 a 50 abandonadas; casi tres años de reclamos; algunas con combustible; tres etapas hasta diciembre; municipio, Asociados Náuticos, Capitanía de Puerto, Conanp)",
            "drenaje": "https://24horasqroo.mx/2026/07/22/zona-hotelera-cancun-laguna-nichpte/ (22/07/2026: estudio de AyMA para el municipio: 9 tubos activos de aguas residuales; drenaje diseñado hace casi 50 años; activista Antonella Vázquez Cavedon)",
            "historia": "https://es.wikipedia.org/wiki/Canc%C3%BAn (los arquitectos Enrique y Agustín Landa Verdugo diseñaron la zona hotelera en la isla y la ciudad en tierra firme)",
        },
        "evidencia": [
            web("e1", "prensa", "https://www.poresto.com/quintana-roo/cancun/2026/9/24/retiran-14-embarcaciones-abandonadas-de-la-laguna-nichupte-tras-anos-de-reclamos.amp.html", "PorEsto, 24/09/2026"),
            web("e2", "prensa", "https://24horasqroo.mx/2026/07/22/zona-hotelera-cancun-laguna-nichpte/", "24 Horas Quintana Roo, 22/07/2026"),
            web("e3", "prensa", "https://www.clicnoticias.com.mx/barcos-abandonados-laguna-nichupte-cancun/", "Clic Noticias"),
            foto("e4", "lugar", "File:LAGUNA NICHUPTE - panoramio.jpg"),
            foto("e5", "lugar", "File:Playa de Cancún y La Laguna Nichupté YEYSUPER.jpg"),
            foto("e6", "lugar", "File:CANCUN - Mexico (Hotel Hotetur Beach Paradise) - Nichupte Laguna - panoramio.jpg"),
            ficha("f1", "Laguna Nichupté · septiembre de 2026", ["14 barcos abandonados retirados",
                  "Hay entre 45 y 50", "Algunos todavía sueltan combustible"], "PorEsto, 24/09/2026"),
            ficha("f2", "Estudio para el municipio", ["9 tubos descargan aguas residuales a la laguna",
                  "Drenaje de la Zona Hotelera: diseñado hace casi 50 años"], "24 Horas Quintana Roo, 22/07/2026"),
            ficha("f3", "Años setenta", ["Enrique y Agustín Landa Verdugo diseñan Cancún",
                  "Hoteles en la isla, entre el mar y la laguna"], "Wikipedia: Cancún"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "En septiembre sacaron catorce barcos abandonados de la laguna Nichupté. Quedan más de treinta.", ["f1", "e1"], "QUEDAN MÁS DE 30"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien cruza el nuevo puente sobre la laguna y no sabe lo que hay abajo.", ["e4", "e5"], "LO QUE HAY ABAJO"),
            plano("p02", "contexto", "Algunos barcos todavía sueltan combustible al agua. Sacarlos costó casi tres años de reclamos.", ["f1", "e3"], "TRES AÑOS DE RECLAMOS"),
            plano("p03", "el_hecho", "La laguna quedó en medio desde el principio. En los setenta, los arquitectos Enrique y Agustín Landa Verdugo pusieron los hoteles entre el mar y la laguna.", ["f3", "e6"], "AÑOS SETENTA"),
            plano("p04", "bucle_abierto", "El drenaje de esa zona se diseñó hace casi cincuenta años, para mucha menos gente.", ["f2", "e2"], "CASI 50 AÑOS"),
            plano("p05", "el_desenlace", "Un estudio hecho para el municipio encontró nueve tubos que descargan aguas residuales a la laguna.", ["f2", "e2"], "9 TUBOS DE AGUAS NEGRAS"),
            plano("p06", "contexto", "La activista Antonella Vázquez Cavedon lo dice así: desde hace años, la Zona Hotelera ya no soporta más carga.", ["e2", "e4"], "YA NO SOPORTA MÁS"),
            plano("p07", "cierre_bucle", "El retiro de barcos sigue hasta diciembre. De los tubos, nadie ha dicho cuándo.", ["e1", "f2"], "¿Y LOS TUBOS?"),
            cierre("Aquí el dato mata al gato. ¿Te meterías a nadar a la laguna? Cuéntamelo en los comentarios.", "¿TE METERÍAS? COMENTA"),
        ],
    },
    # 6 ---------------------------------------------------------------------
    "guion-cancun-tren-maya": {
        "titulo": "Tren Maya en Cancún", "gancho": "NO LO USAN LOS TURISTAS",
        "fuentes": {
            "informe": "https://diario.mx/nacional/2026/sep/03/batea-a-tren-maya-turismo-extranjero-1136434.html (03/09/2026, Segundo Informe de Gobierno: sep 2025 a jun 2026, 1,055,791 pasajeros; 89,920 internacionales = 8.5%; primer tramo inaugurado el 15/12/2023; proyección 140 mil millones, más de 500 mil millones)",
            "percance": "https://www.poresto.com/campeche/2026/8/31/confirma-tren-maya-percance-del-tren-que-cubria-la-ruta-cancunpalenque-no-se-reportaron-personas-lesionadas.html (31/08/2026: percance de vía, ruta Cancún-Palenque, 123 pasajeros, sin lesionados)",
        },
        "evidencia": [
            web("e1", "prensa", "https://diario.mx/nacional/2026/sep/03/batea-a-tren-maya-turismo-extranjero-1136434.html", "El Diario, 03/09/2026"),
            web("e2", "prensa", "https://www.poresto.com/campeche/2026/8/31/confirma-tren-maya-percance-del-tren-que-cubria-la-ruta-cancunpalenque-no-se-reportaron-personas-lesionadas.amp.html", "PorEsto, 31/08/2026"),
            web("e3", "prensa", "https://www.elfinanciero.com.mx/empresas/2025/09/23/tren-maya-en-via-muerta-costara-mas-en-2026-y-seguira-sin-ser-rentable-segun-el-ppef/", "El Financiero, 23/09/2025"),
            foto("e4", "lugar", "File:Tren Maya Estación Cancún Piso Superior.jpg"),
            foto("e5", "lugar", "File:Señal de Estacion Cancún Tren Maya.jpg"),
            foto("e6", "persona", "File:Claudia Sheinbaum Pardo en Guadalajara en campaña 2024.jpg"),
            ficha("f1", "Septiembre 2025 a junio 2026", ["1,055,791 pasajeros",
                  "Extranjeros: 89,920 (8.5%)", "9 de cada 10 son nacionales"], "Segundo Informe de Gobierno, vía El Diario"),
            ficha("f2", "15 de diciembre de 2023", ["Se inaugura el primer tramo",
                  "Proyección: 140 mil millones de pesos", "Hoy, más de 500 mil millones"], "El Diario, 03/09/2026"),
            ficha("f3", "31 de agosto de 2026", ["Percance de vía en la ruta Cancún–Palenque",
                  "123 pasajeros, sin lesionados"], "PorEsto, 31/08/2026"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "El Tren Maya se vendió para atraer turistas extranjeros. Nueve de cada diez pasajeros son de aquí.", ["f1", "e4"], "NO LO USAN LOS TURISTAS"),
            plano("p01", "hook_tercera_persona", "Te imaginas a una familia de Cancún que toma el tren para ir a Mérida un fin de semana. Es más probable que el pasajero seas tú que un extranjero.", ["e5", "e4"], "EL PASAJERO ERES TÚ"),
            plano("p02", "contexto", "El primer tramo se inauguró el quince de diciembre de dos mil veintitrés.", ["f2", "e4"], "15 DE DICIEMBRE DE 2023"),
            plano("p03", "el_hecho", "Se proyectó en ciento cuarenta mil millones de pesos. Según El Diario, ya cuesta más de quinientos mil millones.", ["f2", "e1"], "DE 140 A 500 MIL MILLONES"),
            plano("p04", "bucle_abierto", "De septiembre de dos mil veinticinco a junio de dos mil veintiséis, llevó a un millón cincuenta y cinco mil pasajeros.", ["f1", "e1"], "1 MILLÓN 55 MIL"),
            plano("p05", "el_desenlace", "Extranjeros, solo ochenta y nueve mil novecientos veinte. Lo dice el Segundo Informe de Gobierno de Claudia Sheinbaum.", ["e6", "f1"], "SOLO 8.5% EXTRANJEROS"),
            plano("p06", "contexto", "Y el treinta y uno de agosto, el tren de la ruta Cancún Palenque tuvo un percance en la vía. No hubo heridos.", ["f3", "e2"], "31 DE AGOSTO"),
            plano("p07", "cierre_bucle", "Un tren hecho para turistas extranjeros, que usan sobre todo los de aquí.", ["e4", "f1"], "LO USAN LOS DE AQUÍ"),
            cierre("Aquí el dato mata al gato. ¿Ya te subiste al Tren Maya? Cuéntamelo en los comentarios.", "¿YA TE SUBISTE? COMENTA"),
        ],
    },
}

for slug, d in GUIONES.items():
    guion = {
        "_schema": {"descripcion": "Short de Dato Mata Gato: noticia reciente de Cancún con trasfondo "
                                   "histórico. Fórmula y estilo de /lotefish3.",
                    "fuentes": d["fuentes"]},
        "titulo": d["titulo"], "gancho": d["gancho"],
        "hashtags": ["#DatoMataGato", "#Cancun", "#QuintanaRoo"],
        "evidencia": d["evidencia"], "planos": d["planos"],
    }
    carpeta = Path(r"C:\Android_in") / slug
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / "guion.json").write_text(json.dumps(guion, ensure_ascii=False, indent=2), encoding="utf-8")
    palabras = sum(len(p["narracion"].split()) for p in d["planos"])
    print(f"{slug}: {palabras} palabras")
