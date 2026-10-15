# CLAUDE.md

Mapa del sistema de **Dato Mata Gato** (canal de TikTok/Facebook de Javier), para no tener que explorar. Actualizado el 15/10/2026. Responde siempre en español.

## Dónde está cada cosa

| Repo | Qué hace |
|---|---|
| `C:\dato-mata-gato-bot` | Bot de Telegram y orquestación: `pipeline.py` (genera un video de punta a punta), `fabrica.py` (lotes automáticos), `instruccion_cercania.py` (la fórmula), `evidencia.py` (evidencia real), `herramientas_guion.py` (fotos y revisión del guion), `claude_runner.py` (sesiones de Claude) |
| `C:\illustrated-narrator` | Arma el video desde el guion (`narrator generate`); `poc_remotion/` es el render final con Remotion (animaciones, notas animadas, portada). Su `CLAUDE.md` tiene las reglas del narrador |
| `C:\tts-kokoro` | Voz: motor VoiceStudio (Docker `voicestudio`, puerto 3900) |
| `C:\clip_assistance` (aquí) | Scripts de apoyo en `tools/` (correr y medir lotes, pruebas de voz), análisis en `analisis/`, y la app shorts-factory (`src/`) |
| `C:\Android_in` | Entrada y salida: `<slug>\guion.json`, `fabrica\<lote>\estado.json`, `lotes\<lote>\` (videos archivados con su portada) |

## Cómo se produce hoy

- **Fábrica automática desde Telegram**: `/lotegrande 20 dia [tema]` o `/lotegrande 20 0-9 [tema]`; `/fabrica` (estado) y `/pararfabrica`. La tarea de Windows "DatoMataGato Fabrica" la retoma cada 15 min y sobrevive al límite de Claude. Escribe ~6 guiones por ventana de 5 h (lo que alcanza a generarse: ~45 min por video).
- **Fórmula** ("la contradicción local"): te afecta + está pasando + algo no cuadra + coraje + se puede mostrar + **hace hablar**; dos preguntas directas a quien ve (antes del segundo 10 y a la mitad); mezcla 3 temas actuales : 2 perennes; que envejezca bien. Todo en `instruccion_cercania.py`.
- **Voz solo Fish 3**. **Evidencia real, sin IA.** Render Remotion con portada estilo A ("la nota"). Lotes y fábrica se **archivan local, sin Drive**; Javier publica a mano.

## Reglas de trabajo

- **Nunca push directo a `main`**: rama + PR. Hay PRs abiertos en los tres repos.
- Artefactos de prueba dentro del proyecto (`analisis/`), nunca en el scratchpad.
- Un cambio al pipeline se verifica con una corrida real, no solo con tests (`C:\dato-mata-gato-bot\.venv\Scripts\python.exe -m pytest -q`).
- Verificar cada dato antes de que entre a un guion. No evadir la detección de IA de TikTok. No apagar la PC.
- **Tokens**: la cuota de Claude es una sola para la fábrica y estas conversaciones. Una conversación larga relee todo su historial en cada paso (el 14/10 una llegó a ~500 mil por paso y gastó el 94% del día): **abre una conversación nueva al cambiar de tema**. Medir con `tools/medir_cuota_claude.py` y `tools/perfil_pasos_guion.py`.
