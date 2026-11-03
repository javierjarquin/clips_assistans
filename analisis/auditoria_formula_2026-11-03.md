# Auditoría de la fórmula — 03/11/2026

Autorizada por Javier el 03/11/2026. Cruce de lo producido contra su rendimiento.

## Resumen

El inventario local quedó completo: **328 videos** clasificados por lote, fórmula, estado,
portada y fecha (`analisis/inventario_videos.csv`, lo arma `tools/auditar_formula.py`).

Las métricas **no están puestas todavía** y hay una razón de fondo, no de esfuerzo: pedirlas
rodeando el captcha de TikTok daría menos dato que el export oficial, y una de las dos
preguntas de la auditoría no se puede contestar con los datos que existen. Las dos cosas se
explican abajo.

## 1. Lo que sí quedó medido (sin métricas todavía)

| Fórmula | Videos | Con portada |
|---|---|---|
| contradicción local | 211 | 19 |
| viral | 36 | 34 |
| tendencia TikTok | 23 | 0 |
| polémica | 22 | 20 |
| comparativa | 9 | 9 |
| tradiciones | 7 | 7 |
| (sin clasificar) | 20 | 4 |

Estados: Quintana Roo 74, CDMX 39, Yucatán 10, Tamaulipas 7, Edomex 6, Veracruz 6, Jalisco 6,
Nuevo León 6, resto ≤4. 135 sin estado (son POCs y trivia, no piezas de canal).

**El disco no sabe qué se publicó.** 328 videos en disco, 93 con portada, y Javier sube a mano.
El export de TikTok es la única lista autoritativa de lo que salió — por eso el empalme va del
export hacia el inventario y no al revés (`tools/empalmar_tiktok.py`).

## 2. La comparación de portadas no se puede hacer, y ya está decidida

Era la mitad de la pregunta. Cuatro problemas, en orden de gravedad:

**a) El JPG en disco no es la portada que vio la gente.** TikTok no usa el cuadro 0 — validado
el 30/10 y el 03/11: con la gancho pegada 1/30 s y luego 0.2 s, escogió otros cuadros (0.13 s,
0.3–1 s, 7 s). Entonces que exista `_portada_gancho.jpg` significa *que se generó el archivo*,
no que se mostró. Salvo que se haya subido a mano en "Editar portada", la miniatura real fue un
cuadro semialeatorio. Cruzar esa columna contra vistas mide una variable que casi no llegó al
público.

**b) Cero traslape de fechas.** Gancho: 29/10 → 03/11 (3 días distintos). Nota: 14/10 → 28/10
(8 días). **No hubo un solo día con las dos.** Cualquier diferencia es la portada o es el
calendario, y no hay forma de separarlas.

**c) La mezcla de fórmulas es distinta.** Las 7 de tradiciones son gancho (0 nota); las 19 de
contradicción local son nota (0 gancho). "Gancho vs nota" es en parte "tradiciones vs
contradicción local": dos nichos con públicos distintos.

**d) 5 de los 21 gancho son de hoy** (lote `redes-20261103-0724`). Sin tiempo para juntar
vistas; en un promedio jalarían al gancho hacia abajo por motivos ajenos a la portada.

Y lo de fondo: **ya lo decidiste hoy** con mejor evidencia que la que daría este cruce — la
gancho nunca salió bien en el perfil y los videos más vistos del canal (4–5 mil) son de estilo
nota. Un mecanismo observado vale más que una diferencia de promedios entre 21 y 72 videos que
nunca corrieron juntos. **Recomendación: sacar la portada de la auditoría.** Está resuelta.

Lo que sí queda en pie y no está decidido: **fórmula** y **estado/ciudad**, que sí varían a lo
largo de una ventana larga y con mezcla cruzada.

## 3. Las métricas: el export, no el scraping

`/embed/@datomatagato` y variantes están detrás de captcha a propósito, y rodearlo no es el
camino. Además daría peor dato. **TikTok Studio → Analytics → Descargar datos** da vistas,
likes, comentarios y compartidos **más** lo que decide de verdad en una auditoría de ganchos:

- tiempo promedio visto y % que llegó al final → si el gancho funciona se ve aquí, no en vistas
- de dónde vino el tráfico (Para ti / perfil / búsqueda) → separa "la portada atrajo" de "el
  algoritmo repartió"
- vistas por segundo del video → dónde exactamente se cae la gente

En cuanto tengas el CSV:

