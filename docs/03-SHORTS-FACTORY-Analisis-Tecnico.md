# Shorts Factory — Análisis Técnico Detallado

**Proyecto:** Shorts Factory
**Documentos previos:** 01-Documento-Maestro, 02-Plan-de-Ejecucion
**Versión:** 1.0
**Fecha:** Julio 2026

---

## Propósito de este documento

Este análisis baja del plan de ejecución al detalle de implementación: la estructura de código, los contratos de cada puerto, las tecnologías concretas de cada adaptador, el esquema de datos con sus columnas y tipos, la máquina de estados que gobierna el pipeline, y las consideraciones específicas de cada plataforma. Es el documento de referencia para escribir el código.

---

## 1. Arquitectura de código

### 1.1 Estructura de carpetas

El proyecto sigue la separación hexagonal en cuatro capas: dominio, puertos, adaptadores e infraestructura, con la CLI como capa de entrada.

```
shorts_factory/
├── pyproject.toml
├── README.md
├── .env.example
├── data/                          # Videos y clips (fuera de git)
│   └── {canal}/{video_id}/
│       ├── raw.mp4
│       └── clips/
├── migrations/                    # SQL de creación de tablas
├── src/shorts_factory/
│   ├── domain/                    # NÚCLEO — Python puro
│   │   ├── entities/              # channel, video, download, moment, clip, publication
│   │   └── use_cases/            # un módulo por caso de uso
│   ├── ports/                     # Interfaces (ABC)
│   │   ├── video_source.py
│   │   ├── inference_engine.py
│   │   ├── video_processor.py
│   │   ├── publisher.py
│   │   └── repository.py
│   ├── adapters/                  # Implementaciones concretas
│   │   ├── video_source/ytdlp_adapter.py
│   │   ├── inference/cpu_whisper_adapter.py
│   │   ├── inference/audio_analyzer.py
│   │   ├── inference/scene_detector.py
│   │   ├── processing/ffmpeg_adapter.py
│   │   ├── publishers/meta_adapter.py
│   │   ├── publishers/tiktok_adapter.py
│   │   ├── publishers/x_adapter.py
│   │   └── repository/sqlite_adapter.py
│   ├── infrastructure/            # Config, DI, scheduler, logging
│   └── cli/                        # Entrada por línea de comandos
└── tests/
```

### 1.2 Regla de dependencias

El dominio no importa nada de las capas externas. Los puertos son importados por el dominio (que define o consume las interfaces) y son implementados por los adaptadores. Los adaptadores importan librerías externas (yt-dlp, faster-whisper, requests) pero el dominio nunca las ve. La infraestructura arma el grafo de dependencias en tiempo de arranque, inyectando los adaptadores concretos a los casos de uso. Esta dirección de dependencias —siempre hacia el núcleo— es lo que permite sustituir un adaptador sin tocar la lógica de negocio.

### 1.3 Inyección de dependencias

Un contenedor simple en la capa de infraestructura instancia los adaptadores según la configuración y los provee a los casos de uso. Al inicio no se requiere un framework de inyección; basta una función de composición que lea la configuración y construya los objetos. Esto mantiene el arranque explícito y fácil de seguir.

---

## 2. Contratos de los puertos

Cada puerto es una interfaz abstracta que define qué se puede hacer, sin decir cómo. Los adaptadores implementan el cómo.

### 2.1 VideoSourcePort
Responsable de hablar con la fuente de videos. Define operaciones para listar los videos recientes de un canal (sin descargarlos, solo metadatos) y para descargar un video concreto a una ruta dada. El adaptador inicial usa yt-dlp; el contrato permite agregar fuentes alternativas para la estrategia multi-API.

### 2.2 InferenceEngine
Responsable del análisis de IA. Define la operación de transcribir un audio o video en segmentos con marcas de tiempo. El adaptador por defecto usa faster-whisper en CPU. El contrato está pensado para admitir un adaptador CUDA en el futuro sin cambiar quien lo consume. Las capas de análisis de audio y detección de escenas se modelan como servicios de análisis complementarios que alimentan el puntaje de impacto.

### 2.3 VideoProcessor
Responsable de manipular archivos de video. Define operaciones para cortar un segmento por marcas de tiempo y para convertir a formato vertical 9:16. El adaptador usa FFmpeg por CLI, con opción de aceleración por hardware en el encode.

### 2.4 PublisherPort
Responsable de publicar un clip en una red social. Define una operación de publicación que recibe el clip y sus metadatos y devuelve el resultado (URL o error). Cada red social es un adaptador distinto que implementa este mismo contrato, lo que permite tratar las cuatro plataformas de forma uniforme en la cola de publicación.

### 2.5 RepositoryPort
Responsable de la persistencia. Define las operaciones de lectura y escritura sobre las entidades. El adaptador inicial usa SQLite; el contrato permite migrar a PostgreSQL implementando un nuevo adaptador sin tocar los casos de uso.

