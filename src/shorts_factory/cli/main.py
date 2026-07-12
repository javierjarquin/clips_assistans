"""CLI de Shorts Factory.

Etapa 0: `init` y `status` funcionan; el resto son esqueletos que se
implementan en su etapa correspondiente del plan de ejecución.
"""

import sys

import typer

from shorts_factory.infrastructure.config import load_settings
from shorts_factory.infrastructure.container import Container
from shorts_factory.infrastructure.database import list_tables
from shorts_factory.infrastructure.logging_config import setup_logging

# Windows abre stdout/stderr con la codepage cp1252 por defecto: los títulos de
# video con emoji (frecuentes en YouTube) rompen typer.echo con UnicodeEncodeError.
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

app = typer.Typer(
    help="Shorts Factory — pipeline local de generación y publicación de Shorts/Reels.",
    no_args_is_help=True,
)
channel_app = typer.Typer(help="Gestión de canales monitoreados.", no_args_is_help=True)
app.add_typer(channel_app, name="channel")
media_app = typer.Typer(help="Gestión de archivos locales (videos y clips en disco).", no_args_is_help=True)
app.add_typer(media_app, name="media")


def _container() -> Container:
    settings = load_settings()
    setup_logging(settings.log_level, settings.log_file)
    return Container(settings)


def _pending(stage: str) -> None:
    typer.echo(f"Aún no implementado — llega en la {stage} del plan de ejecución.")


@app.command()
def init() -> None:
    """Crea la base de datos y aplica las migraciones."""
    container = _container()
    applied = container.init_db()
    if applied:
        typer.echo(f"Migraciones aplicadas: {', '.join(applied)}")
    else:
        typer.echo("Base de datos ya al día, sin migraciones pendientes.")
    tables = list_tables(container.connection)
    typer.echo(f"Tablas ({len(tables)}): {', '.join(tables)}")


@app.command()
def status() -> None:
    """Muestra el estado global: totales, videos por fase y cola de publicación."""
    container = _container()
    conn = container.connection
    tables = list_tables(conn)
    if not tables:
        typer.echo("Base de datos vacía. Ejecuta primero: shorts-factory init")
        raise typer.Exit(code=1)
    for table in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        typer.echo(f"{table}: {count}")

    videos_by_status = conn.execute(
        "SELECT status, COUNT(*) FROM videos GROUP BY status ORDER BY status"
    ).fetchall()
    if videos_by_status:
        typer.echo("\nVideos por fase:")
        for row in videos_by_status:
            typer.echo(f"  {row[0]}: {row[1]}")

    queue = conn.execute(
        "SELECT platform, status, COUNT(*) FROM publish_log"
        " GROUP BY platform, status ORDER BY platform"
    ).fetchall()
    if queue:
        typer.echo("\nCola de publicación:")
        for row in queue:
            typer.echo(f"  {row[0]} {row[1]}: {row[2]}")


@channel_app.command("add")
def channel_add(
    youtube_channel_id: str = typer.Argument(help="ID (UC...), handle (@nombre) o URL del canal"),
    name: str = typer.Option(..., "--name", "-n", help="Nombre del canal"),
    niche: str = typer.Option(None, "--niche", help="Nicho del canal (p. ej. reacciones)"),
    include_latest: bool = typer.Option(
        False, "--include-latest",
        help="Encola ya el video más reciente para descargar, sin esperar a que el canal publique algo nuevo.",
    ),
) -> None:
    """Registra un canal para monitorear."""
    from shorts_factory.domain.use_cases.register_channel import ChannelAlreadyExistsError

    container = _container()
    try:
        channel = container.register_channel.execute(youtube_channel_id, name, niche)
    except ChannelAlreadyExistsError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc
    typer.echo(f"Canal registrado #{channel.id}: {channel.name} ({channel.youtube_channel_id})")
    if include_latest:
        video = container.bootstrap_channel.execute(channel.id)
        if video:
            typer.echo(f"Video encolado para descarga: {video.title} ({video.youtube_video_id})")
        else:
            typer.echo("El canal no tiene videos públicos para encolar.")


