
# Qué atacar para volvernos virales, sin sonar a máquina — 03/11/2026

Dos preguntas de Javier. Resulta que tienen la misma respuesta, y no está en el guion.

Lo miden `tools/huella_automatizacion.py` y `tools/pilar_valor_practico.py`.

## Lo primero: el guion no es el problema

Revisé si algún pilar se estaba saltando. No. Los 91 guiones del canal desde el 14/10:

| Pilar | Presencia |
|---|---|
| 1 te afecta | 100% |
| 2 está pasando ahorita | 100% |
| 3 algo no cuadra | 100% |
| 4 coraje | 100% |
| 5 se puede grabar | 100% |
| 6 hace hablar | 89% |
| **7 valor práctico** (el de compartidos) | **96%** |

Supuse dos veces que faltaba algo — primero que la fórmula ignoraba los compartidos, luego que
el pilar 7 por ser opcional se estaba quedando fuera. **Las dos suposiciones estaban mal.** La
instrucción trae a Berger y Milkman explícitos, y el pilar 7 se escribe en 87 de 91 guiones.

Entonces: **todo lo que la fórmula pide, se entrega.** Lo que haya que atacar está en las capas
que la fórmula no gobierna.

## 2. La huella de automatización, medida

Esto es lo que se ve desde el perfil:

```
esqueletos distintos en 91 videos:  1       (p00→p08, 100%)
p08 arranca "aquí el dato mata al gato":  100%
p08 cierra "cuéntamelo en los comentarios":  93%
p01 arranca "te imaginas a...":   75%
#datomatagato:  100%
```

Y lo que **no** es repetitivo, que importa igual:

```
primeras palabras del p00 (el primer segundo real):  11% máximo  -> variado
forma del título:  19% con el remate seco  -> variado, solo un remate repetido
```

### Dónde está concentrada la huella

No está en todas partes. Está en **dos lugares**:

**a) El p01, segundo ~3 del video. 75% abre con "Te imaginas a quien…"**
La especificación dice "(una sola vez)" queriendo decir una vez por video — y se volvió una vez
en *todos* los videos. Tres de cada cuatro arrancan con la misma construcción, justo en el
segundo donde TikTok decide si reparte. Quien ya vio dos videos del canal reconoce el patrón y
se va. **Si solo se cambia una cosa, es esta.**

**b) Un solo esqueleto en 91 videos.** p00→p08 siempre, lo que implica misma duración y mismo
ritmo siempre. Un formato = una rebanada de público.

El p08 ("aquí el dato mata al gato") al 100% **lo defiendo**: una frase de cierre reconocible es
marca, no defecto — todos los canales que funcionan tienen una. El problema no es que exista,
es que sea el único punto fijo que la gente nota junto con el p01.

## 3. Por qué no nos volvemos virales: el techo está en los pilares obligatorios

Aquí está lo incómodo, y es estructural, no un error de ejecución.

**Pilar 1, te afecta:** "le pasa a casi cualquiera que vive **ahí**: su recibo, su colonia, su
camión, su playa." Eso es relevancia local por construcción. Un video sobre el recibo de agua de
Cancún es máximamente relevante en Cancún e irrelevante en Monterrey. Y el inventario lo
confirma: **74 videos de Quintana Roo, 39 de CDMX, el resto ≤7.**

**Pilar 6, hace hablar**, y es el criterio de selección *primero*: "Elige primero por esto y
después por qué tan reciente es." Selecciona temas donde quien ve **tiene algo que contar**. Eso
produce comentarios — o sea, profundidad con el público que ya tienes. Los compartidos son los
que traen público nuevo.

> **La fórmula es una máquina de retención y comentarios, ejecutada casi perfecto. Lo viral
> necesita alcance, y dos de los pilares obligatorios le ponen techo al alcance.**

No está roto: está optimizado para otra cosa. Funcionó cuando el canal era de Cancún para
Cancún (los 4–5 mil vistas). Las fórmulas nuevas son nacionales, pero el pilar 1 sigue pidiendo
"ahí".

Y la instrucción **ya tiene el modo nacional**, en las líneas 80–81: para temas no locales, la 1
pasa a ser "que le toque a quien vive en México hoy" y la 5 "que haya un lugar, un objeto o un
documento real". Existe. Solo es la excepción y no el camino normal.

## 4. Qué atacar, en orden de palanca

### A. Romper la uniformidad del p01 — barato, inmediato, bajo riesgo
75% → meta debajo de 30%. Escribir cuatro o cinco construcciones alternativas **dentro de la
descripción del p01**, no en una regla aparte. Sabemos que eso funciona: la auditoría de
cumplimiento mostró que lo escrito dentro del plano se cumple al 100% (p08), y la regla de sí/no
bajó de 24% a 3% en una semana. Es la palanca más validada que tenemos.

### B. La forma que sí viaja: lo local que revela lo nacional
No es "dejar de ser local" — es que el caso local **destape un número nacional**. Esa pieza se
comparte en los dos lados: el de aquí porque le toca, el de fuera porque el número aplica en su
estado.

El candidato de maltrato animal tiene exactamente esa forma:
**Iztapalapa 439 denuncias (local) → 2,600 nacionales → Puebla 1,010 carpetas y 11 sentencias
(el número que aplica en cualquier estado).** Por eso lo puse primero, y ahora se ve por qué.

Lo contrario, el permiso de un puesto de cohetes en Xilitla, no sale de Xilitla aunque cumpla
los siete pilares.

### C. Variar el esqueleto — más riesgo, mejor hacerlo después del export
Permitir variantes de 6 y de 12 planos para que duración y ritmo cambien. Esto sí toca el
corazón de la instrucción, y la instrucción es lo único que sabemos que funciona. **No antes de
tener el export.**

### D. Cambiar el criterio de selección, solo para los intentos virales
Cuando el objetivo sea alcance y no profundidad, elegir primero por "¿esto le sirve a alguien de
otro estado?" en vez de por "hace hablar". No cambiar el pilar 6 — **agregar** un modo.

## Recomendación

**Hacer ahora: A y B.** A es un cambio chico en el p01 con mecanismo validado. B no cambia nada
del código: es elegir temas con la forma local→nacional, y ya hay uno listo y verificado.

**Esperar al export: C y D.** Son cambios al núcleo, y seguimos sin saber si la caída a ~200
vistas fue alcance, la semana de portada rota, o el público. Mover el núcleo a ciegas es el
único error caro que queda disponible.