---

## 3. Tecnologías por adaptador

### 3.1 Descarga — yt-dlp
Para el escaneo se usa el modo de listado plano (`--flat-playlist`), que devuelve los identificadores y títulos de los videos de un canal sin descargar contenido, lo que lo hace rápido y barato para correr periódicamente. Para la descarga se usa yt-dlp en modo completo. Se contempla que YouTube ha endurecido sus mecanismos, por lo que la estrategia multi-API prevé fallbacks y el uso de cookies de un navegador autenticado cuando sea necesario.

### 3.2 Transcripción — faster-whisper
Se elige faster-whisper (implementación sobre CTranslate2) en lugar de Whisper de referencia porque es más rápido y funciona en CPU con múltiples hilos y cuantización int8, aprovechando el Ryzen 9 5900. Produce segmentos con marcas de tiempo de inicio y fin, que son la base para localizar los momentos y para cortar con precisión.

Sobre el rendimiento en CPU conviene tener expectativas calibradas: faster-whisper en CPU suele transcribir en torno a tiempo real o algo más rápido, dependiendo del tamaño del modelo, la cuantización y el número de hilos —los múltiplos de velocidad más altos que a veces se citan corresponden a ejecución en GPU NVIDIA—. Dado que el sistema procesa en lotes y no en tiempo real, esto es aceptable. El tamaño del modelo se elige balanceando precisión y velocidad con pruebas en el hardware real durante la implementación de esta fase. Existen variantes ligeras (modelos destilados y "turbo") que sirven como palanca si la velocidad en CPU resulta insuficiente. Nota: el Ryzen 9 5900 no cuenta con NPU; la aceleración por NPU para Whisper que AMD ofrece aplica solo a procesadores Ryzen AI recientes, por lo que no es una opción en este hardware.

### 3.3 Análisis de audio — librosa
Se analiza la pista de audio para extraer una señal de intensidad a lo largo del tiempo: energía, picos de volumen, y patrones asociados a risas o gritos. Esta señal es puramente de CPU y complementa la transcripción para detectar momentos que el texto por sí solo no revela (una reacción puede ser un grito sin palabras).

### 3.4 Detección de escenas — PySceneDetect
Marca los cambios bruscos de plano, que suelen coincidir con momentos de énfasis en videos de reacción (cortes rápidos, zooms). Aporta una tercera señal al puntaje de impacto.

### 3.5 Procesamiento de video — FFmpeg
Corta los segmentos seleccionados por marcas de tiempo y los convierte a 9:16. La conversión a vertical puede hacerse con recorte centrado o con fondo desenfocado según el contenido. Para el encode se aprovecha la aceleración por hardware de la GPU AMD (AMF en Windows), que es independiente de ROCm y sí funciona con la RX 5500 XT, acelerando la parte de transcodificación sin depender del stack de machine learning de AMD.

### 3.6 Publicación — APIs de cada red
Meta Graph API cubre Facebook Reels e Instagram Reels con una sola aplicación. TikTok usa la Content Posting API. X usa la API v2 con carga de video en fragmentos. Cada una se encapsula en su adaptador para aislar sus particularidades.

---

## 4. Esquema de datos detallado

El diseño separa entidades lógicas de eventos físicos. Un video, un momento y un clip son cosas que existen; una descarga y una publicación son acciones que pueden fallar, reintentarse y tener su propio historial. Por eso las descargas y las publicaciones viven en tablas propias con estado, mensaje de error y contador de reintentos.

### 4.1 channels
Los canales monitoreados. Campos: identificador interno, identificador del canal en YouTube, nombre, nicho, identificador del último video procesado (clave para detectar novedades), indicador de activo, y marca de creación.

### 4.2 videos
Cada video detectado. Campos: identificador interno, referencia al canal, identificador del video en YouTube, título, duración en segundos, fecha de publicación en YouTube, estado dentro del pipeline, y marca de cuándo lo detectó el scanner. La separación entre fecha de publicación y fecha de detección permite medir cuánto tarda el sistema en reaccionar.

### 4.3 downloads
El evento de descarga. Campos: identificador interno, referencia al video, ruta del archivo, tamaño en bytes, método o fuente que funcionó, estado, mensaje de error si lo hubo, y marca de finalización. El campo de método es valioso para evaluar qué fuentes de la estrategia multi-API son más confiables.

### 4.4 moments
Los segmentos de reacción detectados por la IA. Campos: identificador interno, referencia al video, segundo de inicio, segundo de fin, puntaje de impacto, motivo de la detección (pico de audio, risa, cambio de escena, o combinación), y marca de creación. Esta tabla es la memoria del sistema sobre qué consideró interesante y por qué.