@channel_app.command("bootstrap")
def channel_bootstrap(
    channel_id: int = typer.Argument(help="ID numérico del canal (ver: shorts-factory channel list)"),
) -> None:
    """Encola el video más reciente de un canal ya registrado, sin esperar a que publique algo nuevo."""
    from shorts_factory.domain.use_cases.bootstrap_channel import ChannelNotFoundError

    container = _container()
    try:
        video = container.bootstrap_channel.execute(channel_id)
    except ChannelNotFoundError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc
    if video:
        typer.echo(f"Video encolado para descarga: {video.title} ({video.youtube_video_id})")
    else:
        typer.echo("El canal no tiene videos públicos para encolar.")


@channel_app.command("remove")
def channel_remove(
    channel_id: int = typer.Argument(help="ID numérico del canal (ver: shorts-factory channel list)"),
) -> None:
    """Elimina un canal. Si ya tiene videos asociados, se desactiva en vez de borrarse."""
    from shorts_factory.domain.use_cases.remove_channel import ChannelNotFoundError

    container = _container()
    try:
        deleted = container.remove_channel.execute(channel_id)
    except ChannelNotFoundError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc
    if deleted:
        typer.echo(f"Canal #{channel_id} eliminado.")
    else:
        typer.echo(
            f"Canal #{channel_id} tiene videos asociados: se desactivó en vez de"
            " borrarse (deja de escanearse, pero conserva su historial)."
        )


@channel_app.command("list")
def channel_list() -> None:
    """Lista los canales registrados."""
    container = _container()
    channels = container.channel_repo.list_all()
    if not channels:
        typer.echo("Sin canales registrados. Usa: shorts-factory channel add")
        return
    for ch in channels:
        estado = "activo" if ch.active else "inactivo"
        typer.echo(
            f"#{ch.id} {ch.name} ({ch.youtube_channel_id}) [{estado}]"
            f" último video: {ch.last_video_id or '—'}"
        )


@app.command()
def scan() -> None:
    """Escanea los canales registrados en busca de videos nuevos."""
    container = _container()
    results = container.scan_channels.execute()
    if not results:
        typer.echo("Sin canales activos que escanear.")
        return
    for r in results:
        if r.error:
            typer.echo(f"{r.channel_name}: ERROR — {r.error}")
        elif r.baseline_set:
            typer.echo(f"{r.channel_name}: línea base establecida (primer escaneo)")
        elif r.new_videos:
            typer.echo(f"{r.channel_name}: {len(r.new_videos)} video(s) nuevo(s)")
            for v in r.new_videos:
                typer.echo(f"  - {v.title} ({v.youtube_video_id})")
        else:
            typer.echo(f"{r.channel_name}: sin novedades")


@app.command()
def download() -> None:
    """Descarga los videos pendientes (estado detected)."""
    container = _container()
    report = container.download_videos.execute()
    if not report.downloaded and not report.failed:
        typer.echo("Sin videos pendientes de descarga.")
        return
    for video in report.downloaded:
        typer.echo(f"OK  {video.title} ({video.youtube_video_id})")
    for video, error in report.failed:
        typer.echo(f"FALLÓ  {video.title} ({video.youtube_video_id}): {error}")


@app.command()
def analyze() -> None:
    """Analiza videos descargados: detecta momentos y genera clips."""
    container = _container()
    report = container.analyze_videos.execute()
    if not report.analyzed and not report.failed:
        typer.echo("Sin videos pendientes de análisis.")
        return
    for video in report.analyzed:
        typer.echo(f"OK  {video.title} ({video.youtube_video_id})")
    typer.echo(f"Clips generados: {report.clips_created}")
    for video, error in report.failed:
        typer.echo(f"FALLÓ  {video.title}: {error}")


@app.command()
def publish(
    clip_id: int = typer.Option(
        None, "--clip", help="Publica solo este clip (ver: shorts-factory clips). Sin esto, publica todos los listos."
    ),
) -> None:
    """Publica los clips pendientes según la cola priorizada."""
    container = _container()
    if not container.publishers:
        typer.echo(
            "Sin plataformas habilitadas. Define SF_PLATFORMS en .env"
            " (p. ej. facebook,instagram,tiktok,x) y sus credenciales."
        )
        raise typer.Exit(code=1)
    report = container.publish_clips.execute(clip_id=clip_id)
    typer.echo(f"Encoladas: {report.enqueued}")
    for pub in report.published:
        typer.echo(f"OK  clip {pub.clip_id} -> {pub.platform.value}: {pub.post_url}")
    for pub in report.failed:
        typer.echo(
            f"FALLÓ  clip {pub.clip_id} -> {pub.platform.value}"
            f" (intento {pub.retry_count}): {pub.error_message}"
        )
    if not report.published and not report.failed and not report.enqueued:
        typer.echo("Sin publicaciones pendientes.")


