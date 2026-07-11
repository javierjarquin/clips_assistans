"""CLI de Shorts Factory.

Etapa 0: `init` y `status` funcionan; el resto son esqueletos que se
implementan en su etapa correspondiente del plan de ejecución.
"""

import typer

from shorts_factory.infrastructure.config import load_settings
from shorts_factory.infrastructure.container import Container
from shorts_factory.infrastructure.database import list_tables
from shorts_factory.infrastructure.logging_config import setup_logging

app = typer.Typer(
    help="Shorts Factory — pipeline local de generación y publicación de Shorts/Reels.",
    no_args_is_help=True,
)
channel_app = typer.Typer(help="Gestión de canales monitoreados.", no_args_is_help=True)
app.add_typer(channel_app, name="channel")


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
def publish() -> None:
    """Publica los clips pendientes según la cola priorizada."""
    container = _container()
    if not container.publishers:
        typer.echo(
            "Sin plataformas habilitadas. Define SF_PLATFORMS en .env"
            " (p. ej. facebook,instagram,tiktok,x) y sus credenciales."
        )
        raise typer.Exit(code=1)
    report = container.publish_clips.execute()
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
