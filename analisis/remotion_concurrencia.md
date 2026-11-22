# Concurrencia de Remotion (22/11/2026)

**Pregunta**: ¿cuántas pestañas en paralelo (`Config.setConcurrency`) le convienen al render en esta PC (24 hilos)? La documentación de Remotion avisa que tanto de más como de menos frenan el render, y que hay que medirlo.

**Cómo se midió**: `tools/benchmark_remotion.py`, con la fábrica sin renderizar ni generar voz. Se usaron los mismos cuadros de dos videos reales:
- **plus**: el render de Dato Mata Gato (`poc_remotion`, `CapituloPlus`), con `guion-viral-fumigacion-mariposas-monterrey`.
- **3d**: el render de tradiciones y papasia (`tradiciones_3d`, `Tradicion`), con `guion-tradicion-corona-navidena`.

Los datos crudos están en `remotion_concurrencia/ronda1.csv`, `ronda2.csv` y `completo.csv`.

## Resultados

Los primeros 600 cuadros (20 s de video), en segundos (menos es mejor):

| concurrencia | plus r1 | plus r2 | 3d r1 | 3d r2 |
|---|---|---|---|---|
| default (8) | 54 | 54 | 21 | 20 |
| 2 | | 43 | | 34 |
| 3 | | **39** | | 29 |
| 4 | **40** | **40** | 25 | 26 |
| 6 | | 46 | | 22 |
| 8 | 53 | 54 | 20 | **20** |
| 12 | 71 | | **19** | |
| 16 | 89 | | 27 | |
| 24 | 124 | | **19** | |

El video completo (58 s, 1740 cuadros):

| render | default (8) | 4 |
|---|---|---|
| plus | 83 s | **76 s** (−8 %) |
| 3d | **47 s** | 64 s (+36 %) |

## Decisión

- **plus: 4**, fijo en `poc_remotion/remotion.config.ts`. Siempre fue igual o mejor que el default. Subir de 8 lo hace mucho más lento: con 24 tarda 2.3 veces más. La ganancia en un video completo es chica (~7 s).
- **3d: el default**. Con menos de 8 empeora y con más no mejora. El cambio en `tradiciones_3d/remotion.config.ts` solo deja la variable para volver a medir.
- **Conclusión**: el render no es el cuello de botella. Un video completo tarda 47–83 s, contra ~45 min de voz por video. Lo que acorta un lote es la voz (ver `prueba_num_step/`).

`REMOTION_CONCURRENCY=<n>` cambia el valor en los dos sin tocar código.
