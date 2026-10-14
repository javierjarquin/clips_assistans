"""Segunda tanda de diez guiones de Cancún (10/10/2026): noticia de esta semana
+ trasfondo histórico + cercanía. Misma fórmula que guiones_cancun_cercania.py.

Cada dato salió de una nota o documento que se abrió y leyó. Lo que solo dice un
medio va atribuido en la narración. NO se usan: el día exacto en que se firmó el
acuerdo de la gasolina (las fuentes no coinciden), el año en que el 12 de octubre
empezó a llamarse Día de la Raza (tres versiones distintas), la recaudación del
Visitax (el periodo no está claro) ni las cifras de cáncer de mama (las notas se
contradicen; por eso ese tema se cambió por otro).

    C:\\dato-mata-gato-bot\\.venv\\Scripts\\python.exe tools\\guiones_cancun_cercania2.py
"""

import json
from pathlib import Path


def plano(pid, seccion, narracion, evidencia, texto):
    return {"id": pid, "seccion": seccion, "narracion": narracion,
            "visual": {"tipo": "archivo_historico", "evidencia": evidencia, "prompt_ia": "",
                       "busqueda_medios": "", "motion": "calm"},
            "texto_en_pantalla": texto}


def cierre(narracion, texto):
    return {"id": "p08", "seccion": "identidad_cierre", "narracion": narracion,
            "visual": {"tipo": "grafico_movimiento", "descripcion": "Cartel de cierre del canal.",
                       "prompt_ia": "", "busqueda_medios": ""},
            "texto_en_pantalla": texto}


def ficha(fid, titulo, renglones, fuente):
    return {"id": fid, "tipo": "ficha", "titulo": titulo, "renglones": renglones, "fuente": fuente}


def web(eid, tipo, url, fuente, **extra):
    return {"id": eid, "tipo": tipo, "url": url, "fuente": fuente, **extra}


def foto(eid, tipo, archivo):
    return {"id": eid, "tipo": tipo, "wikimedia": archivo}


def buscar(eid, tipo, consulta):
    return {"id": eid, "tipo": tipo, "buscar_wikimedia": consulta}


ZH = "File:Zona Hotelera, Cancún, Q.R., Mexico - panoramio (106).jpg"
CENTRO = "File:Calle Margaritas, Sm. 22, Col. Centro, Cancún - panoramio.jpg"
TULUM = "File:Avenida Tulum, Cancun, Quintana Roo, Mexico 2021.jpg"
YAXCHILAN = "File:Avenida Yaxchilan at night in Cancun, Mexico.jpg"
SHEINBAUM = "File:Claudia Sheinbaum 2025 (cropped).jpg"

