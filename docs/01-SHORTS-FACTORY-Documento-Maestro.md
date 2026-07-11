# Shorts Factory — Documento Maestro

**Proyecto:** Sistema local de auto-generación y auto-publicación de Reels/Shorts
**Marca:** Construye con IA
**Autor:** Javier Jarquín Chooc
**Versión:** 1.0
**Fecha:** Julio 2026
**Estado:** Fase 0 completada — arquitectura y diseño cerrados

---

## 1. Visión

Shorts Factory es un sistema local (no web/SaaS en su primera etapa) que automatiza el ciclo completo de producción de contenido vertical corto: detecta cuando un canal de YouTube publica un video nuevo, lo descarga, identifica con IA los momentos de mayor impacto, los corta en clips verticales de hasta 60 segundos, y los publica automáticamente en Facebook Reels, Instagram Reels, TikTok y X.

El objetivo es convertir un flujo de trabajo manual y repetitivo —ver un video, elegir los mejores momentos, editarlos en formato vertical, y subirlos uno por uno a cuatro plataformas— en un pipeline desatendido que corre en hardware propio con un costo operativo cercano a un dólar mensual.

## 2. Problema que resuelve

La creación de contenido corto para redes sociales tiene tres fricciones principales:

La primera es la **detección**: hay que estar pendiente de cuándo publica un canal para reaccionar rápido. La segunda es la **edición**: encontrar los momentos buenos dentro de un video largo y recortarlos en formato vertical consume tiempo. La tercera es la **distribución**: subir manualmente el mismo clip a cuatro plataformas distintas, cada una con su interfaz y sus requisitos, multiplica el trabajo.

> **Nota de verificación (julio 2026):** Los datos de plataformas, APIs y precios de este documento fueron verificados contra fuentes actuales. Las condiciones de las APIs de terceros cambian con frecuencia, por lo que deben reconfirmarse en la documentación oficial al momento de implementar cada integración. Ver la sección 8 y el análisis técnico para los puntos que requieren confirmación en el terreno.

Herramientas comerciales como HeyGen resuelven la generación de video pero no incluyen distribución a redes sociales, lo que deja un hueco de mercado. Shorts Factory ataca las tres fricciones en un solo pipeline local y de bajo costo.

## 3. Nicho inicial

El primer nicho de prueba son los **videos de reacciones**. Se eligió porque los momentos de mayor impacto son detectables por señales relativamente claras —picos de volumen, risas, gritos, cambios bruscos de escena— lo que permite validar el motor de detección de la Fase 3 con un caso acotado antes de generalizar a otros tipos de contenido.

## 4. Alcance del sistema (las cuatro fases)

### Fase 1 — Scanner
Monitoreo de canales de YouTube. Se registran canales en una tabla; un proceso programado ejecuta `yt-dlp --flat-playlist` periódicamente, compara el feed actual contra el último video conocido en la base de datos, y detecta automáticamente cuando aparece un video nuevo. Registra el nombre y el identificador del video para no reprocesarlo.

### Fase 2 — Downloader
Descarga del video detectado. Usa una estrategia multi-API con fallbacks: si el método principal falla, intenta con alternativos. El archivo se guarda en una estructura de carpetas organizada por canal y por video, en la ruta `/data/{canal}/{video_id}/raw.mp4`.

### Fase 3 — AI Analyzer
La fase más compleja y el diferenciador del sistema. Un modelo de IA que corre localmente identifica los momentos de reacción del video. Combina tres capas de análisis: transcripción con marcas de tiempo (Whisper), análisis de audio para detectar picos de volumen, risas y gritos, y detección de cambios de escena. Con esas señales genera un puntaje de impacto por segmento, selecciona los mejores momentos de hasta 60 segundos, y usa FFmpeg para cortarlos y convertirlos a formato vertical 9:16.

### Fase 4 — Publisher
Publicación en las redes sociales. Una cola con prioridad configurable por plataforma y por canal va enviando los clips. Publica en Facebook Reels, Instagram Reels y TikTok sin costo por publicación, y en X con un costo aproximado de 0.015 dólares por publicación sin enlace. Cada publicación queda registrada para estadísticas futuras.

Un detalle importante de diseño surge aquí: aunque las apps de Instagram y Facebook ya permiten Reels de varios minutos, sus APIs son más restrictivas y ese es el límite que gobierna al sistema. Por la API de Instagram, solo los videos de entre 5 y 90 segundos en formato 9:16 son elegibles para aparecer en la pestaña Reels; fuera de ese rango se publican como video normal. Por la API de Facebook, los Reels van de 3 a 60 segundos. Por eso el sistema apunta a clips de hasta 60 segundos, que es el denominador común que cumple los límites de API de las cuatro plataformas.

## 5. Decisiones técnicas (Fase 0)

### Lenguaje: Python 3.12+
El cuello de botella real del proyecto es la IA y el procesamiento de video, no el orquestador. Los modelos (Whisper, análisis de audio, detección de escenas) y FFmpeg ya están escritos en C/C++/Rust por debajo; Python solo los coordina. El ecosistema de machine learning es abrumadoramente Python, y la carga de trabajo es en lotes, no de alta concurrencia, por lo que las ventajas de Go o Rust no aplican a este caso. Si en el futuro un módulo específico se vuelve un cuello de botella de CPU puro, la arquitectura hexagonal permite reescribirlo en Rust vía PyO3 sin tocar el resto.

