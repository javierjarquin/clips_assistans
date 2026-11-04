# "Se sienten muy políticos" — qué dice el corpus y qué dice TikTok

Hipótesis de Javier (03/11/2026): los videos se sienten muy políticos y eso puede estar
costando alcance. Medición: `tools/cuanto_de_politico.py` sobre los 91 guiones del canal
desde el 14/10. Detalle en `analisis/cuanto_de_politico.csv`.

## Respuesta corta

**Tienes razón en la sensación y en que algo estructural está frenando el alcance. Pero lo
político no es el mecanismo**, y hay otro que sí está en la lista oficial de TikTok y que ya
habíamos medido sin saber que importaba tanto.

Hay que separar tres cosas que se confunden.

## 1. ¿Son políticos? Institucionales sí, partidistas no

| Quién es el actor del video | |
|---|---|
| solo gobierno | **52%** (47) |
| mixto | 34% (31) |
| solo privado | 10% (9) |
| sin actor | 4% (4) |

**86% tiene un actor de gobierno.** Tu percepción está bien calibrada: eso es lo que se siente.

Pero el matiz importa:

- **Lenguaje partidista o electoral: 5%** (5 de 91). Morena 3 veces, y una mención cada uno de
  campaña, voto, oposición, PRI. Prácticamente nada.
- **El responsable de la pieza 4 (coraje) es gobierno en solo 33%.** En dos tercios de los
  videos el que queda señalado NO es un órgano de gobierno.
- La institución más nombrada es **INEGI (26 veces)**, que es una fuente de estadística, no un
  actor político. Luego "secretaría de" (13), fiscalía (11), municipio (10).

O sea: el canal **cita** al gobierno mucho más de lo que lo **acusa**. Es institucional y
documental, no partidista. Eso es la pieza 4 funcionando como se diseñó — pide "alguien con
nombre o institución responsable", y el responsable de una contradicción local casi siempre es
una institución. **No es deriva, es la fórmula.**

### Por fórmula

| Fórmula | n | solo gobierno | responsable=gob | partidista |
|---|---|---|---|---|
| comparativa | 9 | 67% | 0% | 0% |
| contradicción local | 24 | 42% | **67%** | 4% |
| polémica | 22 | 41% | 9% | 5% |
| viral | 36 | 61% | 33% | 8% |

Contradicción local es la que de verdad señala al gobierno (67%). Las otras tres lo usan como
fuente.

## 2. ¿TikTok castiga el contenido político? No, según su propia lista

Esto es lo que cambia la conclusión. La lista oficial de lo **no elegible para "Para ti"** es:

- contenido de menores de 16 años
- contenido sexualmente sugestivo
- contenido impactante o gráfico
- **contenido no original**
- **contenido de baja calidad** (clips muy cortos, videos solo de GIF)
- marketing sin declarar
- cierto contenido en LIVE

**El contenido político no está en la lista.** Lo que sí está restringido es la **pauta política
pagada** (ni partidos ni candidatos pueden pagar promoción, aunque sí publicar orgánico), y
etiquetas de advertencia en contenido no verificado. Nada de eso aplica a lo que haces: no
pagas promoción y todo lleva evidencia atribuida.

Así que como **mecanismo de castigo**, lo político no se sostiene.

## 3. Lo que sí está en la lista: "contenido no original"

Y aquí es donde tu instinto apunta a algo real aunque la etiqueta sea otra. Ya lo habíamos
medido sin saber que estaba en la lista de TikTok:

```
esqueletos distintos en 91 videos:  1       (p00→p08 siempre)
p01 abre igual:                    75%
p08 abre igual:                   100%
misma voz, mismo ritmo, misma duración:  siempre
```

**"Contenido no original" y "baja calidad" sí causan no-elegibilidad**, y una plantilla
ejecutada 91 veces es exactamente la forma que un clasificador automático lee así. Eso es mucho
más probable como causa de la caída que lo político. El cambio del p01 que acabamos de aplicar
pega justo ahí — no era solo cosmético.

## 4. Lo que sí te cuesta por ser institucional (sin ser castigo)

Separado de la política de TikTok, 86% de actor gubernamental **define tu público**. Un canal
que siempre habla de Ayuntamiento, Secretaría y fiscalía se lee como canal de política local, y
eso autoselecciona una audiencia más chica que un canal de datos. No es penalización: es techo
por definición de nicho. Y encima satura: quien ve tres videos seguidos de "la institución no
cumplió" se cansa, por buenos que sean.

Eso sí vale atacarlo, y es tu decisión de contenido, no un bug.

### Cómo se baja sin romper la fórmula

El 10% de "solo privado" ya es la plantilla. La pieza 4 **no exige gobierno** — exige un
responsable con nombre. Responsables privados que cumplen igual: el patrón, la concesionaria,
la constructora, la cadena, el desarrollador, la empresa de transporte.

El candidato de **propinas y el artículo 346** es exactamente eso: el señalado es **el patrón**,
no el gobierno, y la contradicción sigue siendo documental y da coraje. Por eso ahora lo subiría
de lugar: no es el más fuerte en cifras, pero es el que rompe la racha institucional.

El de maltrato animal sigue siendo el #1 en fuerza, pero ojo: su número viene de fiscalías y
PAOT, así que cuenta como institucional.

## 5. Lo decisivo, y es gratis

> "Si tu contenido se vuelve no elegible para 'Para ti' o queda restringido de otro modo, esa
> información aparece en la herramienta de analytics de TikTok."

**TikTok te lo dice.** No hay que inferirlo de esta auditoría ni de ninguna otra: si el canal
está restringido, está escrito en tu panel. Es la tercera vez que esta sesión llega al mismo
punto, y ahora con una razón más fuerte que las anteriores — no es para medir mejor, es para
leer un diagnóstico que ya existe.

## Recomendación

1. **Entra a TikTok Studio y busca si hay aviso de restricción o no-elegibilidad.** Contesta en
   dos minutos lo que llevamos horas acotando.
2. **No cambies la fórmula por lo político.** No está castigado y tus videos no son partidistas
   (5%).
3. **Sí baja la saturación institucional** por razón de público, no de algoritmo: mete
   responsables privados. Empieza por propinas/artículo 346.
4. **El cambio del p01 era más importante de lo que parecía**: "no original" sí está en la lista
   de no-elegibles.

## Fuentes

- [For You feed Eligibility Standards (TikTok)](https://www.tiktok.com/community-guidelines/en/fyf-standards/?enter_method=left_navigation)
- [Qué significa "no elegible para recomendación"](https://www.lilachbullock.com/what-does-ineligible-for-recommendation-mean-on-tiktok/)
- [TikTok Creator Academy: video no recomendado](https://www.tiktok.com/creator-academy/article/video-not-recommended)
- [Contenido político y pauta pagada](https://www.diariolibre.com/usa/actualidad/2026/05/06/contenido-politico-tiktok-y-elecciones-estadounidenses/3525274)
- [TikTok prohíbe pauta política (Colombia)](https://es-us.noticias.yahoo.com/tiktok-refuerza-medidas-elecciones-colombia-190000845.html)
