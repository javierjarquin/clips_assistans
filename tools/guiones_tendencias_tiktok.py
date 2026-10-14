"""Prueba de tendencias de TikTok (11/10/2026): 5 guiones por cada búsqueda de
la captura de "Estadísticas de búsqueda de creadores" que le sirve al canal:
"Películas de terror", "ciudad de mexico", "la historia" y "marfil película".

FORMATO APARTE (no toca la fórmula de Cancún). Sale del Short de LOCOFER sobre
la Isla de las Muñecas (3.4 M de vistas, 58 s), revisado cuadro por cuadro en
analisis/referencias_virales/:
  - p00 en SEGUNDA PERSONA ("Eres...") y en pantalla LUGAR · AÑO.
  - Cada frase deja algo por saber; la escalada va en tú.
  - La foto real de la persona se REVELA al final (p06), con su nombre.
  - Cierre que conecta con lo que se busca ("esto inspiró...", "si viste Marfil").
  - Cortos: ~120-150 palabras (45-60 s), no 160-200 como los de Cancún.
La segunda persona es de un testigo (policía, mesero, vecino), nunca de una
víctima de asesinato.

Hechos: cada uno salió de Wikipedia (es/en) o de la nota citada en "fuentes".
Lo que las fuentes no confirmaron se quitó (p. ej., cuántos días estuvo cada
hermana Sodi, la causa exacta del choque del Metro, el día de la muerte de
Estefanía en Vallecas). Getty III y la Pascualita se descartaron (menor de edad,
y leyenda sin hechos documentados).

    C:\\dato-mata-gato-bot\\.venv\\Scripts\\python.exe tools\\guiones_tendencias_tiktok.py
"""

import json
from pathlib import Path


def plano(pid, seccion, narracion, evidencia, texto):
    return {"id": pid, "seccion": seccion, "narracion": narracion,
            "visual": {"tipo": "archivo_historico", "evidencia": evidencia, "prompt_ia": "",
                       "busqueda_medios": "", "motion": "calm"},
            "texto_en_pantalla": texto}


def cierre(narracion, texto):
    return {"id": "p07", "seccion": "identidad_cierre", "narracion": narracion,
            "visual": {"tipo": "grafico_movimiento", "descripcion": "Cartel de cierre del canal.",
                       "prompt_ia": "", "busqueda_medios": ""},
            "texto_en_pantalla": texto}


def ficha(fid, titulo, renglones, fuente):
    return {"id": fid, "tipo": "ficha", "titulo": titulo, "renglones": renglones, "fuente": fuente}


def web(eid, tipo, url, fuente):
    return {"id": eid, "tipo": tipo, "url": url, "fuente": fuente}


def buscar(eid, tipo, consulta):
    return {"id": eid, "tipo": tipo, "buscar_wikimedia": consulta}


def foto(eid, tipo, archivo):
    return {"id": eid, "tipo": tipo, "wikimedia": archivo}


SECCIONES = ["gancho_hablado", "hook_tercera_persona", "contexto", "el_hecho",
             "bucle_abierto", "el_desenlace", "cierre_bucle"]


def planos(lineas, cta):
    """lineas: 7 tuplas (narración, [evidencia], texto en pantalla)."""
    out = [plano(f"p{i:02d}", SECCIONES[i], n, ev, t) for i, (n, ev, t) in enumerate(lineas)]
    return out + [cierre("Aquí el dato mata al gato. " + cta[0], cta[1])]


HASHTAGS = {
    "terror": ["#DatoMataGato", "#peliculasdeterror", "#terror", "#historiareal"],
    "cdmx": ["#DatoMataGato", "#CDMX", "#CiudadDeMexico", "#historiareal"],
    "historia": ["#DatoMataGato", "#lahistoria", "#historia", "#Mexico"],
    "marfil": ["#DatoMataGato", "#Marfil", "#secuestro", "#historiareal"],
}

