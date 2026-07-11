# Shorts Factory — Plan de Ejecución

**Proyecto:** Shorts Factory
**Documento previo:** 01-SHORTS-FACTORY-Documento-Maestro.md
**Versión:** 1.0
**Fecha:** Julio 2026

---

## Propósito de este documento

Este plan traduce la visión del documento maestro en un camino de ejecución por etapas. Define el orden de construcción, los entregables de cada etapa, los criterios para considerarla terminada, y las dependencias entre ellas. La filosofía es construir el sistema en cortes verticales funcionales: cada etapa deja algo que corre de principio a fin, en lugar de construir todas las capas horizontales antes de ver resultados.

## Principios de ejecución

El proyecto se construye de forma incremental y siempre funcional. Se prioriza tener un flujo end-to-end mínimo lo antes posible, aunque sea con un solo canal y una sola red social, y luego se enriquece. Cada fase se valida con datos reales antes de pasar a la siguiente. La arquitectura hexagonal se respeta desde el primer día, aunque al inicio cada puerto tenga un solo adaptador. No se optimiza prematuramente: primero funciona, después se mejora.

---

## Etapa 0 — Cimientos del proyecto

**Objetivo:** Dejar el esqueleto sobre el que se construye todo lo demás.

**Entregables:**
La estructura de carpetas hexagonal completa (dominio, puertos, adaptadores, infraestructura, CLI). La configuración del gestor de dependencias con Poetry y el archivo `pyproject.toml`. Las migraciones SQL de las seis tablas y el adaptador de repositorio SQLite. Un sistema de configuración por variables de entorno. Un esqueleto de CLI que ya responde a comandos aunque no hagan nada todavía. La configuración base del sistema de logging.

**Criterio de terminación:** El proyecto se instala con un comando, la base de datos se crea con las seis tablas, y el CLI responde a `--help` mostrando los comandos previstos.

**Dependencias:** Ninguna. Es el punto de partida.

---

## Etapa 1 — Scanner (Fase 1 del sistema)

**Objetivo:** Detectar automáticamente videos nuevos en canales registrados.

**Entregables:**
El puerto `VideoSourcePort` y su adaptador basado en yt-dlp. Los casos de uso para registrar un canal, listar canales, y escanear en busca de videos nuevos. La lógica de comparación contra el último video conocido. Los comandos de CLI para gestionar canales y disparar el escaneo. El registro en las tablas `channels` y `videos`.

**Criterio de terminación:** Se puede registrar un canal por CLI, ejecutar el escaneo, y ver en la base de datos los videos detectados. Al correr el escaneo por segunda vez sin videos nuevos, el sistema no duplica registros. Cuando el canal publica algo nuevo, aparece como un registro nuevo con estado `detected`.

**Dependencias:** Etapa 0.

---

## Etapa 2 — Downloader (Fase 2 del sistema)

**Objetivo:** Descargar los videos detectados y organizarlos en disco.

**Entregables:**
La ampliación del puerto de fuente de video para descarga completa. La estrategia multi-API con fallbacks. La creación de la estructura de carpetas por canal y video. El caso de uso de descarga que actualiza el estado del video. El registro en la tabla `downloads` con el método usado y el resultado. El comando de CLI para disparar descargas pendientes.

**Criterio de terminación:** Un video en estado `detected` se descarga a su carpeta correcta, su estado pasa a `downloaded`, y la tabla `downloads` refleja el método que funcionó, el tamaño del archivo, y la marca de tiempo. Si una descarga falla, el error queda registrado y el video no queda en un estado inconsistente.

**Dependencias:** Etapa 1.

---

## Etapa 3 — AI Analyzer (Fase 3 del sistema)

**Objetivo:** Identificar los momentos de reacción y generar los clips verticales.

**Nota:** Esta es la etapa más compleja y de mayor riesgo técnico. Se aborda con sub-etapas y se valida cada capa por separado antes de combinarlas. El plan detallado de esta etapa se refina al llegar a ella, con base en lo aprendido en las etapas previas.

**Sub-etapas:**

*3a — Transcripción.* Integrar faster-whisper como adaptador del puerto `InferenceEngine`. Producir la transcripción con marcas de tiempo de un video descargado. Validar que corre en CPU en tiempos razonables sobre el Ryzen.

*3b — Análisis de audio.* Detectar picos de volumen, risas y gritos con librosa. Producir una serie temporal de intensidad de audio.

*3c — Detección de escenas.* Integrar PySceneDetect para marcar cambios bruscos de plano.

*3d — Puntaje de impacto.* Combinar las tres señales anteriores en un puntaje por segmento y seleccionar los mejores momentos de hasta 60 segundos. Registrar en la tabla `moments`.