@app.command()
def clips() -> None:
    """Lista los clips listos para publicar: motivo, duración y en qué redes ya salieron."""
    container = _container()
    items = container.list_publishable_clips.execute()
    if not items:
        typer.echo("Sin clips listos. Corre primero: shorts-factory analyze")
        return
    if container.list_publishable_clips.should_suggest_waiting():
        last = container.list_publishable_clips.last_published_at()
        typer.echo(f"⚠ Ya se publicó algo hace menos de 24h (última: {last}). Sugerencia: 1 por día.\n")
    for c in items:
        estado = "✔ archivo OK" if c.file_exists else "✘ archivo no encontrado"
        redes = ", ".join(sorted(c.published_on)) or "ninguna"
        typer.echo(
            f"#{c.clip_id} [{c.channel_name}] {c.video_title} ({c.duration_seconds:.0f}s,"
            f" score={c.impact_score:.2f}, {c.reason}) — {estado} — publicado en: {redes}"
        )


@media_app.command("list")
def media_list() -> None:
    """Lista los videos con su tamaño en disco (raw.mp4 + clips) y qué falta."""
    container = _container()
    assets = container.list_media_assets.execute()
    if not assets:
        typer.echo("Sin videos registrados.")
        return
    total = sum(a.total_size_bytes for a in assets)
    typer.echo(f"{len(assets)} video(s) · {total / (1024 * 1024):.1f} MB en disco\n")
    for a in assets:
        raw_bit = "✔ raw.mp4" if a.raw_exists else "✘ sin raw.mp4"
        existing = sum(1 for c in a.clips if c.exists)
        typer.echo(
            f"#{a.video_id} [{a.channel_name}] {a.title} — {a.status} — {raw_bit}"
            f" — clips: {existing}/{len(a.clips)} en disco"
            f" — {a.total_size_bytes / (1024 * 1024):.1f} MB"
        )


@media_app.command("remove")
def media_remove(
    video_id: int = typer.Argument(help="ID numérico del video (ver: shorts-factory media list)"),
    yes: bool = typer.Option(False, "--yes", "-y", help="No pedir confirmación"),
) -> None:
    """Borra raw.mp4 + clips de un video en disco y su historial en la BD. No se puede deshacer."""
    container = _container()
    if not yes:
        confirm = typer.confirm(
            f"¿Borrar el video #{video_id} (archivos en disco + historial en la BD)?"
        )
        if not confirm:
            raise typer.Abort()
    had_files = container.delete_video_files.execute(video_id)
    typer.echo(
        f"Video #{video_id} eliminado"
        + (" (con archivos en disco)." if had_files else " (solo el registro, sin archivos).")
    )


@app.command()
def run(
    once: bool = typer.Option(
        False, "--once", help="Ejecuta un solo ciclo en lugar de correr indefinidamente"
    ),
    interval: int = typer.Option(
        None, "--interval", "-i", help="Minutos entre ciclos (default: SF_PIPELINE_INTERVAL_MINUTES)"
    ),
) -> None:
    """Corre el pipeline completo (scan -> download -> analyze -> publish) desatendido."""
    import time

    container = _container()
    minutes = interval or container.settings.pipeline_interval_minutes

    def cycle() -> None:
        report = container.run_pipeline.execute()
        typer.echo(
            f"Ciclo: {report.new_videos} nuevos, {report.downloaded} descargados,"
            f" {report.analyzed} analizados, {report.clips_created} clips,"
            f" {report.published} publicados"
        )
        for stage, error in report.stage_errors:
            typer.echo(f"  ERROR en {stage}: {error}")

    if once:
        cycle()
        return
    typer.echo(f"Pipeline desatendido: un ciclo cada {minutes} min (Ctrl+C para salir)")
    try:
        while True:
            cycle()
            time.sleep(minutes * 60)
    except KeyboardInterrupt:
        typer.echo("Detenido por el usuario.")


@app.command()
def gui() -> None:
    """Abre la interfaz gráfica."""
    from shorts_factory.gui.app import main as gui_main

    gui_main()


if __name__ == "__main__":
    app()