### Cómputo: CPU-first con backend intercambiable
El hardware disponible es una PC con procesador Ryzen 9 5900 (12 núcleos, 24 hilos), una GPU AMD Radeon RX 5500 XT de 8GB (arquitectura RDNA 1), y en ocasiones una laptop solo con CPU. La RX 5500 XT no tiene soporte oficial de ROCm de AMD —solo esfuerzos comunitarios que requieren compilar desde código fuente en Linux— y en Windows el soporte es prácticamente inexistente para esta arquitectura. Por eso el motor de IA se diseña CPU-first usando `faster-whisper` (basado en CTranslate2), que corre en el Ryzen aprovechando sus múltiples hilos. La GPU AMD sí se aprovecha para acelerar el encode de video vía FFmpeg (AMF en Windows), que es independiente de ROCm.

Una expectativa a calibrar con pruebas reales: en CPU, faster-whisper transcribe aproximadamente en tiempo real o algo más rápido según el tamaño del modelo, la cuantización int8 y el número de hilos —no necesariamente los múltiplos de velocidad que se citan para GPU—. Como el sistema procesa en lotes y no en tiempo real, esto es aceptable, pero el tamaño de modelo concreto se elige midiendo en el hardware real durante la Etapa 3. La elección de modelos ligeros (como las variantes destiladas o "turbo") es una palanca disponible si la velocidad en CPU resulta insuficiente. El diseño define una interfaz `InferenceEngine` con adaptadores intercambiables (CPU por defecto, CUDA en reserva por si en el futuro se incorpora una GPU NVIDIA), de modo que el mismo código corre sin cambios en la PC y en la laptop.

### Arquitectura: hexagonal (puertos y adaptadores)
El núcleo de dominio (entidades y casos de uso) es Python puro, sin dependencias de librerías externas. Todo lo externo —la fuente de video, el motor de IA, el procesador de video, los publicadores, la base de datos— se conecta a través de puertos (interfaces abstractas) implementados por adaptadores concretos. Esto permite cambiar cualquier componente externo sin tocar la lógica central: migrar de SQLite a PostgreSQL, agregar una nueva red social, o cambiar la fuente de descarga son operaciones que solo añaden o reemplazan un adaptador.

### Base de datos: SQLite ahora, PostgreSQL después
Se empieza con SQLite por simplicidad —un solo archivo, cero configuración— y se migra a PostgreSQL cuando el volumen o la necesidad de concurrencia lo justifiquen. Gracias a la arquitectura hexagonal, la migración solo requiere escribir un nuevo adaptador de repositorio.

### Interacción: CLI primero
El sistema se opera inicialmente por línea de comandos. El dashboard web queda como fase futura, y la arquitectura ya contempla su conexión como un puerto conductor adicional sin reescribir el núcleo.

## 6. Modelo de datos

El esquema define seis tablas que separan las entidades lógicas (canales, videos, momentos, clips) de los eventos físicos que pueden fallar y reintentarse (descargas, publicaciones):

`channels` — canales monitoreados, con el identificador del último video procesado para detectar novedades.
`videos` — cada video detectado, con un estado que lo hace viajar por el pipeline.
`downloads` — evento de descarga, con el método usado y su resultado.
`moments` — segmentos de reacción detectados por la IA, con puntaje de impacto y motivo.
`clips` — archivos ya cortados en 9:16, listos para publicar.
`publish_log` — registro de cada publicación por plataforma, con prioridad, reintentos y URL resultante.

## 7. Presupuesto operativo

Las herramientas base son gratuitas y de código abierto: Python, yt-dlp y FFmpeg. Las APIs de publicación de Facebook Reels, Instagram Reels y TikTok no cobran por publicación. Solo X cobra bajo un modelo de pago por uso, que desde febrero de 2026 es el esquema por defecto para desarrolladores nuevos: aproximadamente 0.015 dólares por publicación sin enlace y 0.20 dólares si la publicación contiene un enlace. Conviene, por tanto, evitar poner enlaces en el texto de las publicaciones de X para mantener el costo bajo.

Para un uso estimado de un video semanal cortado en cuatro clips y publicado en las cuatro redes —unas 64 publicaciones al mes— el costo total mensual ronda un dólar estadounidense, atribuible casi por completo a X. Si el sistema corre en la máquina local no hay costo de servidor.

Una advertencia para la fase futura de estadísticas: leer métricas de engagement desde la API de X también cuesta (alrededor de 0.005 dólares por lectura) y tiene un tope mensual, por lo que esa funcionalidad, cuando se implemente, debe presupuestarse aparte y probablemente convenga usar fuentes alternativas más baratas para lectura de datos. Publicar y leer son costos separados.

## 8. Restricciones y consideraciones

El proceso de aprobación de las APIs no es inmediato: la revisión de aplicaciones de Meta puede tardar días o semanas, y la auditoría de TikTok entre una y dos semanas; sin aprobación, las publicaciones de TikTok quedan en modo privado. X requiere cargar créditos por anticipado. TikTok es la plataforma más restrictiva por su proceso de auditoría manual, sus tokens de corta duración y sus límites de frecuencia. Facebook e Instagram comparten el ecosistema Meta, por lo que se autentican con una sola aplicación.

## 9. Próximos pasos

Con la Fase 0 cerrada, el siguiente paso es el arranque de la implementación: crear el esqueleto del proyecto con la estructura de carpetas hexagonal, configurar el gestor de dependencias, definir las migraciones de las seis tablas, e implementar la Fase 1 (scanner) como primer módulo funcional end-to-end.