```
C:\dato-mata-gato-bot\.venv\Scripts\python.exe C:\clip_assistance\tools\empalmar_tiktok.py <ruta_del_export.csv>
```

Detecta las columnas por alias (sirve en español o inglés), amarra por título normalizado con
parecido difuso, y escribe `analisis/formula_vs_metricas.csv` más `analisis/sin_empalmar.csv`
con lo que no logró amarrar.

## 4. Lo viral de la semana en el nicho (28/10 – 03/11/2026)

Separado en lo que sirve a cada fórmula.

### Sirve a contradicción local (hay documento y afecta)

- **Tepotzotlán, Edomex — obra pública sin registrar.** Regidores exhibieron modificaciones al
  Programa Anual de Obras: proyectos sin registrar y trabajos **iniciados antes de pasar por
  Cabildo**. Es la forma exacta de la fórmula: te afecta, está pasando, el papel no cuadra, y se
  puede mostrar el acta. El mejor candidato de la semana.
- **Nuevo León — presupuesto 2027.** Alcaldes piden no aprobarlo hasta liquidar el adeudo;
  drenaje sanitario y agua del área metropolitana sin mantenimiento. Perenne con gancho de
  actualidad.

### Sirve a tema viral (se está hablando, tres niveles)

- **Miss Universe 2025 y Fátima Bosch** — +72.1 mil publicaciones en TikTok esta semana. Es la
  conversación más grande del país ahora mismo y tiene nivel documental (reglamento del
  concurso) además del rumor.
- **Timbiriche / Sasha Sokol vs Luis de Llano** — comunicado del grupo el 03/11. Tiene lo que
  pide la fórmula: lo que se dice, lo que está en papel (la sentencia civil ya existe) y lo que
  nadie ha contestado. Cuidado: tema de abuso, requiere manejo cuidadoso.

### Virales de indignación (alto engagement, sin documento)

Jalan comentarios pero **no pasan el candado de evidencia**: tortería de Tampico (robo de
propinas en cámaras), pelea en el Tren El Insurgente, maltrato de un perrito en supermercados.
Sirven como gancho de apertura si el cuerpo lo sostiene un dato verificable; solos, no.

### Contexto de formato

Noviembre arrancó con Día de Muertos y Todos los Santos (ofrendas, pan de muerto, catrinas) —
coincide con el nicho de tradiciones, que justo estrenó el 30/10. El formato que domina el mes
es **"el giro final"**: carruseles y POV donde el remate llega al cierre.

## 5. Siguiente paso

1. Bajar el export de TikTok Studio y correr `empalmar_tiktok.py`.
2. Con eso, la auditoría se cierra sobre fórmula y estado — las dos preguntas que sí tienen
   respuesta en los datos.
3. Para el próximo cambio de portada (si lo hay): **correr las dos el mismo día**, mitad y
   mitad, subiendo el JPG a mano en "Editar portada". Sin traslape de fechas no hay auditoría
   posible, solo una diferencia que se puede contar como se quiera.

## Fuentes

- [Tepotzotlán, opacidad en obra pública](https://www.mexiquensenoticias.com/mas-dinero-menos-cuentas-cabildo-exhibe-opacidad-en-obra-publica-de-tepotzotlan/)
- [Presupuesto 2027 Nuevo León](https://www.telediario.mx/politica/presupuesto-2027-nl-alcaldes-piden-no-aprobarlo-liquidar-adeudo)
- [Tendencias TikTok 3–7 de noviembre (Milenio)](https://www.milenio.com/virales/descubre-tendencias-tiktok-03-noviembre-07-videos-virales-tiktok)
- [Timbiriche y Sasha Sokol](https://www.infobae.com/mexico/2026/11/03/timbiriche-defiende-a-sasha-sokol-y-reconoce-su-lucha-contra-luis-de-llano-por-acusaciones-de-abuso-infantil-eso-si-vale-la-pena-recordar/)
- [Tortería de Tampico](https://www.infobae.com/mexico/deportes/2026/11/03/exhiben-a-padre-e-hijo-robando-las-propinas-de-empleados-de-una-torteria-en-tampico/)
- [Tren El Insurgente](https://www.infobae.com/mexico/2026/11/03/mujeres-protagonizan-brutal-enfrentamiento-en-el-tren-el-insurgente-y-pasajeros-captan-todo-en-video/)
- [Trends de noviembre 2026](https://www.que.es/2026/10/30/trends-tiktok-noviembre-2026/)