*3e — Corte y formato.* El puerto `VideoProcessor` y su adaptador FFmpeg. Cortar los momentos seleccionados y convertirlos a 9:16, aprovechando la aceleración por hardware de la GPU para el encode. Registrar en la tabla `clips`.

**Criterio de terminación:** A partir de un video de reacciones descargado, el sistema produce automáticamente entre uno y varios clips verticales de hasta 60 segundos, correspondientes a los momentos de mayor impacto, con sus registros en `moments` y `clips`.

**Dependencias:** Etapa 2.

---

## Etapa 4 — Publisher (Fase 4 del sistema)

**Objetivo:** Publicar los clips en las redes sociales con una cola priorizada.

**Sub-etapas por plataforma**, en orden de menor a mayor fricción de aprobación:

*4a — Meta (Facebook Reels + Instagram Reels).* El puerto `PublisherPort` y el adaptador de Meta Graph API. Ambas redes comparten aplicación, por lo que se implementan juntas.

*4b — TikTok.* El adaptador de la Content Posting API, contemplando su proceso de auditoría y sus límites de frecuencia.

*4c — X.* El adaptador de la API v2 con carga de video en fragmentos y el modelo de pago por uso.

*4d — Cola priorizada.* El sistema de cola que ordena las publicaciones por plataforma y canal, gestiona reintentos, y registra cada intento en `publish_log`.

**Criterio de terminación:** Un clip generado se publica en las plataformas configuradas siguiendo el orden de prioridad, cada publicación queda registrada en `publish_log` con su URL o su error, y los fallos se reintentan según la política definida.

**Dependencias:** Etapa 3. Las sub-etapas de aprobación de APIs (revisión de Meta, auditoría de TikTok, créditos de X) pueden iniciarse en paralelo desde etapas tempranas, ya que no dependen del código sino de trámites externos.

---

## Etapa 5 — Automatización y orquestación

**Objetivo:** Que el pipeline completo corra desatendido de principio a fin.

**Entregables:**
El scheduler que dispara el escaneo periódico. El encadenamiento automático de las fases: un video detectado se descarga, se analiza y se publica sin intervención manual. El manejo de errores y reintentos a nivel de pipeline. Los comandos de CLI para ver el estado global del sistema.

**Criterio de terminación:** Con el sistema corriendo, cuando un canal registrado publica un video nuevo, el sistema lo detecta, lo descarga, lo analiza, genera los clips, y los publica en las redes configuradas, todo sin intervención, dejando el rastro completo en la base de datos.

**Dependencias:** Etapas 1 a 4.

---

## Etapa 6 — Estadísticas y dashboard (fase futura)

**Objetivo:** Explotar los datos registrados y ofrecer una interfaz visual.

**Entregables:**
Consultas y reportes sobre el rendimiento del pipeline: videos procesados, clips generados, publicaciones por plataforma, tasas de error. La incorporación de métricas de engagement leídas desde las APIs de las redes. El dashboard web como puerto conductor adicional. Eventualmente, la migración a PostgreSQL si el volumen lo justifica.

**Criterio de terminación:** Definido al llegar a esta etapa.

**Dependencias:** Etapa 5 y datos acumulados de operación real.

---

## Secuencia y trámites en paralelo

El desarrollo sigue el orden de las etapas 0 a 5. En paralelo al desarrollo de las etapas tempranas conviene iniciar los trámites externos que tienen tiempos de espera largos: la creación y revisión de la aplicación de Meta, el registro y auditoría de la aplicación de TikTok, y la carga de créditos en X. Adelantar estos trámites evita que la Etapa 4 se bloquee esperando aprobaciones.

## Gestión del riesgo

El mayor riesgo técnico está concentrado en la Etapa 3, por la incertidumbre de qué tan bien la detección automática identifica momentos realmente buenos. Por eso se valida cada capa de señal por separado y se empieza con un nicho acotado (reacciones). El segundo riesgo es la dependencia de servicios externos: las descargas de YouTube pueden verse afectadas por cambios de la plataforma, mitigado con la estrategia multi-API; y las aprobaciones de las redes sociales dependen de terceros, mitigado adelantando los trámites.

Un tercer punto de disciplina, más que de riesgo: las condiciones de las APIs de terceros (límites, precios, endpoints, tiempos de aprobación) cambian con frecuencia. Los números que aparecen en estos documentos se verificaron en julio de 2026, pero antes de implementar cada integración deben reconfirmarse en la documentación oficial vigente. El análisis técnico incluye una sección específica que separa lo confirmado de los supuestos a validar en terreno.
