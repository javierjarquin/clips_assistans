# Shorts Factory

Sistema local de auto-generación y auto-publicación de Reels/Shorts. Detecta videos nuevos en canales de YouTube, los descarga, identifica con IA los momentos de mayor impacto, los corta en clips verticales 9:16 de hasta 60 segundos, y los publica en Facebook Reels, Instagram Reels, TikTok y X.

Documentación de diseño (carpeta [docs/](docs/)):

- `01-SHORTS-FACTORY-Documento-Maestro.md` — visión, alcance y decisiones técnicas
- `02-SHORTS-FACTORY-Plan-de-Ejecucion.md` — etapas y criterios de terminación
- `03-SHORTS-FACTORY-Analisis-Tecnico.md` — referencia de implementación

## Requisitos

- Python 3.12 o 3.13 (3.14 aún sin wheels de numba/ctranslate2)
- [Poetry](https://python-poetry.org/)
- FFmpeg (si no está en PATH se busca la instalación de winget automáticamente)

## Instalación

```bash
poetry install
```

## Uso

### Interfaz gráfica (recomendada)

Doble clic en **`Iniciar Shorts Factory.cmd`** (raíz del proyecto), o:

```bash
poetry run shorts-factory-gui
# o bien
poetry run shorts-factory gui
```

Ventana con: registro de canales, botones por fase del pipeline (escanear,
descargar, analizar, publicar, ciclo completo), contadores de videos por fase
en vivo, barra de actividad y log con el detalle de cada paso. La base de
datos se crea sola al abrir.

El botón **⚙ Configuración** abre el panel para capturar las llaves de las
APIs (Meta, TikTok, X), elegir plataformas habilitadas y ajustar parámetros
de análisis — se guardan en el `.env` del proyecto, sin editar nada a mano.

### Línea de comandos

```bash
# Crear la base de datos (seis tablas)
poetry run shorts-factory init

# Registrar un canal y escanear
poetry run shorts-factory channel add "@nombre" --name "Mi Canal" --niche reacciones
poetry run shorts-factory scan

# Fases individuales
poetry run shorts-factory download   # detected  -> downloaded
poetry run shorts-factory analyze    # downloaded -> analyzed (+ moments y clips)
poetry run shorts-factory publish    # clips ready -> redes (requiere SF_PLATFORMS)

# Pipeline completo desatendido (un ciclo cada N minutos)
poetry run shorts-factory run
poetry run shorts-factory run --once   # un solo ciclo

# Estado global
poetry run shorts-factory status
```

Configuración: copiar `.env.example` a `.env` y ajustar. Publicación requiere
credenciales por plataforma (app de Meta, auditoría de TikTok, créditos de X) —
ver documentos de diseño, sección de trámites.

Notas de comportamiento:
- El primer escaneo de un canal solo fija la línea base (no procesa videos viejos).
- El encoder de video se detecta probando nvenc/amf/qsv y cae a libx264 (CPU).
- El adaptador de X elimina enlaces del texto (con enlace cuesta ~13x más).

## Estructura (arquitectura hexagonal)

```
src/shorts_factory/
├── domain/           # Núcleo: entidades y casos de uso (Python puro)
├── ports/            # Interfaces abstractas (ABC)
├── adapters/         # Implementaciones: yt-dlp, whisper, ffmpeg, APIs, SQLite
├── infrastructure/   # Config, BD, logging, composición de dependencias
├── cli/              # Entrada por línea de comandos
└── gui/              # Interfaz gráfica de escritorio (CustomTkinter)
```

Regla de dependencias: todo apunta hacia el dominio. El dominio no importa nada externo; los adaptadores implementan los puertos; la infraestructura arma el grafo al arrancar.

## Tests

```bash
poetry run pytest
```

## Estado del proyecto

- [x] Etapa 0 — Cimientos (estructura, BD, CLI)
- [x] Etapa 1 — Scanner (validación live pendiente: red con YouTube accesible)
- [x] Etapa 2 — Downloader (multi-fallback; validación live pendiente, misma razón)
- [x] Etapa 3 — AI Analyzer (validado end-to-end con video sintético)
- [x] Etapa 4 — Publisher (código y cola listos; publicación real pendiente de credenciales)
- [x] Etapa 5 — Automatización (`run` desatendido con ciclos y resiliencia por fase)
- [ ] Etapa 6 — Estadísticas y dashboard (fase futura)

Pendientes que no dependen del código: probar scan/download en una red sin
bloqueo de YouTube; crear app de Meta, pasar auditoría de TikTok y cargar
créditos de X; calibrar el puntaje de impacto con videos de reacciones reales.