### 4.5 clips
Los archivos ya cortados en formato vertical. Campos: identificador interno, referencia al momento del que provienen, ruta del archivo, duración, formato, estado, y marca de creación.

### 4.6 publish_log
El registro de cada publicación por plataforma. Campos: identificador interno, referencia al clip, plataforma, estado, URL de la publicación resultante, prioridad en la cola, contador de reintentos, mensaje de error, y marca de publicación. Un clip genera varias filas aquí, una por cada red social a la que se envía.

### 4.7 Lo que deliberadamente no se incluye todavía
No se modelan aún las métricas de engagement (vistas, me gusta), que llegarán como una tabla nueva colgada de las publicaciones cuando se integren las APIs de lectura. No hay tabla de usuarios porque el sistema es de un solo operador. La configuración de plataformas vive en archivos de configuración, no en la base de datos. Estas omisiones son intencionales para no cargar el esquema con estructuras vacías; la arquitectura permite agregarlas sin fricción cuando hagan falta.

---

## 5. Máquina de estados del pipeline

El estado del campo correspondiente en la tabla de videos gobierna el avance por el pipeline. Un video recién detectado entra como `detected`. Al iniciar su descarga pasa a `downloading`, y al completarla a `downloaded`. Cuando comienza el análisis pasa a `analyzing`, y al terminar a `analyzed`. Una vez generados y encolados los clips, y publicados, el video se marca como `done`. Cualquier fallo lleva a un estado de error del que se puede reintentar sin dejar el registro inconsistente.

Los estados de las descargas, los clips y las publicaciones se gestionan de forma análoga en sus propias tablas, de modo que un fallo en una publicación a una red no bloquea las demás ni obliga a reprocesar el video completo.

---

## 6. Estrategia de la cola de publicación

La cola ordena las publicaciones pendientes por prioridad, configurable por plataforma y por canal, de modo que se puede decidir, por ejemplo, publicar primero en TikTok e Instagram y después en Facebook y X. Cada intento de publicación se registra en la tabla de publicaciones. Los fallos se reintentan según una política con límite de reintentos y espera creciente entre intentos. La cola respeta los límites de frecuencia de cada plataforma para no exceder sus cuotas.

---

## 7. Consideraciones por plataforma

### 7.1 Meta (Facebook Reels e Instagram Reels)
Ambas redes se manejan con la Graph API bajo una sola aplicación de Meta. Aquí hay una distinción crítica entre lo que permiten las apps y lo que permiten las APIs: aunque las aplicaciones móviles de Instagram y Facebook ya admiten Reels de varios minutos, las APIs son más restrictivas y son ellas las que gobiernan al sistema.

Por la API de Facebook (endpoint de video reels, con flujo de tres pasos: iniciar, subir, publicar), los Reels van de 3 a 60 segundos en formato vertical 9:16. Por la API de Instagram, técnicamente se aceptan videos más largos, pero solo los de entre 5 y 90 segundos con relación 9:16 son elegibles para aparecer en la pestaña Reels; fuera de ese rango se publican como video normal. Algunas cuentas todavía ven un tope de 60 segundos según su historial. Instagram limita a 100 publicaciones por API en una ventana móvil de 24 horas. Ambas requieren cuentas de tipo empresa o creador vinculadas a una página de Facebook. El proceso de revisión de la aplicación de Meta puede tardar días o semanas y conviene iniciarlo con anticipación.

La consecuencia de diseño es que apuntar a clips de hasta 60 segundos satisface simultáneamente los límites de API de las cuatro plataformas, por lo que se adopta como objetivo de corte.

### 7.2 TikTok
Usa la Content Posting API, la más restrictiva de las cuatro. La carga es en fragmentos, no hay programación nativa, los tokens de acceso caducan rápido, y la aplicación pasa por una auditoría manual que toma de una a dos semanas; sin ella, las publicaciones quedan privadas. Los límites de frecuencia son estrictos. Todo esto se encapsula en su adaptador para que el resto del sistema no se contamine con estas particularidades.

### 7.3 X
Usa la API v2. La carga de video es en fragmentos, con una secuencia de inicio, envío de partes, finalización, verificación de estado y creación de la publicación. El modelo es de pago por uso, que desde febrero de 2026 es el esquema por defecto para desarrolladores nuevos: se cargan créditos por anticipado y se descuentan por operación. Publicar cuesta alrededor de 0.015 dólares por publicación sin enlace, pero sube a unos 0.20 dólares si la publicación contiene un enlace —una diferencia de más de diez veces por el mismo acto—, por lo que el adaptador debe evitar incluir enlaces en el texto. No hay nivel gratuito para desarrolladores nuevos; los planes fijos anteriores (Basic y Pro) quedaron cerrados a nuevas altas. Leer datos (para métricas futuras) se cobra aparte, alrededor de 0.005 dólares por lectura, con un tope mensual de dos millones de lecturas. Como los precios de X han cambiado varias veces en pocos meses, el adaptador y el presupuesto deben reconfirmarse contra la consola de desarrollador vigente al implementar.