GUIONES = {
    "guion-cancun-quintana-roo-52-anos": {
        "titulo": "Quintana Roo cumple 52 años", "gancho": "CANCÚN ES MÁS VIEJO", "claves": ["quintana roo", "cancun"],
        "fuentes": {
            "aniversario": "https://www.cancunmio.com/42274186-quintana-roo-cumple-52-anos-como-estado-libre-y-soberano/ (08/10/2026: sesión solemne en Chetumal; Jorge Sanén Cervantes leyó el decreto)",
            "historia": "https://es.wikipedia.org/wiki/Quintana_Roo (8 de octubre de 1974 estado libre y soberano; territorio por decreto del 24/11/1902; 14/12/1931 anexado a Yucatán y Campeche; recreado por Lázaro Cárdenas, DOF 16/01/1935; gobernador provisional David Gustavo Gutiérrez Ruiz)",
            "cancun": "https://politica.expansion.mx/estados/2019/08/20/cancun-se-alista-a-celebrar-a-lo-grande-su-medio-siglo-de-historia (obras desde abril de 1970; decreto de fundación en el DOF del 10/08/1971)",
            "poblacion": "https://grupoanimal.mx/quintana-roo/sociedad/mitad-habitantes-quintana-roo-nacio-fuera-inegi (24/09/2026, Encuesta Intercensal 2025 del INEGI: 2,095,074 habitantes; 49.2% nació en otra entidad o país)",
        },
        "evidencia": [
            web("e1", "prensa", "https://www.cancunmio.com/42274186-quintana-roo-cumple-52-anos-como-estado-libre-y-soberano/", "Cancún Mío, 08/10/2026"),
            web("e2", "prensa", "https://grupoanimal.mx/quintana-roo/sociedad/mitad-habitantes-quintana-roo-nacio-fuera-inegi", "Grupo Animal, 24/09/2026"),
            web("e3", "prensa", "https://politica.expansion.mx/estados/2019/08/20/cancun-se-alista-a-celebrar-a-lo-grande-su-medio-siglo-de-historia", "Expansión, 20/08/2019"),
            foto("e4", "lugar", "File:PlanMaestroCun.jpg"),
            foto("e5", "lugar", "File:Palacio de Gobierno, Chetumal, Q. Roo. - panoramio.jpg"),
            foto("e6", "lugar", "File:Cancun from the air July 1985.jpg"),
            ficha("f1", "Quintana Roo", ["1902: se crea el territorio federal", "1931: lo reparten entre Yucatán y Campeche",
                  "1935: Lázaro Cárdenas lo vuelve a crear", "8 de octubre de 1974: estado libre y soberano"], "Wikipedia: Quintana Roo"),
            ficha("f2", "Cancún", ["Abril de 1970: empiezan las obras", "10 de agosto de 1971: decreto de fundación en el Diario Oficial",
                  "Cuatro años antes que el estado"], "Expansión, 20/08/2019"),
            ficha("f3", "Quintana Roo hoy", ["2,095,074 habitantes", "49.2% nació en otro estado o en otro país"],
                  "INEGI, Encuesta Intercensal 2025, vía Grupo Animal"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "Cancún empezó a construirse antes de que Quintana Roo fuera estado. Este ocho de octubre, en Chetumal, se celebraron los cincuenta y dos años del estado.", ["f2", "e4"], "CANCÚN ES MÁS VIEJO"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien llegó a Cancún desde otro estado, con una maleta y sin conocer a nadie. Casi la mitad de los que viven en Quintana Roo nació en otro lugar.", ["f3", "e2"], "CASI LA MITAD"),
            plano("p02", "contexto", "Según el INEGI, cuarenta y nueve punto dos por ciento de los habitantes del estado nació en otra entidad o en otro país.", ["f3", "e2"], "49.2%"),
            plano("p03", "el_hecho", "Las obras de Cancún arrancaron en abril de mil novecientos setenta. El decreto de fundación salió en el Diario Oficial en agosto de mil novecientos setenta y uno.", ["f2", "e3"], "1970"),
            plano("p04", "bucle_abierto", "Quintana Roo era un territorio federal desde mil novecientos dos. En mil novecientos treinta y uno lo desaparecieron y lo repartieron entre Yucatán y Campeche.", ["f1", "e5"], "LO DESAPARECIERON"),
            plano("p05", "el_desenlace", "Lázaro Cárdenas lo volvió a crear en mil novecientos treinta y cinco. Y el ocho de octubre de mil novecientos setenta y cuatro se convirtió en estado libre y soberano.", ["f1", "e1"], "8 DE OCTUBRE DE 1974"),
            plano("p06", "contexto", "Su primer gobernador fue provisional: David Gustavo Gutiérrez Ruiz. Este año, el decreto se volvió a leer en el Congreso, en Chetumal.", ["e5", "e1"], "52 AÑOS"),
            plano("p07", "cierre_bucle", "Hoy el estado tiene más de dos millones de habitantes. Y una de cada dos personas llegó de fuera, como Cancún.", ["e6", "f3"], "UNA DE CADA DOS"),
            cierre("Aquí el dato mata al gato. ¿Tú de dónde llegaste a Cancún? Cuéntamelo en los comentarios.", "¿DE DÓNDE LLEGASTE?"),
        ],
    },
    "guion-cancun-gasolina-2539": {
        "titulo": "Gasolina en Cancún", "gancho": "25.39 EL LITRO", "claves": ["gasolina", "magna"],
        "fuentes": {
            "precio": "https://www.poresto.com/quintana-roo/cancun/2026/9/29/gasolina-en-cancun-alcanza-2539-pesos-por-litro-y-golpea-al-bolsillo-de-los-automovilistas.html (29/09/2026, Profeco: Go Gas de la av. 20 de Noviembre, Región 227, 25.39; margen 2.86, el más alto de ocho regiones; Oxxo Gas a 24.99 en Aguascalientes, Toluca y Monterrey; testimonio de José Manuel Pineda)",
            "abril": "https://www.poresto.com/quintana-roo/2026/4/8/mas-de-200-estaciones-de-servicio-en-quintana-roo-incumplen-el-acuerdo-nacional-del-precio-de-la-gasolina.html (abril 2026: 197 estaciones arriba de 24; solo tres cumplen: Cancún SM 84, Playa del Carmen y Bacalar)",
            "acuerdo": "https://www.poresto.com/mexico/2026/8/31/presidenta-sheinbaum-renueva-acuerdo-con-gasolineros-para-mantener-gasolina-magna-debajo-de-24-pesos.html (renovación del 31/08/2026; acuerdo voluntario desde febrero de 2025)",
        },
        "evidencia": [
            web("e1", "prensa", "https://www.poresto.com/quintana-roo/cancun/2026/9/29/gasolina-en-cancun-alcanza-2539-pesos-por-litro-y-golpea-al-bolsillo-de-los-automovilistas.amp.html", "PorEsto, 29/09/2026"),
            web("e2", "prensa", "https://www.poresto.com/quintana-roo/2026/4/8/mas-de-200-estaciones-de-servicio-en-quintana-roo-incumplen-el-acuerdo-nacional-del-precio-de-la-gasolina.amp.html", "PorEsto, 08/04/2026"),
            web("e3", "prensa", "https://www.poresto.com/mexico/2026/8/31/presidenta-sheinbaum-renueva-acuerdo-con-gasolineros-para-mantener-gasolina-magna-debajo-de-24-pesos.amp.html", "PorEsto, 31/08/2026"),
            foto("e4", "persona", SHEINBAUM), foto("e5", "lugar", TULUM), foto("e6", "lugar", YAXCHILAN),
            ficha("f1", "Septiembre de 2026 · Cancún", ["Magna: 25.39 pesos por litro", "Avenida 20 de Noviembre, Región 227",
                  "El margen más alto de 8 regiones"], "Profeco, vía PorEsto, 29/09/2026"),
            ficha("f2", "El acuerdo", ["Desde febrero de 2025: Magna por debajo de 24 pesos", "Es voluntario",
                  "31 de agosto de 2026: se renueva otra vez"], "PorEsto"),
            ficha("f3", "Abril de 2026 · Quintana Roo", ["197 gasolineras arriba de 24 pesos", "Solo 3 cumplían",
                  "Una en Cancún: Supermanzana 84"], "Profeco, vía PorEsto, 08/04/2026"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "En Cancún, el litro de Magna ya llegó a veinticinco pesos con treinta y nueve centavos. Y existe un acuerdo para que no pase de veinticuatro.", ["f1", "e1"], "25.39 EL LITRO"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien reparte en moto en Cancún y carga gasolina todos los días.", ["e5", "e1"], "TODOS LOS DÍAS"),
            plano("p02", "contexto", "José Manuel Pineda es repartidor. Se lo dijo así a PorEsto: sí, ya nos pesa, porque le tenemos que echar todos los días.", ["e1", "e6"], "YA NOS PESA"),
            plano("p03", "el_hecho", "Según la Profeco, una gasolinera de la avenida veinte de Noviembre vendía a veinticinco treinta y nueve, con el margen más alto de las ocho regiones que revisó.", ["f1", "e1"], "EL MARGEN MÁS ALTO"),
            plano("p04", "bucle_abierto", "El acuerdo para que la Magna no pase de veinticuatro pesos existe desde febrero de dos mil veinticinco. Es voluntario.", ["f2", "e3"], "ES VOLUNTARIO"),
            plano("p05", "el_desenlace", "En abril, ciento noventa y siete gasolineras de Quintana Roo vendían arriba de veinticuatro. Solo tres cumplían, y una estaba en Cancún.", ["f3", "e2"], "SOLO 3 CUMPLÍAN"),
            plano("p06", "contexto", "El treinta y uno de agosto, Claudia Sheinbaum renovó el acuerdo con los gasolineros por seis meses más.", ["e4", "e3"], "SE RENOVÓ"),
            plano("p07", "cierre_bucle", "En Monterrey o en Toluca hay gasolina a veinticuatro noventa y nueve. Aquí, cada tanque de cincuenta litros sale unos veinte pesos más caro.", ["e1", "f1"], "20 PESOS MÁS"),
            cierre("Aquí el dato mata al gato. ¿A cuánto cargaste esta semana? Cuéntamelo en los comentarios.", "¿A CUÁNTO CARGASTE?"),
        ],
    },
    "guion-cancun-acuifero-maya": {
        "titulo": "El acuífero maya", "gancho": "EL AGUA DE TU LLAVE", "claves": ["acuifero", "cuevas", "cenotes"],
        "fuentes": {
            "anp": "https://quintanaroo.heraldodemexico.com.mx/local/2026/10/9/avanza-al-80-la-propuesta-tecnica-para-decretar-el-acuifero-maya-como-area-natural-protegida-17282.html (09/10/2026: Pedro Álvarez Icaza, Conanp; 80%; 2.5 millones de hectáreas subterráneas en tres estados; consulta pública antes de terminar 2026; decreto en 2027; cita textual)",
            "aguakan": "https://www2.aguakan.com/docs/Informe%20de%20Sostenibilidad%202025_%20Aguakan.pdf (p. 7: 185 pozos abastecen a Cancún e Isla Mujeres; se extrae agua del subsuelo)",
            "tren": "https://www.elfinanciero.com.mx/nacional/2024/01/24/tren-maya-ambientalistas-alertan-ecocidio-en-cuevas-y-cenotes-por-obras-del-tramo-5/ (24/01/2024, AP: Guillermo DChristy, Aktun Túyul cerca de Xpu Ha; \"al menos 12 grandes perforaciones\")",
        },
        "evidencia": [
            web("e1", "prensa", "https://quintanaroo.heraldodemexico.com.mx/local/2026/10/9/avanza-al-80-la-propuesta-tecnica-para-decretar-el-acuifero-maya-como-area-natural-protegida-17282.html", "Heraldo de México QRoo, 09/10/2026"),
            web("e2", "documento", "https://www2.aguakan.com/docs/Informe%20de%20Sostenibilidad%202025_%20Aguakan.pdf", "Aguakan, Informe de Sostenibilidad 2025", pagina=7, desde=0.6, fraccion=0.82),
            web("e3", "prensa", "https://www.elfinanciero.com.mx/nacional/2024/01/24/tren-maya-ambientalistas-alertan-ecocidio-en-cuevas-y-cenotes-por-obras-del-tramo-5/", "El Financiero, 24/01/2024"),
            web("e4", "prensa", "https://grupoanimal.mx/politica/tren-maya-danos-cuevas-cenotes", "Grupo Animal"),
            foto("e5", "lugar", "File:Carwash Cenote Quintana Roo Feb 2020.jpg"),
            foto("e6", "lugar", "File:Cenote, Solidaridad, Quintana Roo, Mexico, Mayo 2011.jpg"),
            ficha("f1", "Acuífero maya", ["Propuesta de Área Natural Protegida: 80% lista", "2.5 millones de hectáreas bajo tierra",
                  "Quintana Roo, Yucatán y Campeche"], "Conanp, vía Heraldo de México QRoo, 09/10/2026"),
            ficha("f2", "El agua de Cancún", ["185 pozos abastecen a Cancún e Isla Mujeres", "Se saca del subsuelo"],
                  "Aguakan, Informe de Sostenibilidad 2025, p. 7"),
            ficha("f3", "Enero de 2024 · Tramo 5 del Tren Maya", ["Espeleólogos denuncian pilotes dentro de cuevas",
                  "\"Al menos 12 grandes perforaciones\"", "Cueva Aktun Túyul, cerca de Xpu Ha"], "El Financiero, con AP"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "El agua que sale de tu llave en Cancún viene de debajo de la tierra. Y apenas ahora la quieren declarar área protegida.", ["f2", "e5"], "EL AGUA DE TU LLAVE"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien abre la llave en su casa en Cancún sin saber que esa agua viene de ríos que corren bajo la selva.", ["e6", "f2"], "RÍOS BAJO LA SELVA"),
            plano("p02", "contexto", "Según Aguakan, ciento ochenta y cinco pozos abastecen a Cancún e Isla Mujeres. Toda esa agua se saca del subsuelo.", ["f2", "e2"], "185 POZOS"),
            plano("p03", "el_hecho", "El nueve de octubre, Pedro Álvarez Icaza, de la Conanp, dijo que la propuesta para proteger el acuífero maya va al ochenta por ciento.", ["f1", "e1"], "AL 80%"),
            plano("p04", "bucle_abierto", "Serían dos millones y medio de hectáreas bajo tierra, en Quintana Roo, Yucatán y Campeche. Él mismo lo dijo: no es una reserva fácil, porque estamos reservando subsuelo.", ["f1", "e1"], "RESERVAR EL SUBSUELO"),
            plano("p05", "el_desenlace", "La consulta pública sería antes de que termine este año. El decreto, en dos mil veintisiete.", ["e1", "e5"], "DECRETO EN 2027"),
            plano("p06", "contexto", "En enero de dos mil veinticuatro, el espeleólogo Guillermo DChristy grabó pilotes del tren atravesando una cueva. Fue en el tramo cinco, cerca de Xpu Ha, y habló de al menos doce grandes perforaciones.", ["f3", "e3"], "12 PERFORACIONES"),
            plano("p07", "cierre_bucle", "Las cuevas ya tienen pilotes. La protección todavía no tiene decreto.", ["e4", "f1"], "SIN DECRETO"),
            cierre("Aquí el dato mata al gato. ¿Tú tomas agua de la llave o de garrafón? Cuéntamelo en los comentarios.", "¿LLAVE O GARRAFÓN?"),
        ],
    },
    "guion-cancun-abrir-negocio": {
        "titulo": "Abrir un negocio en Cancún", "gancho": "51 MIL EN PERMISOS", "claves": ["negocio", "permisos"],
        "fuentes": {
            "permisos": "https://www.poresto.com/quintana-roo/cancun/2026/9/28/abrir-un-negocio-formal-en-cancun-puede-costar-hasta-51-mil-pesos-solo-en-permisos.html (28/09/2026: hasta 51,328 pesos; licencia de funcionamiento 19,355; análisis de agua residual 7,200; basura 6,888; anuncios 5,812; uso de suelo 3,733; Protección Civil 1,585; Canaco-Servytur: 6 de cada 10 comercios informales y 386 cierres en el primer semestre; cita de comerciante anónimo)",
        },
        "evidencia": [
            web("e1", "prensa", "https://www.poresto.com/quintana-roo/cancun/2026/9/28/abrir-un-negocio-formal-en-cancun-puede-costar-hasta-51-mil-pesos-solo-en-permisos.amp.html", "PorEsto, 28/09/2026"),
            foto("e2", "lugar", "File:Mercado 28 Cancun, Mexico Julio 2012 - 01.jpg"),
            foto("e3", "lugar", "File:Mercado 28, Cancún 2014.jpg"),
            foto("e4", "lugar", CENTRO), foto("e5", "lugar", TULUM),
            ficha("f1", "Abrir un negocio en Cancún", ["Licencia de funcionamiento: 19,355 pesos", "Análisis de agua residual: 7,200",
                  "Basura: 6,888 · Anuncios: 5,812", "Uso de suelo: 3,733 · Protección Civil: 1,585"], "PorEsto, 28/09/2026"),
            ficha("f2", "Comercio en Cancún", ["6 de cada 10 comercios, en la informalidad",
                  "386 cierres definitivos en el primer semestre de 2026"], "Canaco-Servytur, vía PorEsto"),
            ficha("f3", "Un comerciante", ["\"Te exigen la terminación de obra del local que ocupes\""], "PorEsto, 28/09/2026"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "Abrir un negocio formal en Cancún puede costar hasta cincuenta y un mil pesos, solo en permisos.", ["f1", "e1"], "51 MIL EN PERMISOS"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien junta sus ahorros para poner una tiendita o una fonda en su colonia de Cancún, y antes de vender el primer taco ya debe miles.", ["e4", "e2"], "ANTES DEL PRIMER TACO"),
            plano("p02", "contexto", "Según PorEsto, solo la licencia de funcionamiento cuesta diecinueve mil trescientos cincuenta y cinco pesos.", ["f1", "e1"], "19,355 LA LICENCIA"),
            plano("p03", "el_hecho", "Luego vienen el análisis de agua residual, la recolección de basura, los anuncios, el uso de suelo y Protección Civil.", ["f1", "e3"], "Y LUEGO, TODO LO DEMÁS"),
            plano("p04", "bucle_abierto", "Un comerciante lo resumió así: para sacar hoy la licencia, te exigen la terminación de obra del local que ocupes.", ["f3", "e1"], "TERMINACIÓN DE OBRA"),
            plano("p05", "el_desenlace", "Según la Canaco, seis de cada diez comercios en Cancún operan en la informalidad.", ["f2", "e2"], "6 DE CADA 10"),
            plano("p06", "contexto", "Y en el primer semestre de dos mil veintiséis cerraron para siempre trescientos ochenta y seis micro y pequeños negocios.", ["f2", "e5"], "386 CIERRES"),
            plano("p07", "cierre_bucle", "Abrir en regla cuesta hasta cincuenta y un mil pesos. Y la mayoría de los comercios de Cancún no está en regla.", ["e4", "f1"], "LA MAYORÍA, SIN REGLA"),
            cierre("Aquí el dato mata al gato. ¿Tienes negocio? ¿Cuánto te costó abrirlo? Cuéntamelo en los comentarios.", "¿CUÁNTO TE COSTÓ?"),
        ],
    },
    "guion-cancun-dnr-turistas": {
        "titulo": "El cobro a turistas extranjeros", "gancho": "DE 861 A 1,334", "claves": ["dnr", "no residente"],
        "fuentes": {
            "propuesta": "https://noticaribe.com.mx/2026/10/09/empresarios-de-quintana-roo-llevan-a-san-lazaro-rechazo-al-alza-del-dnr-alertan-sobre-perdida-de-competitividad-turistica/ (09/10/2026: de 983 a 1,334.80 en el Paquete Económico 2027; Valeria Rindertsma, AMEXME Riviera Maya, en la Comisión de Hacienda; 508,819 visitantes menos en el primer semestre según el sector)",
            "hoteleros": "https://grupoanimal.mx/quintana-roo/economia/hoteleros-rechazan-aumento-derecho-de-no-residente-quintana-roo (18/09/2026: 861 pesos en 2025; alza acumulada cercana a 55%; Raúl Andrade Angulo; CHCM)",
            "2019": "https://expansion.mx/empresas/2021/11/18/empresarios-piden-recursos-dnr-promocion-tren-maya (el DNR dejó de ir a la promoción turística y se fue al Tren Maya tras extinguirse el CPTM en 2019)",
        },
        "evidencia": [
            web("e1", "prensa", "https://noticaribe.com.mx/2026/10/09/empresarios-de-quintana-roo-llevan-a-san-lazaro-rechazo-al-alza-del-dnr-alertan-sobre-perdida-de-competitividad-turistica/", "Noticaribe, 09/10/2026"),
            web("e2", "prensa", "https://grupoanimal.mx/quintana-roo/economia/hoteleros-rechazan-aumento-derecho-de-no-residente-quintana-roo", "Grupo Animal, 18/09/2026"),
            web("e3", "prensa", "https://expansion.mx/empresas/2021/11/18/empresarios-piden-recursos-dnr-promocion-tren-maya", "Expansión, 18/11/2021"),
            foto("e4", "lugar", ZH), foto("e5", "lugar", "File:Cancun aerial photo by safa.jpg"), foto("e6", "lugar", "File:MMUN001.jpg"),
            ficha("f1", "Derecho de No Residente", ["2025: 861 pesos", "2026: 983 pesos", "Propuesta para 2027: 1,334.80"],
                  "Grupo Animal y Noticaribe"),
            ficha("f2", "Los hoteleros", ["Casi 55% más en dos años", "Primer semestre de 2026: 508,819 visitantes menos, según el sector"],
                  "Consejo Hotelero del Caribe Mexicano y AMEXME"),
            ficha("f3", "2019", ["Desaparece el Consejo de Promoción Turística", "Lo que se cobra a los turistas se va al Tren Maya"],
                  "Expansión, 18/11/2021"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "A cada turista extranjero que llega a México le quieren cobrar mil trescientos treinta y cuatro pesos en dos mil veintisiete. En Cancún, los hoteleros ya están preocupados.", ["f1", "e1"], "1,334 PESOS"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien trabaja de mesero o de camarista en Cancún, y su propina depende de cuántos turistas lleguen.", ["e4", "e5"], "TU PROPINA"),
            plano("p02", "contexto", "Se llama Derecho de No Residente. En dos mil veinticinco eran ochocientos sesenta y un pesos. Hoy son novecientos ochenta y tres.", ["f1", "e2"], "DE 861 A 983"),
            plano("p03", "el_hecho", "El Paquete Económico de dos mil veintisiete propone subirlo a mil trescientos treinta y cuatro pesos con ochenta. Casi cincuenta y cinco por ciento más en dos años.", ["f1", "e1"], "CASI 55% MÁS"),
            plano("p04", "bucle_abierto", "Valeria Rindertsma preside a las mujeres empresarias de la Riviera Maya. Ella llevó el rechazo a la Cámara de Diputados.", ["e1", "e6"], "A SAN LÁZARO"),
            plano("p05", "el_desenlace", "Según el sector, en el primer semestre llegaron quinientos ocho mil visitantes menos. Ellos mismos aclaran que no todo es por este cobro.", ["f2", "e1"], "508 MIL MENOS"),
            plano("p06", "contexto", "Y hay un fondo: desde dos mil diecinueve, cuando desapareció el Consejo de Promoción Turística, ese dinero se fue al Tren Maya.", ["f3", "e3"], "SE FUE AL TREN MAYA"),
            plano("p07", "cierre_bucle", "Raúl Andrade Angulo, de los hoteleros del sur, lo pidió así: que el cobro se destine a la promoción turística, y no solo a otros segmentos.", ["e2", "f2"], "¿A DÓNDE VA?"),
            cierre("Aquí el dato mata al gato. ¿Trabajas en turismo? ¿Ya se nota que llegan menos? Cuéntamelo en los comentarios.", "¿YA SE NOTA?"),
        ],
    },
    "guion-cancun-visitax-aeropuerto": {
        "titulo": "Visitax en el aeropuerto", "gancho": "¿285 O 550?", "claves": ["visitax"],
        "fuentes": {
            "t2": "https://www.poresto.com/quintana-roo/cancun/2026/10/5/550-o-285-pesos-turistas-denuncian-cobro-de-casi-el-doble-por-visitax-en-la-terminal-2-del-aeropuerto-de-cancun.html (05/10/2026: oficial 285; módulos de la Terminal 2 cobran hasta 550, 265 más; creado en 2021 y aplicado en 2022; personal no explica quién autorizó; testimonio de un conductor)",
            "2026": "https://elcongresista.mx/politica/quintana-roo/quintana-roo-no-aumentara-el-visitax-en-2026 (el estado anunció que no aumentaría en 2026)",
            "turistas": "https://www.poresto.com/quintana-roo/cancun/2025/12/31/extranjeros-reprochan-presunto-cobro-abusivo-en-impuestos-del-visitax-en-cancun.html (Grant Henry: más de 30 años volando a Cancún sin pagarlo)",
        },
        "evidencia": [
            web("e1", "prensa", "https://www.poresto.com/quintana-roo/cancun/2026/10/5/550-o-285-pesos-turistas-denuncian-cobro-de-casi-el-doble-por-visitax-en-la-terminal-2-del-aeropuerto-de-cancun.amp.html", "PorEsto, 05/10/2026"),
            web("e2", "prensa", "https://elcongresista.mx/politica/quintana-roo/quintana-roo-no-aumentara-el-visitax-en-2026", "El Congresista"),
            web("e3", "prensa", "https://www.poresto.com/quintana-roo/cancun/2025/12/31/extranjeros-reprochan-presunto-cobro-abusivo-en-impuestos-del-visitax-en-cancun.amp.html", "PorEsto, 31/12/2025"),
            foto("e4", "lugar", "File:MMUN002.jpg"), foto("e5", "lugar", "File:MMUN003.jpg"), foto("e6", "lugar", ZH),
            ficha("f1", "Visitax", ["Lo paga cada turista extranjero en Quintana Roo", "Tarifa oficial: 285 pesos",
                  "Creado en 2021, se cobra desde 2022"], "PorEsto, 05/10/2026"),
            ficha("f2", "Terminal 2 del aeropuerto", ["Módulos que cobran hasta 550 pesos", "265 pesos más que la tarifa oficial",
                  "Nadie explicó quién lo autorizó"], "PorEsto, 05/10/2026"),
            ficha("f3", "Diciembre de 2025", ["El gobierno del estado: no sube en 2026"], "El Congresista"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "En la Terminal dos del aeropuerto de Cancún hay módulos que cobran el Visitax casi al doble. La tarifa oficial es de doscientos ochenta y cinco pesos.", ["f2", "e1"], "¿285 O 550?"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien maneja un transporte del aeropuerto en Cancún y escucha a sus pasajeros decir que les cobraron veinticinco o treinta dólares por persona, de golpe.", ["e4", "e1"], "DE GOLPE"),
            plano("p02", "contexto", "El Visitax lo paga cada turista extranjero que visita Quintana Roo. Se creó en dos mil veintiuno y se empezó a cobrar en dos mil veintidós.", ["f1", "e5"], "DESDE 2022"),
            plano("p03", "el_hecho", "Según PorEsto, en la Terminal dos cobran hasta quinientos cincuenta pesos por persona. Doscientos sesenta y cinco más que la tarifa oficial.", ["f2", "e1"], "265 PESOS MÁS"),
            plano("p04", "bucle_abierto", "El personal no supo explicar de dónde sale ese monto ni quién lo autorizó.", ["f2", "e4"], "¿QUIÉN LO AUTORIZÓ?"),
            plano("p05", "el_desenlace", "En diciembre, el gobierno del estado aseguró que el Visitax no subiría en dos mil veintiséis.", ["f3", "e2"], "NO IBA A SUBIR"),
            plano("p06", "contexto", "Y hay quien ni sabe que existe. Grant Henry, un turista, contó que lleva más de treinta años volando a Cancún y nunca lo ha pagado.", ["e3", "e6"], "30 AÑOS SIN PAGARLO"),
            plano("p07", "cierre_bucle", "La misma tarifa, dos precios distintos. Y nadie dice quién se queda con la diferencia.", ["e1", "f2"], "¿Y LA DIFERENCIA?"),
            cierre("Aquí el dato mata al gato. ¿A tus visitas de fuera les cobraron el Visitax? Cuéntamelo en los comentarios.", "¿SE LO COBRARON?"),
        ],
    },
    "guion-cancun-tribunales-laborales": {
        "titulo": "Tribunales laborales cerrados", "gancho": "TU DEMANDA, EN PAUSA", "claves": ["tribunales", "laboral", "laborales"],
        "fuentes": {
            "cierre": "https://noticaribe.com.mx/2026/10/08/cierran-tribunales-laborales-por-falla-informatica/ (08/10/2026: cierre desde el martes 6 en Chetumal y Cancún, este en la avenida Nichupté; apagón en Chetumal dañó equipos; reabrirían el martes; rezago desde inicios de año; decenas de personas sin audiencia)",
            "2021": "https://ruptura360.mx/el-estado/sistema-de-justicia-laboral-rezago/ (04/11/2021: el sistema nuevo arrancó el 3 de noviembre; 26 mil expedientes heredados de las Juntas; Catalina Portillo Navarro, STPS; el tribunal tiene hasta seis meses para resolver)",
            "jueces": "https://www.poresto.com/quintana-roo/2021/10/4/quintana-roo-sistema-de-justicia-laboral-entrara-en-funciones-en-noviembre.html (las Juntas Locales desaparecen; tres jueces laborales)",
        },
        "evidencia": [
            web("e1", "prensa", "https://noticaribe.com.mx/2026/10/08/cierran-tribunales-laborales-por-falla-informatica/", "Noticaribe, 08/10/2026"),
            web("e2", "prensa", "https://ruptura360.mx/el-estado/sistema-de-justicia-laboral-rezago/", "Ruptura 360, 04/11/2021"),
            web("e3", "prensa", "https://www.poresto.com/quintana-roo/2021/10/4/quintana-roo-sistema-de-justicia-laboral-entrara-en-funciones-en-noviembre.amp.html", "PorEsto, 04/10/2021"),
            foto("e4", "lugar", TULUM), foto("e5", "lugar", CENTRO), foto("e6", "lugar", "File:Palacio de Gobierno, Chetumal, Q. Roo. - panoramio.jpg"),
            ficha("f1", "Tribunales Laborales · octubre de 2026", ["Cerrados desde el martes 6 de octubre", "Chetumal y Cancún (avenida Nichupté)",
                  "Un apagón dañó los equipos de cómputo"], "Noticaribe, 08/10/2026"),
            ficha("f2", "3 de noviembre de 2021", ["Arranca el nuevo sistema de justicia laboral", "Desaparecen las Juntas de Conciliación",
                  "Heredan 26 mil expedientes"], "Ruptura 360 y PorEsto"),
            ficha("f3", "La promesa", ["45 días para intentar un acuerdo", "Si no hay acuerdo, el tribunal tiene hasta seis meses para resolver"],
                  "STPS Quintana Roo, vía Ruptura 360"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "Si tienes una demanda laboral en Cancún, esta semana tu audiencia no se hizo. El tribunal está cerrado.", ["f1", "e1"], "TU DEMANDA, EN PAUSA"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien lleva meses esperando su liquidación, llega a su audiencia en la avenida Nichupté y encuentra un aviso pegado en la puerta.", ["e1", "e4"], "UN AVISO EN LA PUERTA"),
            plano("p02", "contexto", "Desde el martes seis de octubre cerraron los Tribunales Laborales de Chetumal y de Cancún. Un apagón en Chetumal dañó los equipos de cómputo.", ["f1", "e6"], "UN APAGÓN"),
            plano("p03", "el_hecho", "Según Noticaribe, decenas de personas se quedaron sin audiencia. Y los tribunales ya arrastraban rezago desde inicios del año.", ["e1", "e5"], "YA HABÍA REZAGO"),
            plano("p04", "bucle_abierto", "Este sistema empezó el tres de noviembre de dos mil veintiuno. Llegó para reemplazar a las Juntas de Conciliación.", ["f2", "e3"], "DESDE 2021"),
            plano("p05", "el_desenlace", "Desde el primer día cargó con veintiséis mil expedientes heredados, según Catalina Portillo Navarro, entonces titular del Trabajo en el estado.", ["f2", "e2"], "26 MIL EXPEDIENTES"),
            plano("p06", "contexto", "La promesa era clara: si no había acuerdo, el tribunal tendría hasta seis meses para resolver.", ["f3", "e2"], "SEIS MESES"),
            plano("p07", "cierre_bucle", "Se espera que reabran el martes. Lo que nadie ha dicho es cuándo serán las audiencias que no se hicieron.", ["e1", "f1"], "A VOLVER A AGENDAR"),
            cierre("Aquí el dato mata al gato. ¿Cuánto tardó tu demanda laboral? Cuéntamelo en los comentarios.", "¿CUÁNTO TARDÓ LA TUYA?"),
        ],
    },
    "guion-cancun-beca-rita-cetina": {
        "titulo": "Beca Rita Cetina", "gancho": "¿QUIÉN FUE RITA CETINA?", "claves": ["rita cetina", "beca"],
        "fuentes": {
            "pagos": "https://quintanaroo.heraldodemexico.com.mx/local/2026/10/9/beca-rita-cetina-como-saber-si-ya-cayo-tu-pago-de-octubre-con-la-curp-17287.html (09/10/2026: 1,900 pesos por familia cada bimestre más 700 por estudiante adicional; pagos del 5 al 16 de octubre por apellido: M el 12, T a Z el 16; trámites gratuitos)",
            "rita": "https://es.wikipedia.org/wiki/Rita_Cetina_Guti%C3%A9rrez (nació en Mérida el 22/05/1846, murió el 11/10/1908; La Siempreviva en 1870 con Gertrudis Tenorio Zavala y Cristina Farfán; primer número de la revista el 7/05/1870)",
        },
        "evidencia": [
            web("e1", "prensa", "https://quintanaroo.heraldodemexico.com.mx/local/2026/10/9/beca-rita-cetina-como-saber-si-ya-cayo-tu-pago-de-octubre-con-la-curp-17287.html", "Heraldo de México QRoo, 09/10/2026"),
            web("e2", "prensa", "https://www.unotv.com/nacional/quien-fue-rita-cetina-gutierrez-maestra-que-da-nombre-beca-universal-de-ninos-y-jovenes/", "UnoTV"),
            web("e3", "prensa", "https://www.mexicodesconocido.com.mx/rita-cetina.html", "México Desconocido"),
            foto("e4", "persona", "File:Rita Cetina (aka Rita Cetina Gutiérrez).jpg"),
            foto("e5", "lugar", "File:Rita Cetina Gutiérrez, busto en el parque de las mujeres ilustres.jpg"),
            foto("e6", "lugar", CENTRO),
            ficha("f1", "Beca Rita Cetina · secundaria", ["1,900 pesos por familia cada bimestre", "700 más por cada estudiante adicional",
                  "Los trámites son gratuitos"], "Heraldo de México QRoo, 09/10/2026"),
            ficha("f2", "Pagos de octubre, por apellido", ["Lunes 12: M", "13: N a Q · 14: R · 15: S", "Viernes 16: T a Z"],
                  "Heraldo de México QRoo"),
            ficha("f3", "Rita Cetina Gutiérrez", ["Mérida, 22 de mayo de 1846", "1870: funda La Siempreviva",
                  "Muere el 11 de octubre de 1908"], "Wikipedia: Rita Cetina Gutiérrez"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "Esta semana sigue cayendo la beca Rita Cetina en Cancún. Pero casi nadie sabe quién fue Rita Cetina.", ["f2", "e4"], "¿QUIÉN FUE?"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien tiene a su hijo en una secundaria pública de Cancún y revisa la tarjeta del Bienestar cada mañana para ver si ya cayó.", ["e1", "e6"], "¿YA CAYÓ?"),
            plano("p02", "contexto", "Son mil novecientos pesos por familia cada bimestre, y setecientos más por cada hijo adicional en secundaria.", ["f1", "e1"], "1,900 POR BIMESTRE"),
            plano("p03", "el_hecho", "Se paga por la inicial del apellido. El lunes doce les toca a los de la eme. Del trece al dieciséis, al resto del abecedario.", ["f2", "e1"], "LUNES 12: LA M"),
            plano("p04", "bucle_abierto", "Rita Cetina Gutiérrez nació en Mérida en mil ochocientos cuarenta y seis. Fue maestra y poeta.", ["f3", "e4"], "MÉRIDA, 1846"),
            plano("p05", "el_desenlace", "En mil ochocientos setenta fundó La Siempreviva, con Gertrudis Tenorio Zavala y Cristina Farfán: una escuela y una revista hechas por mujeres.", ["f3", "e3"], "LA SIEMPREVIVA, 1870"),
            plano("p06", "contexto", "Después la nombraron directora del Instituto Literario de Niñas de Yucatán.", ["e2", "e5"], "ESCUELA PARA NIÑAS"),
            plano("p07", "cierre_bucle", "Murió el once de octubre de mil novecientos ocho. Ciento dieciocho años después, su nombre llega cada bimestre a miles de casas.", ["e5", "f3"], "11 DE OCTUBRE"),
            cierre("Aquí el dato mata al gato. ¿Ya te cayó la beca? Cuéntamelo en los comentarios.", "¿YA TE CAYÓ?"),
        ],
    },
    "guion-cancun-12-de-octubre": {
        "titulo": "12 de octubre en Quintana Roo", "gancho": "¿HAY CLASES EL LUNES?", "claves": ["12 de octubre", "pluricultural"],
        "fuentes": {
            "sep": "https://quintanaroo.heraldodemexico.com.mx/local/2026/10/9/hay-megapuente-por-el-12-de-octubre-en-quintana-roo-esto-dice-el-calendario-de-la-sep-17279.html (09/10/2026: lunes 12 de clases normales; no es descanso obligatorio según el art. 74 de la LFT; se llama Día de la Nación Pluricultural; próximos días sin clases: 30 de octubre y 2 de noviembre)",
            "inegi": "https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2021/EstSociodemo/ResultCenso2020_QRoo.pdf (p. 2: 204,949 hablantes de lengua indígena de 3 años y más, 11.7%; en 2010 eran 16.2%, 198,587; 2.8% afromexicanos)",
            "nombre": "https://www.cronica.com.mx/nacional/dia-nacion-pluricultural-existe-dia-raza-mexico.html (cambio de nombre en 2020)",
        },
        "evidencia": [
            web("e1", "prensa", "https://quintanaroo.heraldodemexico.com.mx/local/2026/10/9/hay-megapuente-por-el-12-de-octubre-en-quintana-roo-esto-dice-el-calendario-de-la-sep-17279.html", "Heraldo de México QRoo, 09/10/2026"),
            web("e2", "documento", "https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2021/EstSociodemo/ResultCenso2020_QRoo.pdf", "INEGI, Censo 2020 · Quintana Roo", pagina=2, desde=0.66, fraccion=0.86),
            web("e3", "prensa", "https://www.cronica.com.mx/nacional/dia-nacion-pluricultural-existe-dia-raza-mexico.html", "La Crónica"),
            buscar("e4", "lugar", "El Rey zona arqueológica Cancún"), foto("e5", "lugar", CENTRO), foto("e6", "lugar", TULUM),
            ficha("f1", "Lunes 12 de octubre", ["Hay clases normales, según el calendario de la SEP", "No es día de descanso obligatorio",
                  "Nombre oficial: Día de la Nación Pluricultural"], "Heraldo de México QRoo, 09/10/2026"),
            ficha("f2", "Quintana Roo · lenguas indígenas", ["2010: 16.2% hablaba una lengua indígena", "2020: 11.7%",
                  "204,949 personas"], "INEGI, Censo 2020"),
            ficha("f3", "Sin clases", ["Viernes 30 de octubre: Consejo Técnico", "Lunes 2 de noviembre: Día de Muertos"], "Calendario SEP, vía Heraldo de México QRoo"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "Este lunes doce de octubre sí hay clases en Quintana Roo. Y el día ya no se llama como te enseñaron en la escuela.", ["f1", "e1"], "¿HAY CLASES EL LUNES?"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien en Cancún ya planeaba el puente largo con los niños, y se entera de que el lunes hay escuela.", ["e5", "e1"], "NO HAY PUENTE"),
            plano("p02", "contexto", "Según el calendario de la SEP, el lunes doce es día de clases normal. Tampoco es descanso obligatorio en la Ley Federal del Trabajo.", ["f1", "e1"], "DÍA NORMAL"),
            plano("p03", "el_hecho", "Antes se le decía Día de la Raza. Desde dos mil veinte, su nombre oficial es Día de la Nación Pluricultural.", ["e3", "e4"], "NACIÓN PLURICULTURAL"),
            plano("p04", "bucle_abierto", "Y en Quintana Roo eso se nota. Según el INEGI, más de doscientas cuatro mil personas hablan una lengua indígena.", ["f2", "e2"], "204 MIL"),
            plano("p05", "el_desenlace", "Pero cada vez son menos en proporción. En dos mil diez eran el dieciséis por ciento del estado. En dos mil veinte, el once punto siete.", ["f2", "e2"], "DE 16% A 11.7%"),
            plano("p06", "contexto", "En plena Zona Hotelera de Cancún sigue en pie una zona arqueológica maya: El Rey.", ["e4", "e6"], "EL REY"),
            plano("p07", "cierre_bucle", "El puente largo llega hasta finales de mes: el treinta de octubre no hay clases, y el dos de noviembre tampoco.", ["f3", "e1"], "30 DE OCTUBRE"),
            cierre("Aquí el dato mata al gato. ¿En tu casa alguien habla maya? Cuéntamelo en los comentarios.", "¿ALGUIEN HABLA MAYA?"),
        ],
    },
    "guion-cancun-sereques-villas-otoch": {
        "titulo": "Sereques en Villas Otoch", "gancho": "7 SEREQUES EN UN TENDEDERO", "claves": ["aguti", "sereques"],
        "fuentes": {
            "hallazgo": "https://www.poresto.com/quintana-roo/cancun/2026/10/9/hallazgo-ejemplares-aguti-centroamericano-vida-cancun-moviliza-autoridades.html (09/10/2026: siete agutíes centroamericanos, sereques, colgados de una soga de tender ropa en la Séptima Privada Eucalipto con avenida Río Hondo, Villas Otoch, SM 247; vecinos creyeron que eran perros; dos detenidos, un joven y su madre; versiones: rituales o salpicón; dijeron haberlos capturado en un área verde cerca del Arco Vial; Fiscalía especializada en delitos contra el ambiente y la fauna)",
        },
        "evidencia": [
            web("e1", "prensa", "https://www.poresto.com/quintana-roo/cancun/2026/10/9/hallazgo-ejemplares-aguti-centroamericano-vida-cancun-moviliza-autoridades.amp.html", "PorEsto, 09/10/2026"),
            foto("e2", "lugar", "File:Agouti Tulum Take 2.jpg"),
            foto("e3", "lugar", "File:Central American agouti (Dasyprocta punctata).jpg"),
            foto("e4", "lugar", CENTRO), foto("e5", "lugar", TULUM),
            ficha("f1", "Villas Otoch · Supermanzana 247", ["7 agutíes, conocidos como sereques", "Colgados de un tendedero",
                  "Séptima Privada Eucalipto con avenida Río Hondo"], "PorEsto, 09/10/2026"),
            ficha("f2", "Dos versiones", ["Un joven: \"rituales\"", "Su madre: eran para salpicón",
                  "\"Se les había olvidado bajarlos del tendedero\""], "PorEsto, 09/10/2026"),
            ficha("f3", "Lo que sigue", ["Dos detenidos", "La Fiscalía de delitos contra el ambiente y la fauna integra la carpeta",
                  "Falta saber si hubo delito"], "PorEsto, 09/10/2026"),
        ],
        "planos": [
            plano("p00", "gancho_hablado", "En Villas Otoch, en Cancún, unos vecinos vieron siete animales colgados de un tendedero. Primero pensaron que eran perros.", ["f1", "e1"], "7 EN UN TENDEDERO"),
            plano("p01", "hook_tercera_persona", "Te imaginas a quien sale a tender su ropa en la supermanzana doscientos cuarenta y siete, y en su misma calle ve eso.", ["e4", "f1"], "EN SU MISMA CALLE"),
            plano("p02", "contexto", "No eran perros. Eran agutíes, a los que aquí se les dice sereques. Estaban en la séptima privada Eucalipto, con la avenida Río Hondo.", ["f1", "e2"], "ERAN SEREQUES"),
            plano("p03", "el_hecho", "Los vecinos llamaron a la Policía y a Bienestar Animal. Detuvieron a dos personas: un joven y su madre.", ["f3", "e1"], "DOS DETENIDOS"),
            plano("p04", "bucle_abierto", "Y las versiones no cuadran. Según PorEsto, el joven habló primero de rituales.", ["f2", "e3"], "¿RITUALES?"),
            plano("p05", "el_desenlace", "Su madre dijo otra cosa: que eran para hacer salpicón, y que se les había olvidado bajarlos del tendedero.", ["f2", "e1"], "¿SALPICÓN?"),
            plano("p06", "contexto", "Dijeron que los atraparon en un área verde cerca del Arco Vial. Sí: en las áreas verdes de Cancún todavía viven sereques.", ["e2", "e5"], "CERCA DEL ARCO VIAL"),
            plano("p07", "cierre_bucle", "Ahora la Fiscalía especializada en delitos contra la fauna tiene que decidir si hubo delito. Todavía no lo dice.", ["f3", "e3"], "¿HUBO DELITO?"),
            cierre("Aquí el dato mata al gato. ¿Has visto sereques en tu colonia? Cuéntamelo en los comentarios.", "¿HAS VISTO UNO?"),
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