GUIONES = {
    # ---------------------------------------------------------- PELÍCULAS DE TERROR
    "guion-tt-isla-de-las-munecas": {
        "nicho": "terror", "titulo": "La historia de la Isla de las Muñecas", "claves": ["muñecas", "xochimilco"],
        "fuentes": {"wiki": "https://en.wikipedia.org/wiki/Island_of_the_Dolls (Julián Santana Barrera; la niña no está documentada; murió en 2001 a los 80, boca abajo en el canal tras decir que lo llamaban sirenas; su familia la abrió al público; Guinness 2022)"},
        "evidencia": [
            web("e1", "documento", "https://en.wikipedia.org/wiki/Island_of_the_Dolls", "Wikipedia: Island of the Dolls"),
            web("e2", "prensa", "https://www.unotv.com/entretenimiento/la-isla-de-las-munecas-en-xochimilco-la-leyenda-detras-del-macabro-lugar/", "UnoTV"),
            web("e3", "prensa", "https://www.tvazteca.com/aztecauno/azteca-uno-especiales/2025-08-20/el-lugar-turistico-de-cdmx-que-parece-inofensivo-pero-esconde-un-pasado-maldito", "TV Azteca, 20/08/2025"),
            buscar("e4", "lugar", "Isla de las Muñecas Xochimilco"), buscar("e5", "lugar", "Island of the Dolls Xochimilco"),
            buscar("e6", "lugar", "Xochimilco trajinera canal"),
            ficha("f1", "Isla de las Muñecas · Xochimilco", ["Julián Santana Barrera vivió ahí solo", "Colgó muñecas durante décadas",
                  "La niña ahogada: nunca se documentó"], "Wikipedia: Island of the Dolls"),
            ficha("f2", "2001", ["Murió a los 80 años", "Boca abajo en el canal", "Su familia abrió la isla al público"], "Wikipedia"),
        ],
        "planos": planos([
            ("Eres Julián Santana Barrera. Vives solo en una chinampa de Xochimilco, y empiezas a colgar muñecas de los árboles.", ["e4", "e6"], "XOCHIMILCO, CDMX"),
            ("Dicen que encontraste a una niña ahogada en el canal. Y después, una muñeca flotando en el mismo lugar.", ["e5", "f1"], "UNA NIÑA EN EL CANAL"),
            ("Cuelgas una. Luego otra. Durante décadas, la isla se llena de muñecas.", ["e4", "e2"], "DÉCADAS"),
            ("En dos mil uno tienes ochenta años. Estás pescando con tu sobrino, y le dices que unas sirenas te llaman.", ["e6", "e1"], "LAS SIRENAS"),
            ("Tu sobrino se aleja un momento. Cuando regresa, estás muerto, boca abajo en el canal.", ["f2", "e5"], "BOCA ABAJO"),
            ("Según la historia, en el mismo lugar donde dijiste que se ahogó la niña. Esa niña nunca se ha podido documentar.", ["f1", "e3"], "¿EXISTIÓ?"),
            ("Don Julián sí existió. Su familia abrió la isla al público, y en dos mil veintidós Guinness la reconoció como la mayor colección de muñecas embrujadas del mundo.", ["e1", "e4"], "DON JULIÁN"),
        ], ("¿Te atreverías a ir? Comenta.", "¿IRÍAS?")),
    },
    "guion-tt-ed-gein": {
        "nicho": "terror", "titulo": "La historia de Ed Gein", "claves": ["gein"],
        "fuentes": {"wiki": "https://es.wikipedia.org/wiki/Ed_Gein (arresto 16/11/1957; Bernice Worden, 58; Mary Hogan, 1954; cráneos, máscaras y pantalla de lámpara de piel; nueve tumbas; 1968 culpable pero legalmente demente; murió en 1984; Psicosis, La masacre de Texas, El silencio de los inocentes)",
                    "netflix": "https://www.infobae.com/entretenimiento/2025/09/15/netflix-lanza-el-trailer-de-monstruo-la-historia-de-ed-gein-serie-sobre-el-asesino-que-inspiro-la-masacre-de-texas/ (su madre murió en 1945)"},
        "evidencia": [
            web("e1", "documento", "https://es.wikipedia.org/wiki/Ed_Gein", "Wikipedia: Ed Gein"),
            web("e2", "prensa", "https://www.infobae.com/entretenimiento/2025/09/15/netflix-lanza-el-trailer-de-monstruo-la-historia-de-ed-gein-serie-sobre-el-asesino-que-inspiro-la-masacre-de-texas/", "Infobae, 15/09/2025"),
            web("e3", "prensa", "https://www.elcomercio.com/afull/cine-y-series/historia-real-de-ed-gein/", "El Comercio"),
            buscar("e4", "lugar", "Plainfield Wisconsin"), buscar("e5", "persona", "Ed Gein"),
            ficha("f1", "Plainfield, Wisconsin · 1957", ["16 de noviembre: desaparece Bernice Worden, 58 años", "Dueña de la ferretería del pueblo"], "Wikipedia: Ed Gein"),
            ficha("f2", "Lo que encontró la policía", ["Cráneos", "Máscaras de piel humana", "Una pantalla de lámpara hecha con piel de un rostro"], "Wikipedia: Ed Gein"),
            ficha("f3", "Inspiró", ["Psicosis (1960)", "La masacre de Texas", "El silencio de los inocentes (1991)"], "Wikipedia: Ed Gein"),
        ],
        "planos": planos([
            ("Eres policía en Plainfield, Wisconsin. Es el dieciséis de noviembre de mil novecientos cincuenta y siete, y la dueña de la ferretería desapareció.", ["f1", "e4"], "PLAINFIELD, 1957"),
            ("Se llama Bernice Worden y tiene cincuenta y ocho años. Las sospechas te llevan a la granja de un vecino que vive solo desde que murió su madre.", ["f1", "e2"], "UN VECINO CALLADO"),
            ("Entras. Encuentras cráneos, máscaras hechas con piel humana y una pantalla de lámpara hecha con la piel de un rostro.", ["f2", "e1"], "LO QUE HABÍA ADENTRO"),
            ("Él confiesa que sacó cuerpos de nueve tumbas. Y que también mató a Mary Hogan, una tabernera desaparecida en mil novecientos cincuenta y cuatro.", ["e3", "f2"], "NUEVE TUMBAS"),
            ("En mil novecientos sesenta y ocho lo declaran culpable del asesinato de Bernice, pero legalmente demente.", ["e1", "e4"], "LEGALMENTE DEMENTE"),
            ("Pasa el resto de su vida en una institución psiquiátrica. Muere en mil novecientos ochenta y cuatro.", ["e2", "e3"], "HASTA 1984"),
            ("Se llamaba Ed Gein. Y de su historia salieron Psicosis, La masacre de Texas y El silencio de los inocentes.", ["e5", "f3"], "ED GEIN"),
        ], ("¿Cuál de las tres viste? Comenta.", "¿CUÁL VISTE?")),
    },
    "guion-tt-anneliese-michel": {
        "nicho": "terror", "titulo": "La historia real de Emily Rose", "claves": ["anneliese", "michel", "exorcismo"],
        "fuentes": {"wiki": "https://en.wikipedia.org/wiki/Anneliese_Michel y https://es.wikipedia.org/wiki/Anneliese_Michel (murió el 1/07/1976 en Klingenberg a los 23; 65-67 exorcismos en unos diez meses, una o dos por semana, hasta cuatro horas; Ernst Alt y Arnold Renz; 30 kg; desnutrición y deshidratación; fiscalía de Aschaffenburg en 1977; juicio desde el 30/03/1978; abril de 1978 culpables de homicidio por negligencia, penas suspendidas; las sesiones se grabaron; El exorcismo de Emily Rose, 2005)"},
        "evidencia": [
            web("e1", "documento", "https://es.wikipedia.org/wiki/Anneliese_Michel", "Wikipedia: Anneliese Michel"),
            web("e2", "documento", "https://en.wikipedia.org/wiki/Anneliese_Michel", "Wikipedia (inglés): Anneliese Michel"),
            web("e3", "prensa", "https://slashfilm.com/stories/the-exorcism-of-emily-rose-is-based-on-a-tragic-real-life-story", "SlashFilm"),
            buscar("e4", "lugar", "Klingenberg am Main"), buscar("e5", "persona", "Anneliese Michel"),
            ficha("f1", "Klingenberg, Alemania · 1976", ["Anneliese Michel, 23 años", "Murió el 1 de julio", "Pesaba unos 30 kilos"], "Wikipedia"),
            ficha("f2", "Los exorcismos", ["Más de 60 sesiones en unos diez meses", "Hasta cuatro horas cada una", "Se grabaron en cintas"], "Wikipedia"),
            ficha("f3", "1978", ["Padres y dos sacerdotes: culpables de homicidio por negligencia", "Penas suspendidas"], "Wikipedia"),
        ],
        "planos": planos([
            ("Eres fiscal en Aschaffenburg, Alemania. Es mil novecientos setenta y siete, y te llega el caso de una joven de veintitrés años que murió de hambre.", ["e4", "e1"], "ALEMANIA, 1977"),
            ("Murió en Klingenberg el uno de julio de mil novecientos setenta y seis. Pesaba unos treinta kilos.", ["f1", "e2"], "30 KILOS"),
            ("Durante unos diez meses, dos sacerdotes le hicieron más de sesenta exorcismos. Una o dos sesiones por semana, de hasta cuatro horas.", ["f2", "e3"], "MÁS DE 60 EXORCISMOS"),
            ("Sus padres estaban de acuerdo. Y las sesiones se grabaron en cintas.", ["f2", "e1"], "LAS CINTAS"),
            ("La autopsia dijo desnutrición y deshidratación.", ["e2", "e4"], "LA AUTOPSIA"),
            ("En mil novecientos setenta y ocho, los padres y los sacerdotes Ernst Alt y Arnold Renz fueron declarados culpables de homicidio por negligencia. Sus penas quedaron suspendidas.", ["f3", "e1"], "CULPABLES"),
            ("Se llamaba Anneliese Michel. Y en dos mil cinco su historia se volvió la película El exorcismo de Emily Rose.", ["e5", "e3"], "ANNELIESE MICHEL"),
        ], ("¿Enfermedad o posesión? Comenta.", "¿ENFERMEDAD O POSESIÓN?")),
    },
    "guion-tt-amityville": {
        "nicho": "terror", "titulo": "La historia real de Amityville", "claves": ["amityville", "defeo"],
        "fuentes": {"wiki": "https://en.wikipedia.org/wiki/Ronald_DeFeo_Jr. (13/11/1974; 112 Ocean Avenue; seis víctimas; rifle Marlin calibre .35 hacia las 3:00; DeFeo de 23 años; primero culpó a la mafia; seis sentencias de 25 años a perpetua el 4/12/1975; murió en 2021; los Lutz se fueron tras 28 días; The Amityville Horror 1979)",
                    "ecartelera": "https://www.ecartelera.com/noticias/la-historia-real-de-amityville-44769/"},
        "evidencia": [
            web("e1", "documento", "https://en.wikipedia.org/wiki/Amityville_murders", "Wikipedia: Amityville murders"),
            web("e2", "prensa", "https://www.ecartelera.com/noticias/la-historia-real-de-amityville-44769/", "eCartelera"),
            web("e3", "prensa", "https://www.biobiochile.cl/noticias/sociedad/misterios/2017/10/07/la-verdadera-historia-de-amityville-la-casa-del-horror-que-costo-la-vida-de-una-familia.shtml", "BioBioChile"),
            buscar("e4", "lugar", "112 Ocean Avenue Amityville"), buscar("e5", "persona", "Ronald DeFeo"),
            ficha("f1", "Amityville, Nueva York · 1974", ["13 de noviembre, hacia las 3 de la mañana", "112 Ocean Avenue", "Seis muertos de la familia DeFeo"], "Wikipedia"),
            ficha("f2", "Ronald DeFeo Jr., 23 años", ["Primero culpó a la mafia", "Luego confesó", "Seis sentencias de 25 años a perpetua"], "Wikipedia"),
            ficha("f3", "Los Lutz", ["Se mudaron a la casa un año después", "Se fueron a los 28 días", "Terror en Amityville (1979)"], "Wikipedia y eCartelera"),
        ],
        "planos": planos([
            ("Eres policía en Amityville, Nueva York. Es el trece de noviembre de mil novecientos setenta y cuatro, y te reportan seis muertos en el ciento doce de Ocean Avenue.", ["f1", "e4"], "AMITYVILLE, 1974"),
            ("Son los padres y cuatro hermanos de la familia DeFeo. Los mataron hacia las tres de la mañana, con un rifle.", ["f1", "e1"], "SEIS MUERTOS"),
            ("Sobrevivió un solo hijo, Ronald, de veintitrés años. Primero dice que fue la mafia.", ["f2", "e3"], "¿LA MAFIA?"),
            ("Luego confiesa.", ["e1", "e4"], "CONFIESA"),
            ("Lo condenan a seis sentencias de veinticinco años a cadena perpetua. Muere preso en dos mil veintiuno.", ["f2", "e2"], "SEIS SENTENCIAS"),
            ("Un año después, otra familia, los Lutz, se muda a esa casa. Se van a los veintiocho días.", ["f3", "e4"], "28 DÍAS"),
            ("Dijeron que la casa estaba embrujada. Nunca lo probaron, pero su historia se volvió la película Terror en Amityville.", ["e5", "f3"], "TERROR EN AMITYVILLE"),
        ], ("¿Vivirías en esa casa? Comenta.", "¿VIVIRÍAS AHÍ?")),
    },
    "guion-tt-caso-vallecas": {
        "nicho": "terror", "titulo": "La historia real de Verónica", "claves": ["vallecas", "estefania"],
        "fuentes": {"hipertextual": "https://hipertextual.com/cine-television/el-terrorifico-caso-real-en-el-que-se-basa-expediente-vallecas/ (ouija en el colegio; el expediente no afirma ni niega)",
                    "auralcrave": "https://auralcrave.com/es/2022/02/04/caso-vallecas-la-real-historia-de-estefania-gutierrez-detras-de-la-pelicula-veronica/",
                    "nota": "El día exacto de la muerte (julio o agosto de 1991) discrepa entre fuentes: se dice 'el verano de 1991'. Informe policial de noviembre de 1992, inspector José Pedro Negri."},
        "evidencia": [
            web("e1", "prensa", "https://hipertextual.com/cine-television/el-terrorifico-caso-real-en-el-que-se-basa-expediente-vallecas/", "Hipertextual"),
            web("e2", "prensa", "https://auralcrave.com/es/2022/02/04/caso-vallecas-la-real-historia-de-estefania-gutierrez-detras-de-la-pelicula-veronica/", "Auralcrave"),
            web("e3", "documento", "https://en.wikipedia.org/wiki/Ver%C3%B3nica_(2017_Spanish_film)", "Wikipedia: Verónica (2017)"),
            buscar("e4", "lugar", "Vallecas Madrid"), buscar("e5", "lugar", "Ouija board"),
            ficha("f1", "Vallecas, Madrid", ["Verano de 1991: muere Estefanía Gutiérrez Lázaro", "Los médicos no dieron una causa clara"], "Hipertextual y Auralcrave"),
            ficha("f2", "Noviembre de 1992", ["El inspector José Pedro Negri pasa la noche en el piso", "Su informe no afirma ni niega", "Habla de hechos que no pudieron explicar"], "Hipertextual"),
        ],
        "planos": planos([
            ("Eres inspector de policía en Madrid. Es noviembre de mil novecientos noventa y dos, y te llaman a un piso del barrio de Vallecas.", ["e4", "f2"], "VALLECAS, 1992"),
            ("La familia dice que en su casa pasan cosas que nadie explica. Un año antes murió su hija, Estefanía Gutiérrez Lázaro.", ["f1", "e2"], "ESTEFANÍA"),
            ("Según varias versiones, había jugado a la ouija en el colegio.", ["e5", "e1"], "LA OUIJA"),
            ("Murió en el verano de mil novecientos noventa y uno. Los médicos nunca dieron una causa clara.", ["f1", "e2"], "SIN CAUSA CLARA"),
            ("El inspector José Pedro Negri y sus hombres pasan esa noche en el piso. Y lo que ven queda escrito en un informe oficial.", ["f2", "e1"], "EL INFORME"),
            ("El informe no dice que hubiera fantasmas. Pero tampoco lo niega: habla de hechos que no pudieron explicar.", ["f2", "e4"], "NO LO NIEGA"),
            ("Ese expediente inspiró Verónica, la película de terror de Paco Plaza, en dos mil diecisiete.", ["e3", "e5"], "VERÓNICA"),
        ], ("¿Has jugado a la ouija? Comenta.", "¿HAS JUGADO?")),
    },
    # ---------------------------------------------------------- CIUDAD DE MÉXICO
    "guion-tt-canibal-de-la-guerrero": {
        "nicho": "cdmx", "titulo": "La historia del caníbal de la Guerrero", "claves": ["calva", "guerrero"],
        "fuentes": {"wiki": "https://es.wikipedia.org/wiki/Jos%C3%A9_Luis_Calva_Zepeda (octubre de 2007; Alejandra Galeana Garavito, 32, madre de dos; refrigerador y sartén; novela Instintos caníbales; aceptó el asesinato y negó el canibalismo; muerto el 11/12/2007 en el Reclusorio Oriente, ahorcado según las autoridades)",
                    "chilango": "https://www.chilango.com/cultura/la-escalofriante-historia-del-poeta-canibal-de-la-colonia-guerrero/ (detenido el 8 de octubre)"},
        "evidencia": [
            web("e1", "prensa", "https://www.chilango.com/cultura/la-escalofriante-historia-del-poeta-canibal-de-la-colonia-guerrero/", "Chilango"),
            web("e2", "prensa", "https://expansion.mx/actualidad/2007/10/17/el-canibal-tiene-un-complice-pgjdf", "Expansión, 17/10/2007"),
            foto("e4", "lugar", "File:Una calle de la Colonia Guerrero, México DF. - panoramio.jpg"),
            foto("e5", "lugar", "File:Reclusorio Preventivo Varonil Oriente.jpg"),
            ficha("f1", "Colonia Guerrero · octubre de 2007", ["Alejandra Galeana Garavito, 32 años", "Madre de dos hijos", "Reportada como desaparecida"], "Wikipedia"),
            ficha("f2", "Lo que encontró la policía", ["Partes del cuerpo en el refrigerador", "Otras en un sartén", "Una novela: Instintos caníbales"], "Wikipedia y Chilango"),
        ],
        "planos": planos([
            ("Eres policía en la Ciudad de México. Es octubre de dos mil siete, y vas a un departamento de la colonia Guerrero por una mujer desaparecida.", ["e4", "f1"], "COLONIA GUERRERO, 2007"),
            ("Se llama Alejandra Galeana Garavito. Tiene treinta y dos años y es madre de dos hijos.", ["f1", "e1"], "ALEJANDRA"),
            ("En el refrigerador encuentras partes de su cuerpo. Otras, en un sartén.", ["f2", "e2"], "EL REFRIGERADOR"),
            ("Su pareja escribía poemas y una novela. Se llamaba Instintos caníbales.", ["f2", "e3"], "INSTINTOS CANÍBALES"),
            ("Lo detienen el ocho de octubre. Acepta el asesinato, pero niega el canibalismo.", ["e2", "e1"], "LO NIEGA"),
            ("El once de diciembre aparece muerto en el Reclusorio Oriente. Las autoridades dicen que se ahorcó.", ["e5", "e3"], "RECLUSORIO ORIENTE"),
            ("Se llamaba José Luis Calva Zepeda. Lo llamaron el poeta caníbal.", ["e3", "e1"], "EL POETA CANÍBAL"),
        ], ("¿Recuerdas este caso? Comenta.", "¿LO RECUERDAS?")),
    },
    "guion-tt-trotsky-coyoacan": {
        "nicho": "cdmx", "titulo": "La historia del asesinato de Trotsky", "claves": ["trotsky", "trotski", "mercader"],
        "fuentes": {"es": "https://es.wikipedia.org/wiki/Asesinato_de_Le%C3%B3n_Trotski (20/08/1940, muere el 21; Ramón Mercader alias Jacques Mornard; piolet; su tumba está en su casa de Coyoacán)",
                    "en": "https://en.wikipedia.org/wiki/Assassination_of_Leon_Trotsky (24/05/1940 con Siqueiros; 60 años; 20 años en Lecumberri, libre en 1960; Héroe de la Unión Soviética)"},
        "evidencia": [
            web("e1", "documento", "https://es.wikipedia.org/wiki/Asesinato_de_Le%C3%B3n_Trotski", "Wikipedia: Asesinato de León Trotski"),
            web("e2", "documento", "https://en.wikipedia.org/wiki/Assassination_of_Leon_Trotsky", "Wikipedia (inglés)"),
            buscar("e3", "lugar", "Museo Casa de León Trotsky Coyoacán"), buscar("e4", "persona", "Leon Trotsky 1940 Mexico"),
            buscar("e5", "persona", "David Alfaro Siqueiros"), buscar("e6", "persona", "Ramón Mercader"),
            ficha("f1", "Coyoacán · 1940", ["24 de mayo: un comando ataca la casa a balazos", "Con el pintor David Alfaro Siqueiros", "Él sobrevive"], "Wikipedia"),
            ficha("f2", "20 de agosto de 1940", ["Un hombre que se hace llamar Jacques Mornard", "Lo ataca con un piolet", "Muere al día siguiente"], "Wikipedia"),
        ],
        "planos": planos([
            ("Eres guardia en una casa de Coyoacán. Es mil novecientos cuarenta, y tres meses antes ya intentaron matar al hombre que cuidas.", ["e3", "f1"], "COYOACÁN, 1940"),
            ("El veinticuatro de mayo, un comando armado, con el pintor David Alfaro Siqueiros, entró a balazos. Él sobrevivió.", ["f1", "e5"], "24 DE MAYO"),
            ("El veinte de agosto llega un hombre que se hace llamar Jacques Mornard.", ["f2", "e1"], "JACQUES MORNARD"),
            ("Lo ataca con un piolet.", ["f2", "e2"], "UN PIOLET"),
            ("Muere al día siguiente, a los sesenta años.", ["e1", "e3"], "21 DE AGOSTO"),
            ("El asesino era Ramón Mercader, un agente soviético. Pasó veinte años en Lecumberri, y al salir, la Unión Soviética lo nombró héroe.", ["e6", "e2"], "HÉROE SOVIÉTICO"),
            ("El hombre era León Trotsky. Su tumba está en esa misma casa de Coyoacán.", ["e4", "e3"], "LEÓN TROTSKY"),
        ], ("¿Sabías que pasó en la Ciudad de México? Comenta.", "¿LO SABÍAS?")),
    },
    "guion-tt-obregon-la-bombilla": {
        "nicho": "cdmx", "titulo": "La historia de Obregón en La Bombilla", "claves": ["obregon", "bombilla"],
        "fuentes": {"wiki": "https://es.wikipedia.org/wiki/Asesinato_de_%C3%81lvaro_Obreg%C3%B3n (17/07/1928, 14:20; La Bombilla, San Ángel; José de León Toral se presentó como dibujante; seis disparos; Madre Conchita, 20 años en Islas Marías, libre en 1940 tras 12; Toral fusilado en Lecumberri el 9/02/1929; presidente electo; Guerra Cristera; monumento en el lugar)"},
        "evidencia": [
            web("e1", "documento", "https://es.wikipedia.org/wiki/Asesinato_de_%C3%81lvaro_Obreg%C3%B3n", "Wikipedia: Asesinato de Álvaro Obregón"),
            buscar("e2", "lugar", "Monumento a Álvaro Obregón San Ángel"), buscar("e3", "persona", "Álvaro Obregón"),
            buscar("e4", "persona", "José de León Toral"), buscar("e5", "lugar", "San Ángel Ciudad de México"),
            ficha("f1", "La Bombilla, San Ángel", ["17 de julio de 1928, 14:20", "Come el presidente electo", "Recién reelecto"], "Wikipedia"),
            ficha("f2", "El dibujante", ["Le muestra una caricatura", "Le dispara seis veces", "Fusilado en Lecumberri, febrero de 1929"], "Wikipedia"),
            ficha("f3", "La Madre Conchita", ["Acusada de autora intelectual", "Doce años presa en las Islas Marías"], "Wikipedia"),
        ],
        "planos": planos([
            ("Eres mesero en La Bombilla, en San Ángel. Es el diecisiete de julio de mil novecientos veintiocho, y en tu restaurante come el presidente electo.", ["e5", "f1"], "SAN ÁNGEL, 1928"),
            ("Acaba de ganar la reelección. El país está en plena Guerra Cristera.", ["f1", "e1"], "GUERRA CRISTERA"),
            ("Un joven se acerca con un cuaderno. Dice que es dibujante y le enseña una caricatura. El presidente se ríe.", ["f2", "e2"], "UNA CARICATURA"),
            ("Entonces el joven saca una pistola y le dispara seis veces.", ["f2", "e1"], "SEIS DISPAROS"),
            ("Se llamaba José de León Toral. Lo fusilaron en Lecumberri en febrero de mil novecientos veintinueve.", ["e4", "f2"], "JOSÉ DE LEÓN TORAL"),
            ("Con él juzgaron a una monja, la Madre Conchita, acusada de ser la autora intelectual. Pasó doce años presa en las Islas Marías.", ["f3", "e1"], "LA MADRE CONCHITA"),
            ("El presidente era Álvaro Obregón. Donde estaba el restaurante, hoy hay un monumento.", ["e3", "e2"], "ÁLVARO OBREGÓN"),
        ], ("¿Has pasado por ese monumento? Comenta.", "¿LO CONOCES?")),
    },
    "guion-tt-sobera-de-la-flor": {
        "nicho": "cdmx", "titulo": "La historia de Higinio Sobera de la Flor", "claves": ["sobera"],
        "fuentes": {"universal": "https://www.eluniversal.com.mx/cultura/higinio-sobera-el-psicopata-sexual-y-asesino-aterro-mexico-en-1952/ (mayo de 1952: Armando Lepe Ruiz en Insurgentes y Yucatán; Arnoldo Galván Santoyo, 18, en Coyoacán; Hortensia López Gómez, seis impactos; acorralado el 14 de mayo en el hotel Montejo; 24 años; 'no soy ningún payaso'; El Pelón)",
                    "chilango": "https://www.chilango.com/noticias/asesinos-seriales-en-mexico/ (hijo de un hacendado tabasqueño)"},
        "evidencia": [
            web("e1", "prensa", "https://www.eluniversal.com.mx/cultura/higinio-sobera-el-psicopata-sexual-y-asesino-aterro-mexico-en-1952/", "El Universal"),
            web("e2", "prensa", "https://www.chilango.com/noticias/asesinos-seriales-en-mexico/", "Chilango"),
            foto("e3", "lugar", "File:Avenida de los Insurgentes Sur, CDMX 10-22.jpg"), buscar("e4", "lugar", "Coyoacán Viveros"),
            buscar("e5", "lugar", "Colonia Roma Ciudad de México"),
            ficha("f1", "Mayo de 1952 · Ciudad de México", ["Armando Lepe Ruiz, en Insurgentes y Yucatán", "Arnoldo Galván Santoyo, 18 años, en Coyoacán", "Hortensia López Gómez"], "El Universal"),
            ficha("f2", "14 de mayo de 1952", ["Lo acorralan en el hotel Montejo", "Se entrega", "\"No soy ningún payaso\""], "El Universal"),
        ],
        "planos": planos([
            ("Eres agente de la policía en la Ciudad de México. Es mayo de mil novecientos cincuenta y dos, y matan a un hombre en Insurgentes y Yucatán.", ["e3", "f1"], "CDMX, 1952"),
            ("Se llamaba Armando Lepe Ruiz. Según el asesino, lo había llamado payaso.", ["f1", "e1"], "PAYASO"),
            ("Días antes, en Coyoacán, mataron a un joven de dieciocho años, Arnoldo Galván Santoyo.", ["e4", "f1"], "COYOACÁN"),
            ("Y aparece el cuerpo de una mujer, Hortensia López Gómez, con seis balazos.", ["f1", "e2"], "SEIS BALAZOS"),
            ("El catorce de mayo lo acorralas en un cuarto del hotel Montejo. Se entrega.", ["f2", "e1"], "HOTEL MONTEJO"),
            ("Tiene veinticuatro años, es hijo de un hacendado de Tabasco, y le dicen El Pelón.", ["e2", "e5"], "EL PELÓN"),
            ("Se llamaba Higinio Sobera de la Flor. Y lo explicó así: no soy ningún payaso.", ["f2", "e1"], "HIGINIO SOBERA"),
        ], ("¿Habías oído de él? Comenta.", "¿LO CONOCÍAS?")),
    },
    "guion-tt-metro-viaducto-1975": {
        "nicho": "cdmx", "titulo": "La historia del choque del Metro de 1975", "claves": ["metro", "viaducto"],
        "fuentes": {"razon": "https://www.razon.com.mx/ciudad/registra-metro-en-5-decadas-tres-accidentes-de-gravedad/ (unos 70 km/h; el conductor no frenó; después, piloto automático)",
                    "expansion": "https://politica.expansion.mx/cdmx/2023/01/07/los-choques-de-trenes-registrados-en-la-historia-del-metro-capitalino (20/10/1975, línea 2, Viaducto; 30 muertos; falta de comunicación y error del conductor; sin sistema anticolisión)",
                    "nota": "Muertos: 30 u 31 según la fuente; se dice 'unos treinta'. Condena del conductor: 10 o 12 años; se dice 'a prisión'."},
        "evidencia": [
            web("e1", "prensa", "https://www.mexicodesconocido.com.mx/tragedia-metro-cdmx-1975.html", "México Desconocido"),
            web("e2", "prensa", "https://politica.expansion.mx/cdmx/2023/01/07/los-choques-de-trenes-registrados-en-la-historia-del-metro-capitalino", "Expansión, 07/01/2023"),
            web("e3", "prensa", "https://www.razon.com.mx/ciudad/registra-metro-en-5-decadas-tres-accidentes-de-gravedad/", "La Razón"),
            foto("e4", "lugar", "File:Estacion Viaducto.JPG"), foto("e5", "lugar", "File:Mexico City Metro.jpg"),
            ficha("f1", "Lunes 20 de octubre de 1975", ["Línea 2, estación Viaducto", "Un tren choca contra otro que esperaba salir", "Unos 30 muertos y 70 heridos"], "Expansión y México Desconocido"),
            ficha("f2", "Después", ["Falta de comunicación y error del conductor", "Los trenes no tenían sistema anticolisión", "Se instala el piloto automático"], "Expansión y La Razón"),
        ],
        "planos": planos([
            ("Eres pasajero del Metro en la Ciudad de México. Es el lunes veinte de octubre de mil novecientos setenta y cinco, y tu tren va hacia Viaducto, en la línea dos.", ["e5", "f1"], "LÍNEA 2, 1975"),
            ("Adelante, en la estación, otro tren espera para salir.", ["e4", "e1"], "OTRO TREN"),
            ("Tu tren no alcanza a frenar.", ["f1", "e3"], "NO FRENA"),
            ("El choque deja unos treinta muertos y cerca de setenta heridos.", ["f1", "e2"], "30 MUERTOS"),
            ("La investigación habló de falta de comunicación y de un error del conductor. Los trenes no tenían cómo evitar chocar entre sí.", ["f2", "e2"], "SIN PROTECCIÓN"),
            ("El conductor fue condenado a prisión.", ["e3", "e4"], "A PRISIÓN"),
            ("Por este choque, el Metro instaló el piloto automático en sus trenes. Fue el peor accidente de su historia.", ["f2", "e1"], "EL PEOR ACCIDENTE"),
        ], ("¿Tú en qué línea viajas? Comenta.", "¿QUÉ LÍNEA TOMAS?")),
    },
    # ---------------------------------------------------------- LA HISTORIA
    "guion-tt-zona-del-silencio": {
        "nicho": "historia", "titulo": "La historia de la Zona del Silencio", "claves": ["silencio", "mapimi"],
        "fuentes": {"wiki": "https://es.wikipedia.org/wiki/Zona_del_Silencio (julio de 1970, cohete Athena desde Green River, Utah; dos contenedores de cobalto 57; búsqueda de tres semanas; ramal de tren de 12 km; mitos; reserva de la biosfera en 1974)",
                    "atlas": "https://atlasobscura.com/places/mapimi-silent-zone (11/07/1970)"},
        "evidencia": [
            web("e1", "documento", "https://es.wikipedia.org/wiki/Zona_del_Silencio", "Wikipedia: Zona del Silencio"),
            web("e2", "prensa", "https://atlasobscura.com/places/mapimi-silent-zone", "Atlas Obscura"),
            web("e3", "documento", "https://en.wikipedia.org/wiki/Mapim%C3%AD_Silent_Zone", "Wikipedia (inglés)"),
            buscar("e4", "lugar", "Zona del Silencio Mapimí"), buscar("e5", "lugar", "Reserva de la Biosfera Mapimí"),
            buscar("e6", "lugar", "Athena RTV rocket"),
            ficha("f1", "11 de julio de 1970", ["Un cohete Athena de EE. UU. pierde el control", "Cae en el desierto de Mapimí", "Lleva cobalto 57, radiactivo"], "Wikipedia y Atlas Obscura"),
            ficha("f2", "Lo que siguió", ["Tres semanas de búsqueda", "Una vía de tren de 12 km para sacar los restos", "1974: reserva de la biosfera"], "Wikipedia"),
        ],
        "planos": planos([
            ("Eres vaquero en el desierto de Mapimí, en Durango. Es julio de mil novecientos setenta, y algo cae del cielo.", ["e4", "f1"], "MAPIMÍ, 1970"),
            ("Es un cohete Athena de Estados Unidos, lanzado desde Utah. Perdió el control.", ["e6", "f1"], "UN COHETE"),
            ("Lleva dos contenedores pequeños de cobalto cincuenta y siete. Es material radiactivo.", ["f1", "e2"], "RADIACTIVO"),
            ("Lo buscan por tierra y aire durante tres semanas.", ["e1", "e4"], "TRES SEMANAS"),
            ("Para sacar los restos y la tierra contaminada, construyen una vía de tren de doce kilómetros.", ["f2", "e3"], "UNA VÍA DE TREN"),
            ("Y de ahí nace la leyenda: que ahí no funcionan los radios, que hay extraterrestres.", ["e2", "e5"], "LA LEYENDA"),
            ("Nadie lo ha probado. Le dicen la Zona del Silencio, y desde mil novecientos setenta y cuatro es reserva de la biosfera.", ["e5", "f2"], "ZONA DEL SILENCIO"),
        ], ("¿Irías a la Zona del Silencio? Comenta.", "¿IRÍAS?")),
    },
    "guion-tt-momias-de-guanajuato": {
        "nicho": "historia", "titulo": "La historia de las momias de Guanajuato", "claves": ["momias", "guanajuato"],
        "fuentes": {"wiki": "https://es.wikipedia.org/wiki/Momias_de_Guanajuato (1865, panteón de Santa Paula, primera momia: el médico francés Remigio Leroy, fosa sin pagos; impuesto por entierro desde 1865; nitratos y alumbre en el subsuelo; 111 cuerpos en la colección; la momia más pequeña del mundo, un feto)"},
        "evidencia": [
            buscar("e2", "lugar", "Museo de las Momias de Guanajuato"), buscar("e3", "lugar", "Panteón de Santa Paula Guanajuato"),
            buscar("e4", "lugar", "Guanajuato ciudad"), buscar("e5", "lugar", "momia Guanajuato"),
            ficha("f1", "Panteón de Santa Paula · 1865", ["Se exhuma el primer cuerpo momificado", "El médico francés Remigio Leroy", "Nadie pagaba por su tumba"], "Wikipedia"),
            ficha("f2", "Por qué se momificaron", ["Nitratos y alumbre en el subsuelo", "111 cuerpos en la colección", "La momia más pequeña del mundo"], "Wikipedia"),
        ],
        "planos": planos([
            ("Eres sepulturero en el panteón de Santa Paula, en Guanajuato. Es mil ochocientos sesenta y cinco, y abres una tumba por la que nadie pagó.", ["e3", "f1"], "GUANAJUATO, 1865"),
            ("Adentro no hay huesos. Hay un cuerpo seco, casi completo.", ["e5", "e1"], "UN CUERPO SECO"),
            ("Ese año, el gobierno empezó a cobrar un impuesto por los entierros. Si nadie pagaba, el cuerpo salía.", ["f1", "e1"], "EL IMPUESTO"),
            ("Y fueron saliendo más cuerpos conservados.", ["e2", "e5"], "SALEN MÁS"),
            ("La razón estaba en la tierra: el subsuelo de ese panteón tiene nitratos y alumbre.", ["f2", "e3"], "NITRATOS Y ALUMBRE"),
            ("Hoy la colección tiene ciento once cuerpos. Entre ellos, la que llaman la momia más pequeña del mundo.", ["f2", "e2"], "111 CUERPOS"),
            ("La primera fue la del médico francés Remigio Leroy. Así nacieron las momias de Guanajuato.", ["f1", "e4"], "REMIGIO LEROY"),
        ], ("¿Ya fuiste al museo? Comenta.", "¿YA FUISTE?")),
    },
    "guion-tt-chupacabras": {
        "nicho": "historia", "titulo": "La historia del chupacabras", "claves": ["chupacabras"],
        "fuentes": {"wiki": "https://es.wikipedia.org/wiki/Chupacabras (marzo de 1995: ocho ovejas muertas con tres heridas en el pecho; Madelyne Tolentino, Canóvanas; nombre del comediante Silverio Pérez; más de 200 reportes en 1995; Nayarit a mediados de los 90; análisis veterinario de 300 víctimas sin desangrar; Benjamin Radford: se parece a 'Sil' de Species; octubre de 2010 Barry O'Connor, U. de Míchigan: coyotes con sarna)"},
        "evidencia": [
            web("e1", "documento", "https://es.wikipedia.org/wiki/Chupacabras", "Wikipedia: Chupacabras"),
            web("e2", "documento", "https://en.wikipedia.org/wiki/Chupacabra", "Wikipedia (inglés): Chupacabra"),
            buscar("e3", "lugar", "Canóvanas Puerto Rico"), buscar("e4", "lugar", "Chupacabras"),
            buscar("e5", "lugar", "coyote mange"),
            ficha("f1", "Puerto Rico · marzo de 1995", ["Ocho ovejas muertas", "Tres heridas en el pecho", "Más de 200 reportes ese año"], "Wikipedia"),
            ficha("f2", "Lo que dijeron los expertos", ["300 supuestas víctimas: ninguna desangrada", "Se parece a la criatura de la película Especies", "2010: coyotes con sarna"], "Wikipedia"),
        ],
        "planos": planos([
            ("Eres ganadero en Puerto Rico. Es marzo de mil novecientos noventa y cinco, y aparecen ocho ovejas muertas, con tres heridas en el pecho.", ["e3", "f1"], "PUERTO RICO, 1995"),
            ("Una vecina de Canóvanas, Madelyne Tolentino, dice que vio a la criatura.", ["e4", "e1"], "LA TESTIGO"),
            ("Un comediante le pone el nombre que todos conocemos: chupacabras.", ["e4", "e2"], "EL NOMBRE"),
            ("Ese año hay más de doscientos reportes en la isla. Y a mediados de los noventa llega a México, con animales mutilados en Nayarit.", ["f1", "e1"], "LLEGA A MÉXICO"),
            ("Pero un análisis veterinario de trescientas supuestas víctimas no encontró que las hubieran desangrado.", ["f2", "e2"], "NO LAS DESANGRÓ"),
            ("El investigador Benjamin Radford concluyó que la descripción de la testigo se parecía a la criatura de la película Especies.", ["f2", "e1"], "UNA PELÍCULA"),
            ("Y en dos mil diez, un biólogo de la Universidad de Míchigan dio otra explicación para Estados Unidos: coyotes con sarna.", ["e5", "f2"], "COYOTES CON SARNA"),
        ], ("¿Tú creíste en el chupacabras? Comenta.", "¿TÚ CREÍSTE?")),
    },
    "guion-tt-juan-soldado": {
        "nicho": "historia", "titulo": "La historia de Juan Soldado", "claves": ["soldado", "castillo"],
        "fuentes": {"es": "https://es.wikipedia.org/wiki/Juan_Soldado (Juan Castillo Morales, 23 años; ejecutado el 17/02/1938 en el cementerio de Tijuana por la ley fuga; tribunal militar sumario; se declaró culpable; confesión y ropa ensangrentada; panteón número uno, Puerta Blanca; santo popular de los migrantes)",
                    "en": "https://en.wikipedia.org/wiki/Juan_Soldado (niña de ocho años; muchos dudaron de su culpa; milagros; miles de peregrinos)",
                    "nota": "No se nombra a la niña."},
        "evidencia": [
            web("e2", "documento", "https://en.wikipedia.org/wiki/Juan_Soldado", "Wikipedia (inglés)"),
            buscar("e3", "lugar", "Juan Soldado Tijuana capilla"), buscar("e4", "lugar", "Panteón Municipal 1 Tijuana"),
            buscar("e5", "lugar", "Tijuana 1930s"),
            ficha("f1", "Tijuana · febrero de 1938", ["Juan Castillo Morales, soldado, 23 años", "Acusado de matar a una niña de ocho años", "Juicio militar sumario"], "Wikipedia"),
            ficha("f2", "17 de febrero de 1938", ["Ley fuga en el panteón", "Pruebas: una confesión y ropa con sangre", "Muchos dudaron de su culpa"], "Wikipedia"),
        ],
        "planos": planos([
            ("Eres soldado en Tijuana. Es febrero de mil novecientos treinta y ocho, y a tu compañero lo acusan de matar a una niña de ocho años.", ["e5", "f1"], "TIJUANA, 1938"),
            ("Se llama Juan Castillo Morales. Tiene veintitrés años.", ["f1", "e1"], "23 AÑOS"),
            ("Un tribunal militar lo juzga en un juicio sumario. Él se declara culpable.", ["f1", "e2"], "JUICIO SUMARIO"),
            ("El diecisiete de febrero lo llevan al panteón y le aplican la ley fuga: lo dejan correr, y le disparan.", ["f2", "e4"], "LA LEY FUGA"),
            ("Había pruebas en su contra: una confesión y ropa con sangre. Aun así, mucha gente empezó a dudar.", ["f2", "e1"], "LA DUDA"),
            ("Y empezaron a contar milagros en su tumba.", ["e3", "e2"], "MILAGROS"),
            ("Hoy le dicen Juan Soldado. La Iglesia no lo reconoce, pero miles le rezan en el panteón número uno de Tijuana, sobre todo migrantes.", ["e3", "e4"], "JUAN SOLDADO"),
        ], ("¿Habías oído de Juan Soldado? Comenta.", "¿LO CONOCÍAS?")),
    },
    "guion-tt-pedro-infante-merida": {
        "nicho": "historia", "titulo": "La historia de la muerte de Pedro Infante", "claves": ["infante"],
        "fuentes": {"wiki": "https://es.wikipedia.org/wiki/Pedro_Infante (15/04/1957 entre 7:30 y 8:00; C-87 Liberator Express XA-KUN de TAMSA, de la que era socio; de Mérida a la Ciudad de México; unos 200 m; calle 54 Sur y 87; cinco muertos: tres tripulantes y dos personas en tierra; error de maniobra y probable corrimiento de la carga, llevaba pescado; funeral en la Ciudad de México el 17 de abril, Panteón Jardín)",
                    "nota": "Las dos víctimas en tierra eran menores: no se nombran."},
        "evidencia": [
            web("e1", "documento", "https://es.wikipedia.org/wiki/Pedro_Infante", "Wikipedia: Pedro Infante"),
            buscar("e2", "persona", "Pedro Infante"), buscar("e3", "lugar", "Consolidated C-87 Liberator Express"),
            buscar("e4", "lugar", "Mérida Yucatán centro"),
            ficha("f1", "Mérida · 15 de abril de 1957", ["Entre las 7:30 y las 8:00", "Un avión de carga hacia la Ciudad de México", "Cae en la calle 54 Sur con 87"], "Wikipedia"),
            ficha("f2", "El accidente", ["Cinco muertos: tres tripulantes y dos personas en tierra", "Error de maniobra", "La carga, mal acomodada, se habría corrido"], "Wikipedia"),
        ],
        "planos": planos([
            ("Vives en Mérida. Es el quince de abril de mil novecientos cincuenta y siete, cerca de las ocho de la mañana, y ves un avión que acaba de despegar.", ["e4", "f1"], "MÉRIDA, 1957"),
            ("Es un avión de carga que va a la Ciudad de México. Lleva pescado.", ["e3", "f1"], "UN AVIÓN DE CARGA"),
            ("Sube unos doscientos metros. Y se desploma en pleno centro, en la calle cincuenta y cuatro sur con ochenta y siete.", ["f1", "e4"], "CALLE 54 CON 87"),
            ("Mueren los tres de la tripulación y dos personas en tierra.", ["f2", "e1"], "CINCO MUERTOS"),
            ("La investigación dijo error de maniobra, y que la carga, mal acomodada, probablemente se corrió.", ["f2", "e3"], "LA CARGA"),
            ("En la cabina iba uno de los hombres más famosos de México. Era socio de la empresa del avión.", ["e1", "e4"], "EN LA CABINA"),
            ("Era Pedro Infante. Dos días después, la Ciudad de México lo despidió en el Panteón Jardín.", ["e2", "e5"], "PEDRO INFANTE"),
        ], ("¿En tu casa todavía ven sus películas? Comenta.", "¿TODAVÍA LO VEN?")),
    },
    # ---------------------------------------------------------- MARFIL (secuestros de herederos)
    "guion-tt-patty-hearst": {
        "nicho": "marfil", "titulo": "La historia de Patty Hearst", "claves": ["hearst"],
        "fuentes": {"wiki": "https://en.wikipedia.org/wiki/Patty_Hearst (4/02/1974, 19 años, departamento de Berkeley, Ejército Simbionés de Liberación; 'Tania' en abril; asalto al Hibernia Bank el 15/04/1974 grabado; detenida el 18/09/1975; F. Lee Bailey: lavado de cerebro y síndrome de Estocolmo; Carter conmutó, libre el 1/02/1979; Clinton la indultó el 20/01/2001; nieta de William Randolph Hearst)"},
        "evidencia": [
            web("e2", "documento", "https://es.wikipedia.org/wiki/Patty_Hearst", "Wikipedia: Patty Hearst"),
            foto("e3", "persona", "File:Patty Hearst- Hibernia bank robbery.jpg"), foto("e4", "persona", "File:Patty Hearst FBI poster.jpg"),
            buscar("e5", "persona", "William Randolph Hearst"), buscar("e6", "lugar", "Berkeley California 1970s"),
            ficha("f1", "Berkeley, California · 4 de febrero de 1974", ["Una joven de 19 años es secuestrada", "Por el Ejército Simbionés de Liberación"], "Wikipedia"),
            ficha("f2", "15 de abril de 1974", ["Una cámara la graba asaltando un banco", "Ahora se llama \"Tania\""], "Wikipedia"),
            ficha("f3", "Después", ["Detenida en septiembre de 1975", "Carter le reduce la pena (1979)", "Clinton la indulta (2001)"], "Wikipedia"),
        ],
        "planos": planos([
            ("Eres la nieta de uno de los hombres más ricos de Estados Unidos. Tienes diecinueve años, y el cuatro de febrero de mil novecientos setenta y cuatro te sacan a la fuerza de tu departamento en Berkeley.", ["e6", "f1"], "BERKELEY, 1974"),
            ("Te secuestra un grupo armado: el Ejército Simbionés de Liberación.", ["f1", "e1"], "SECUESTRADA"),
            ("Dos meses después, en una grabación, dices que te uniste a ellos. Que ahora te llamas Tania.", ["f2", "e2"], "AHORA ES TANIA"),
            ("El quince de abril, una cámara te graba con un arma, asaltando un banco en San Francisco.", ["e3", "f2"], "EL ASALTO"),
            ("Te detienen en septiembre de mil novecientos setenta y cinco. Tu abogado dice que te lavaron el cerebro: síndrome de Estocolmo.", ["f3", "e1"], "¿LAVADO DE CEREBRO?"),
            ("Te condenan. El presidente Jimmy Carter te reduce la pena, y Bill Clinton te indulta en dos mil uno.", ["f3", "e2"], "INDULTADA"),
            ("Se llama Patty Hearst. Su abuelo era William Randolph Hearst, el magnate de los periódicos.", ["e4", "e5"], "PATTY HEARST"),
        ], ("Si viste Marfil, esto sí pasó. ¿Víctima o cómplice? Comenta.", "¿VÍCTIMA O CÓMPLICE?")),
    },
    "guion-tt-bosco-gutierrez-cortina": {
        "nicho": "marfil", "titulo": "La historia de Bosco Gutiérrez Cortina", "claves": ["bosco", "gutierrez", "tres metros cuadrados", "257 días"],
        "fuentes": {"razon": "https://www.razon.com.mx/entretenimiento/2025/09/16/quien-es-bosco-gutierrez-cortina-hombre-que-escapo-tras-9-meses-secuestrado/ (29/08/1990 tras misa; dos hombres; 33 años; primeros 16 días en un cuarto para anular sus sentidos; pidió una Biblia; tres intentos de pago; escapó)",
                    "almudi": "https://www.almudi.org/noticias-articulos-y-opinion/16676-la-libertad-en-tres-metros-cuadrados (257 días; 3 m por 1.5; diario de unas 700 hojas; película Espacio interior de Kai Parlange; 'Yo estuve secuestrado nueve meses y me escapé')",
                    "nota": "La Razón dice 275 días; el libro y Almudí, 257: se usa 257."},
        "evidencia": [
            web("e1", "prensa", "https://www.razon.com.mx/entretenimiento/2025/09/16/quien-es-bosco-gutierrez-cortina-hombre-que-escapo-tras-9-meses-secuestrado/", "La Razón, 16/09/2025"),
            web("e2", "prensa", "https://www.almudi.org/noticias-articulos-y-opinion/16676-la-libertad-en-tres-metros-cuadrados", "Almudí"),
            web("e3", "documento", "https://www.lecturalia.com/libro/73103/257-dias", "Lecturalia: 257 días"),
            buscar("e4", "lugar", "Ciudad de México 1990"),
            ficha("f1", "Ciudad de México · 29 de agosto de 1990", ["Un arquitecto de 33 años sale de misa", "Dos hombres lo suben a un coche"], "La Razón"),
            ficha("f2", "El cuarto", ["Tres metros por uno y medio", "257 días", "Escribió un diario de unas 700 hojas"], "Almudí"),
        ],
        "planos": planos([
            ("Eres arquitecto en la Ciudad de México. Es el veintinueve de agosto de mil novecientos noventa, sales de misa, y dos hombres te suben a un coche.", ["e4", "f1"], "CDMX, 1990"),
            ("Te encierran en un cuarto de tres metros por uno y medio.", ["f2", "e2"], "3 METROS POR 1.5"),
            ("Tienes treinta y tres años y una familia que te espera.", ["f1", "e1"], "33 AÑOS"),
            ("Los primeros días caes en depresión. Luego pides una Biblia, y empiezas a escribir un diario.", ["e1", "e2"], "UN DIARIO"),
            ("Tu familia intenta pagar el rescate tres veces.", ["e1", "e3"], "TRES INTENTOS"),
            ("Pasan doscientos cincuenta y siete días. Y logras escapar.", ["f2", "e3"], "257 DÍAS"),
            ("Se llama Bosco Gutiérrez Cortina. Su diario se volvió la película Espacio interior.", ["e5", "e2"], "BOSCO GUTIÉRREZ"),
        ], ("Si viste Marfil, esto sí pasó en México. ¿Tú habrías aguantado? Comenta.", "¿HABRÍAS AGUANTADO?")),
    },
    "guion-tt-sinatra-junior": {
        "nicho": "marfil", "titulo": "La historia del secuestro de Frank Sinatra Jr.", "claves": ["sinatra"],
        "fuentes": {"wiki": "https://en.wikipedia.org/wiki/Frank_Sinatra_Jr. (8/12/1963, Harrah's Lake Tahoe, cuarto 417; 19 años; su padre ofreció un millón y pagó 240 mil dólares; liberado dos días después; Barry Keenan, Johnny Irwin y Joe Amsler; Keenan, el cerebro, declarado legalmente demente al momento del crimen; cumplieron poco)"},
        "evidencia": [
            web("e1", "documento", "https://en.wikipedia.org/wiki/Frank_Sinatra_Jr.", "Wikipedia: Frank Sinatra Jr."),
            web("e2", "documento", "https://es.wikipedia.org/wiki/Frank_Sinatra_Jr.", "Wikipedia: Frank Sinatra Jr."),
            buscar("e3", "persona", "Frank Sinatra Jr. 1963"), buscar("e4", "persona", "Frank Sinatra 1960s"),
            buscar("e5", "lugar", "Harrah's Lake Tahoe"), foto("e6", "persona", "File:Frank Sinatra Jr. (1965).jpg"),
            ficha("f1", "Lake Tahoe · 8 de diciembre de 1963", ["Hotel Harrah's, cuarto 417", "Un joven de 19 años es secuestrado"], "Wikipedia"),
            ficha("f2", "El rescate", ["El padre ofrece un millón de dólares", "Los secuestradores piden 240 mil", "Lo liberan dos días después"], "Wikipedia"),
        ],
        "planos": planos([
            ("Eres el hijo de uno de los cantantes más famosos del mundo. Tienes diecinueve años, es el ocho de diciembre de mil novecientos sesenta y tres, y estás en el cuarto cuatrocientos diecisiete del hotel Harrah's, en Lake Tahoe.", ["e5", "f1"], "LAKE TAHOE, 1963"),
            ("Ahí te secuestran.", ["f1", "e1"], "SECUESTRADO"),
            ("Tu padre ofrece un millón de dólares. Los secuestradores piden menos: doscientos cuarenta mil.", ["f2", "e2"], "PIDEN MENOS"),
            ("Él paga. Y dos días después te liberan.", ["f2", "e1"], "DOS DÍAS"),
            ("Detienen a tres hombres. El cerebro era Barry Keenan.", ["e2", "e5"], "TRES DETENIDOS"),
            ("Los condenan a penas largas, pero cumplen poco. A Keenan, después, lo declaran legalmente demente al momento del crimen.", ["e1", "f2"], "CUMPLEN POCO"),
            ("Eras Frank Sinatra Junior. Y tu padre, Frank Sinatra.", ["e6", "e4"], "FRANK SINATRA JR."),
        ], ("Si viste Marfil, esto sí pasó. ¿Habrías pagado? Comenta.", "¿HABRÍAS PAGADO?")),
    },
    "guion-tt-secuestro-heineken": {
        "nicho": "marfil", "titulo": "La historia del secuestro de Freddy Heineken", "claves": ["heineken"],
        "fuentes": {"wiki": "https://en.wikipedia.org/wiki/Freddy_Heineken (1983, con su chofer Ab Doderer; 35 millones de florines; liberados tras pagar; Cor van Hout, Willem Holleeder, Jan Boellaard, Frans Meijer y Martin Erkamps; Van Hout y Holleeder más de tres años en Francia antes de ser extraditados; Meijer en Paraguay hasta que lo encontró Peter R. de Vries; películas de 2011 y 2015, una con Anthony Hopkins)",
                    "nota": "Ámsterdam: el lugar del secuestro no viene en la página; no se dice."},
        "evidencia": [
            web("e1", "documento", "https://en.wikipedia.org/wiki/Freddy_Heineken", "Wikipedia: Freddy Heineken"),
            web("e2", "documento", "https://es.wikipedia.org/wiki/Freddy_Heineken", "Wikipedia: Freddy Heineken"),
            buscar("e3", "persona", "Freddy Heineken"), buscar("e4", "lugar", "Heineken brewery Amsterdam"),
            buscar("e5", "persona", "Willem Holleeder"),
            foto("e6", "persona", "File:Dhr. Heineken (l) en dhr. Doderer, Bestanddeelnr 932-7956.jpg"),
            foto("e7", "persona", "File:Na de ontvoering van directeur Freddy Heineken van bierbrouwerij Heineken wordt , Bestanddeelnr 932-7760.jpg"),
            ficha("f1", "Países Bajos · 1983", ["Secuestran al dueño de Heineken y a su chofer", "Piden 35 millones de florines"], "Wikipedia"),
            ficha("f2", "Los secuestradores", ["Eran cinco", "Dos huyeron a Francia: más de tres años", "Otro, a Paraguay"], "Wikipedia"),
        ],
        "planos": planos([
            ("Eres el dueño de una de las cerveceras más grandes del mundo. Es mil novecientos ochenta y tres, y unos hombres se los llevan a ti y a tu chofer.", ["e4", "f1"], "PAÍSES BAJOS, 1983"),
            ("Tu chofer se llama Ab Doderer.", ["e6", "f1"], "EL CHOFER"),
            ("Piden treinta y cinco millones de florines.", ["f1", "e2"], "35 MILLONES"),
            ("Se paga el rescate, y los liberan.", ["e7", "e4"], "LIBERADOS"),
            ("Los secuestradores eran cinco. Dos de ellos, Cor van Hout y Willem Holleeder, huyeron a Francia.", ["f2", "e5"], "HUYEN A FRANCIA"),
            ("Pasaron más de tres años allá antes de ser extraditados. Otro escapó a Paraguay, hasta que un periodista lo encontró.", ["f2", "e2"], "PARAGUAY"),
            ("Eras Freddy Heineken. Tu secuestro se volvió película, y en una de ellas Anthony Hopkins hace de ti.", ["e3", "e1"], "FREDDY HEINEKEN"),
        ], ("Si viste Marfil, esto sí pasó. Comenta.", "ESTO SÍ PASÓ")),
    },
    "guion-tt-zapata-sodi": {
        "nicho": "marfil", "titulo": "La historia del secuestro de las hermanas de Thalía", "claves": ["zapata", "sodi"],
        "fuentes": {"excelsior": "https://www.excelsior.com.mx/espectaculos/laura-zapata-y-ernestina-sodi-fue-secuestro-que-termino-separando-hermanas-thalia (22/09/2002, al salir de La casa de Bernarda Alba; camioneta les cierra el paso; rompen el vidrio con la culata; 'Que se lleven el coche'; casa de seguridad; esperaban que pagara Tommy Mottola; Laura liberada primero; unos 45 días; Líbranos del mal, 2005)",
                    "nota": "No se usan las acusaciones entre las hermanas ni los días exactos de cada una (las fuentes no coinciden)."},
        "evidencia": [
            web("e1", "prensa", "https://www.excelsior.com.mx/espectaculos/laura-zapata-y-ernestina-sodi-fue-secuestro-que-termino-separando-hermanas-thalia", "Excélsior"),
            web("e2", "prensa", "https://www.elfinanciero.com.mx/espectaculos/2026/07/16/secuestrador-de-laura-zapata-presenta-amparo-y-citan-a-la-actriz/", "El Financiero, 16/07/2026"),
            web("e3", "prensa", "https://www.nmas.com.mx/entretenimiento/quien-era-ernestina-sodi-de-que-murio-historia-mama-camila-sodi-sufrio-secuestro/", "N+"),
            buscar("e4", "persona", "Laura Zapata actriz"), buscar("e5", "lugar", "Ciudad de México noche avenida"),
            ficha("f1", "Ciudad de México · 22 de septiembre de 2002", ["Salen de una función de La casa de Bernarda Alba", "Una camioneta les cierra el paso", "Un hombre armado rompe el vidrio"], "Excélsior"),
            ficha("f2", "Después", ["Las llevan a una casa de seguridad", "Liberan primero a una", "Unos 45 días en total"], "Excélsior"),
        ],
        "planos": planos([
            ("Eres actriz en la Ciudad de México. Es la noche del veintidós de septiembre de dos mil dos, y sales con tu hermana de una función de La casa de Bernarda Alba.", ["e5", "f1"], "CDMX, 2002"),
            ("Una camioneta les cierra el paso. Un hombre armado rompe el vidrio con la culata.", ["f1", "e1"], "EL VIDRIO"),
            ("Tú le dices: que se lleven el coche. Pero no quieren el coche. Las quieren a ustedes.", ["f1", "e2"], "NO QUIEREN EL COCHE"),
            ("Las llevan a una casa de seguridad. Esperan que pague el esposo de su hermana más famosa.", ["f2", "e1"], "LA CASA DE SEGURIDAD"),
            ("Primero liberan a una. La otra sale días después. Todo dura unos cuarenta y cinco días.", ["f2", "e3"], "45 DÍAS"),
            ("Años después, cada una contó una versión distinta. Y dejaron de hablarse.", ["e3", "e2"], "DOS VERSIONES"),
            ("Eran Laura Zapata y Ernestina Sodi, hermanas de Thalía. Ernestina lo contó en el libro Líbranos del mal.", ["e4", "e1"], "LAS HERMANAS DE THALÍA"),
        ], ("Si viste Marfil, esto sí pasó en México. Comenta.", "ESTO SÍ PASÓ")),
    },
}

if __name__ == "__main__":
    for slug, d in GUIONES.items():
        ids = {e["id"] for e in d["evidencia"]}
        for pl in d["planos"]:
            if "evidencia" in pl["visual"]:
                pl["visual"]["evidencia"] = [e for e in pl["visual"]["evidencia"] if e in ids]
        guion = {
            "_schema": {"descripcion": "Short de Dato Mata Gato, FORMATO TENDENCIA (prueba de búsquedas de "
                                       f"TikTok, nicho '{d['nicho']}'): segunda persona, foto real al final, 45-60 s.",
                        "fuentes": d["fuentes"]},
            "titulo": d["titulo"], "gancho": d["planos"][0]["texto_en_pantalla"], "claves": d.get("claves", []),
            "hashtags": HASHTAGS[d["nicho"]], "evidencia": d["evidencia"], "planos": d["planos"],
        }
        carpeta = Path(r"C:\Android_in") / slug
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / "guion.json").write_text(json.dumps(guion, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{d['nicho']:8} {slug}: {sum(len(p['narracion'].split()) for p in d['planos'])} palabras")