Existe la librería Python XDK (SDK oficial de X) y Tweepy como alternativa comunitaria; la elección concreta se decide al implementar el adaptador.

---

## 8. Cómputo y rendimiento

El diseño CPU-first responde a la realidad del hardware: la GPU AMD RX 5500 XT (RDNA 1) no tiene soporte oficial de ROCm y en Windows es prácticamente inviable para machine learning, por lo que forzarla sería una pelea de días con drivers y compilaciones para un resultado inestable. El Ryzen 9 5900, con doce núcleos y veinticuatro hilos, mueve bien faster-whisper y el análisis de audio, que son las cargas de IA del sistema. La GPU sí se aprovecha donde es competente: el encode de video con FFmpeg vía AMF, que no depende de ROCm.

La interfaz `InferenceEngine` con adaptadores intercambiables permite que el mismo código corra en la laptop (solo CPU) y en la PC sin cambios, y deja lista la puerta para un adaptador CUDA si en el futuro se incorpora una GPU NVIDIA, que sí tendría soporte maduro. El trabajo se procesa en lotes, no en tiempo real, por lo que la latencia de la CPU es aceptable para el caso de uso.

---

## 9. Riesgos técnicos y mitigaciones

El riesgo principal es la calidad de la detección de momentos en la Fase 3: no hay garantía de que el puntaje automático coincida con lo que un humano consideraría un buen momento. Se mitiga validando cada señal por separado, empezando con un nicho acotado de reacciones donde las señales son claras, y ajustando el puntaje con base en resultados reales.

El segundo riesgo es la fragilidad de la descarga desde YouTube ante cambios de la plataforma, mitigado con la estrategia multi-API con fallbacks.

El tercer riesgo son los tiempos y condiciones de aprobación de las APIs de las redes sociales, que dependen de terceros; se mitiga adelantando los trámites en paralelo al desarrollo.

Un cuarto riesgo es el soporte de hardware para IA en AMD, ya resuelto por diseño con el enfoque CPU-first.

---

## 10. Supuestos y puntos a verificar en terreno

Este apartado separa lo confirmado de lo que son supuestos de planeación, para no construir sobre certezas falsas. Los datos de plataformas y precios de este documento fueron verificados contra fuentes públicas actuales (julio de 2026), pero las condiciones de servicios de terceros cambian con frecuencia y deben reconfirmarse en la documentación oficial al implementar cada pieza.

**Confirmado y estable a la fecha:** los límites de duración de las APIs de Facebook Reels (3 a 60 segundos) e Instagram Reels (5 a 90 segundos elegibles para la pestaña Reels); el límite de 100 publicaciones diarias por API en Instagram; el requisito de cuentas empresa/creador en Meta; el modelo de pago por uso de X con su costo por publicación y el recargo por enlaces; la ausencia de nivel gratuito en X para desarrolladores nuevos; la falta de soporte oficial de ROCm para la RX 5500 XT; y la idoneidad de faster-whisper en CPU.

**Supuestos de planeación que deben validarse al ejecutar:**

El rendimiento real de faster-whisper en el Ryzen 9 5900 se debe medir para elegir tamaño de modelo; la cifra exacta de velocidad depende del hardware y la configuración.

La calidad de la detección de momentos de reacción es una hipótesis a validar con material real; no hay garantía previa de que las señales elegidas (audio, escena, transcripción) capturen lo que un humano consideraría un buen momento.

La viabilidad y estabilidad de la descarga desde YouTube con yt-dlp está sujeta a los cambios que la plataforma introduce periódicamente; la estrategia multi-API es precisamente la mitigación de este supuesto.

Los tiempos exactos de aprobación de las APIs (revisión de Meta, auditoría de TikTok) son estimaciones basadas en experiencias reportadas, no compromisos de las plataformas.

Los detalles finos de cada API (nombres exactos de endpoints, versiones, permisos requeridos, formatos aceptados) deben tomarse de la documentación oficial vigente al momento de escribir cada adaptador, no de este documento, que captura el panorama general y no reemplaza la referencia oficial.

Los precios de X en particular han cambiado varias veces en 2026, por lo que deben reconfirmarse en la consola de desarrollador antes de presupuestar en firme.

## 11. Lo que sigue

Con este análisis, el siguiente paso concreto es implementar la Etapa 0 del plan: crear la estructura de carpetas, configurar Poetry, escribir las migraciones de las seis tablas y el adaptador SQLite, y montar el esqueleto de la CLI. A partir de ahí se construye la Fase 1 (scanner) como primer flujo funcional end-to-end.
