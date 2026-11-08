# ¿Hay que ajustar la fórmula? — 03/11/2026

Pregunta de Javier: con lo de la indignación, ¿la fórmula cuadra o hay que modificar algo
nuestro? Esto se puede contestar **sin métricas de TikTok**, comparando los 402 guiones en
disco contra la especificación en `instruccion_cercania.py`.

Lo arman `tools/auditar_cumplimiento.py`, `tools/cumplimiento_por_epoca.py` y
`tools/pregunta_a_la_mitad.py`. Detalle por guion en `analisis/cumplimiento_formula.csv`.

## Respuesta corta

**La fórmula no necesita cambios, y hay que resistir la tentación de cambiarla.** Se está
cumpliendo entre el 85% y el 100% en las ocho exigencias. Lo único que de verdad se movió es
la **mezcla de vigencias**, y no porque alguien rompiera una regla — cambió la composición del
canal debajo de la regla.

## 1. La maquinaria funciona: todo lo que se escribió, se cumplió

217 guiones de fórmulas del canal, partidos por época (los de antes de la fábrica no se rigen
por reglas que todavía no existían):

| Exigencia | Antes de la fábrica | Fábrica temprana (14–20/10) | Desde el 21/10 |
|---|---|---|---|
| `plus.contradiccion` | 0% | **100%** | **100%** |
| `plus.mapa` | 0% | **100%** | **100%** |
| Sin evidencia | 64% | **0%** | **0%** |
| Cierre p08 con pregunta | 31% | **100%** | **100%** |
| Pregunta temprana (p01/p02) | 1% | 85% | **89%** |
| Pregunta a la mitad (p03/p04/p05) | 0% | — | **87%** |
| Las dos preguntas | 0% | — | **85%** |
| Regla de sí/no (del 21/10) | 24% la rompía | — | **3% la rompe** |

La regla de sí o no es el mejor ejemplo de que el sistema responde: entró el 21/10 y la
violación cayó de 24% a 3% (un guion de 38, `guion-polemica-lady-gringa-taqueria`: "¿Cuál es
tu sueldo?").

**El patrón detrás de todo esto:** una exigencia se cumple al 100% cuando está escrita *dentro*
de la descripción de su propio plano (p08 trae la plantilla de la pregunta en su texto), y se
cumple peor cuando solo vive en una regla flotante. Vale tenerlo presente para el próximo
cambio: **escribir la regla en el plano, no aparte.**

### Corrección de medición

Una primera pasada reportó 16% de cumplimiento en la pregunta a la mitad. **Ese número estaba
mal** y era un artefacto del detector: medía por tercios de posición, y con 9 planos el tercio
de en medio salía p04–p06. Pero 61 de las preguntas caen en **p03**, que la especificación sí
cuenta como "a la mitad" y el detector contaba como temprana. Con la ventana correcta
(p03/p04/p05) el cumplimiento real es **87%**. No hay hueco que tapar en la instrucción.

### Dónde caen las preguntas a quien ve

```
p01:  90   <- ventana temprana
p03:  61   <- ventana de la mitad
p04:  21   <- ventana de la mitad
p07:  22
p08:  82
```

`p02` y `p05` nunca reciben pregunta aunque la especificación los permite. No es defecto —
las preguntas se concentran en p01, p03 y p08, que es un reparto sano. Solo queda anotado.

## 2. Lo que sí se movió: la mezcla, por composición

`MEZCLA = {"conversacion": 3, "perenne": 2}` — objetivo 60% conversación. El canal va en **82%**.
Pero el desglose por fórmula enseña que nadie desobedeció:

| Fórmula | conversación | perenne | % conversación |
|---|---|---|---|
| contradicción local | 8 | 8 | **50%** |
| comparativa | 0 | 9 | **0%** |
| polémica | 22 | 0 | **100%** |
| viral | 36 | 0 | **100%** |

Contradicción local va en 50/50 — **cumple de más**, tiene más perennes que el objetivo.
Comparativa es perenne pura. Y polémica y viral son 100% conversación **por diseño**: hablan de
lo que se está hablando ahorita, no pueden ser perennes.

El 82% no es indisciplina: es que el volumen se movió a los nichos efímeros. **Viral + polémica
= 58 guiones contra 16 de contradicción local**, 3.6 a 1. La regla 3:2 se escribió cuando
contradicción local era el canal entero; hoy se aplica dentro de cada fórmula mientras la
mezcla del canal se decide en otra parte — en cuántos lotes de cada tipo se piden.

**"Que envejezca bien" era un objetivo de diseño del canal, y la composición lo fue dejando
atrás sin que nadie lo decidiera.** Eso sí es "algo de nosotros" que ajustar.

### Las dos salidas

1. **Mover el 3:2 al nivel del canal**, no de la fórmula: que la fábrica balancee *entre*
   fórmulas (más lotes de comparativa y contradicción local) en vez de solo *dentro* de cada
   una. Es un cambio en cómo se piden los lotes, no en la instrucción.
2. **Aceptar que viral y polémica son el motor efímero** y subirle a propósito la cuota de
   perennes a contradicción local y comparativa para compensar. Más barato, menos ordenado.

La #1 es la correcta si el objetivo de que envejezca bien sigue en pie.

## 3. Lo incómodo, y lo más importante

**Las ocho exigencias se cumplen, así que el cumplimiento no puede explicar la caída a ~200
vistas.** La fórmula se está ejecutando con fidelidad y el resultado bajó. Eso deja fuera la
hipótesis de que el problema está en la especificación del guion.

Lo que queda, por orden de sospecha:

1. **La etapa de la portada, que estuvo rota una semana.** Del 29/10 al 03/11 el pipeline generó
   una portada que TikTok no usó, y el perfil se llenó de rótulos azules tenues. Esa etapa no la
   gobierna la fórmula y es la que decide si alguien entra.
2. **La distribución.** Si el algoritmo repartió menos, ningún cambio de guion se nota.
3. **El público.** Quintana Roo 74 videos contra CDMX 39 y el resto ≤7: el canal nació para
   Cancún y las fórmulas nuevas son nacionales. Puede ser que la audiencia construida no sea la
   que recibe lo nuevo.

Las tres se separan con **una sola cosa: el export de TikTok Studio** (fuente de tráfico
distingue la #1 de la #2; audiencia por región la #3). Sin eso, cualquier ajuste a la fórmula
sería cambiar lo único que sabemos que está funcionando, a ciegas.

## Recomendación

1. **No tocar `instruccion_cercania.py`.** Cumple.
2. **Sí ajustar la mezcla de lotes** (opción 1 arriba) — es la única desviación real de un
   objetivo de diseño.
3. **Bajar el export antes de cualquier otro cambio.** Es lo que convierte esta auditoría de
   "se cumple la fórmula" en "la fórmula funciona", que no es lo mismo.
4. Para el próximo cambio de regla: escribirla **dentro del plano** que la ejecuta. Es lo que
   distingue las exigencias al 100% de las demás.
