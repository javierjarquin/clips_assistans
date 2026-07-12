"""GUI de Shorts Factory (CustomTkinter).

Diseño: la ventana es un puerto conductor más — usa los mismos casos de uso
que la CLI a través del contenedor. Cada acción corre en un hilo de trabajo
con su propio contenedor (SQLite exige conexión por hilo); el hilo publica
progreso en una cola y la UI la drena con `after()`.
"""

import logging
import os
import queue
import subprocess
import sys
import threading
from datetime import datetime

import customtkinter as ctk

from shorts_factory.infrastructure.config import load_settings
from shorts_factory.infrastructure.container import Container

PHASE_LABELS = [
    ("detected", "Detectados"),
    ("downloading", "Descargando"),
    ("downloaded", "Descargados"),
    ("analyzing", "Analizando"),
    ("analyzed", "Analizados"),
    ("done", "Terminados"),
    ("error", "Con error"),
]


class QueueLogHandler(logging.Handler):
    """Reenvía los logs de los casos de uso a la cola de la UI: ese es el progreso fino."""

    def __init__(self, log_queue: queue.Queue) -> None:
        super().__init__()
        self._queue = log_queue
        self.setFormatter(logging.Formatter("%(message)s"))

    def emit(self, record: logging.LogRecord) -> None:
        self._queue.put(("log", self.format(record)))


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Shorts Factory")
        self.geometry("980x640")
        self.minsize(860, 560)
        ctk.set_appearance_mode("dark")

        self._queue: queue.Queue = queue.Queue()
        self._busy = False
        self._action_buttons: list[ctk.CTkButton] = []

        self._log_handler = QueueLogHandler(self._queue)
        self._log_handler.setLevel(logging.INFO)
        logging.getLogger("shorts_factory").addHandler(self._log_handler)
        logging.getLogger("shorts_factory").setLevel(logging.INFO)

        self._build_layout()
        self._init_db()
        self._refresh_channels()
        self._refresh_status()
        self.after(120, self._drain_queue)

    # ------------------------------------------------------------- layout

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Columna izquierda: canales + acciones ---
        left = ctk.CTkFrame(self, width=300)
        left.grid(row=0, column=0, sticky="nsw", padx=(10, 5), pady=10)

        ctk.CTkLabel(left, text="Canales", font=("", 16, "bold")).pack(
            anchor="w", padx=12, pady=(12, 4)
        )
        self._channels_box = ctk.CTkTextbox(left, height=110, width=280, state="disabled")
        self._channels_box.pack(padx=12, pady=(0, 8), fill="x")

        self._channel_id = ctk.CTkEntry(left, placeholder_text="@handle o ID del canal")
        self._channel_id.pack(padx=12, pady=2, fill="x")
        self._channel_name = ctk.CTkEntry(left, placeholder_text="Nombre")
        self._channel_name.pack(padx=12, pady=2, fill="x")
        self._channel_niche = ctk.CTkEntry(left, placeholder_text="Nicho (opcional)")
        self._channel_niche.pack(padx=12, pady=2, fill="x")
        self._channel_include_latest = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            left, text="Encolar el video más reciente ya (para probar)",
            variable=self._channel_include_latest, font=("", 11),
        ).pack(anchor="w", padx=12, pady=(2, 4))
        add_btn = ctk.CTkButton(left, text="Agregar canal", command=self._on_add_channel)
        add_btn.pack(padx=12, pady=(0, 4), fill="x")
        self._action_buttons.append(add_btn)

        remove_row = ctk.CTkFrame(left, fg_color="transparent")
        remove_row.pack(padx=12, pady=(0, 12), fill="x")
        remove_row.grid_columnconfigure(0, weight=1)
        self._channel_remove_id = ctk.CTkEntry(remove_row, placeholder_text="ID a eliminar")
        self._channel_remove_id.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        remove_btn = ctk.CTkButton(
            remove_row, text="Eliminar", width=80, fg_color="#8b2f2f",
            hover_color="#6e2424", command=self._on_remove_channel,
        )
        remove_btn.grid(row=0, column=1)
        self._action_buttons.append(remove_btn)

        bootstrap_row = ctk.CTkFrame(left, fg_color="transparent")
        bootstrap_row.pack(padx=12, pady=(0, 12), fill="x")
        bootstrap_row.grid_columnconfigure(0, weight=1)
        self._channel_bootstrap_id = ctk.CTkEntry(bootstrap_row, placeholder_text="ID para encolar último video")
        self._channel_bootstrap_id.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        bootstrap_btn = ctk.CTkButton(
            bootstrap_row, text="Encolar", width=80,
            command=self._on_bootstrap_from_field,
        )
        bootstrap_btn.grid(row=0, column=1)
        self._action_buttons.append(bootstrap_btn)

        ctk.CTkLabel(left, text="Pipeline", font=("", 16, "bold")).pack(
            anchor="w", padx=12, pady=(4, 4)
        )
        for text, action in [
            ("1. Escanear canales", "scan"),
            ("2. Descargar videos", "download"),
            ("3. Analizar y cortar clips", "analyze"),
            ("4. Publicar en redes", "publish"),
            ("Ciclo completo", "cycle"),
        ]:
            btn = ctk.CTkButton(left, text=text, command=lambda a=action: self._start_task(a))
            btn.pack(padx=12, pady=3, fill="x")
            self._action_buttons.append(btn)

        ctk.CTkButton(
            left, text="📋 Publicar clips (manual)", fg_color="gray30",
            command=self._open_publish_panel,
        ).pack(padx=12, pady=(10, 3), fill="x")
        ctk.CTkButton(
            left, text="🗂 Gestionar archivos", fg_color="gray30",
            command=self._open_media_panel,
        ).pack(padx=12, pady=(3, 3), fill="x")
        ctk.CTkButton(
            left, text="Abrir carpeta de clips", fg_color="gray30",
            command=self._open_data_dir,
        ).pack(padx=12, pady=(3, 3), fill="x")
        ctk.CTkButton(
            left, text="⚙  Configuración", fg_color="gray30",
            command=self._open_settings,
        ).pack(padx=12, pady=(3, 12), fill="x")

        # --- Columna derecha: progreso + estado + log ---
        right = ctk.CTkFrame(self)
        right.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(3, weight=1)

        progress_frame = ctk.CTkFrame(right, fg_color="transparent")
        progress_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 4))
        progress_frame.grid_columnconfigure(0, weight=1)
        self._phase_label = ctk.CTkLabel(progress_frame, text="Listo", anchor="w")
        self._phase_label.grid(row=0, column=0, sticky="ew")
        self._progress = ctk.CTkProgressBar(progress_frame, mode="indeterminate")
        self._progress.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self._progress.set(0)

        ctk.CTkLabel(right, text="Videos por fase", font=("", 14, "bold")).grid(
            row=1, column=0, sticky="w", padx=12, pady=(10, 2)
        )
        counts_frame = ctk.CTkFrame(right)
        counts_frame.grid(row=2, column=0, sticky="ew", padx=12)
        self._count_labels: dict[str, ctk.CTkLabel] = {}
        for i, (status, label) in enumerate(PHASE_LABELS):
            cell = ctk.CTkFrame(counts_frame, fg_color="gray20")
            cell.grid(row=0, column=i, padx=3, pady=6, sticky="ew")
            counts_frame.grid_columnconfigure(i, weight=1)
            value = ctk.CTkLabel(cell, text="0", font=("", 18, "bold"))
            value.pack(pady=(6, 0))
            ctk.CTkLabel(cell, text=label, font=("", 10)).pack(pady=(0, 6))
            self._count_labels[status] = value
        self._clips_label = ctk.CTkLabel(right, text="Clips listos: 0 · Publicados: 0", anchor="w")
        self._clips_label.grid(row=2, column=0, sticky="sw", padx=16, pady=(78, 0))

        ctk.CTkLabel(right, text="Actividad", font=("", 14, "bold")).grid(
            row=3, column=0, sticky="nw", padx=12, pady=(12, 0)
        )
        self._log_box = ctk.CTkTextbox(right, state="disabled", wrap="word")
        self._log_box.grid(row=3, column=0, sticky="nsew", padx=12, pady=(40, 12))

    # ------------------------------------------------------------- helpers

    def _log(self, message: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        self._log_box.configure(state="normal")
        self._log_box.insert("end", f"[{stamp}] {message}\n")
        self._log_box.see("end")
        self._log_box.configure(state="disabled")

    def _init_db(self) -> None:
        container = Container(load_settings())
        applied = container.init_db()
        if applied:
            self._log(f"Base de datos migrada: {', '.join(applied)}")

    def _refresh_channels(self) -> None:
        container = Container(load_settings())
        channels = container.channel_repo.list_all()
        self._channels_box.configure(state="normal")
        self._channels_box.delete("1.0", "end")
        if channels:
            for ch in channels:
                estado = "" if ch.active else " [inactivo]"
                self._channels_box.insert(
                    "end", f"#{ch.id} {ch.name} ({ch.youtube_channel_id}){estado}\n"
                )
        else:
            self._channels_box.insert("end", "Sin canales registrados")
        self._channels_box.configure(state="disabled")

    def _refresh_status(self) -> None:
        container = Container(load_settings())
        conn = container.connection
        counts = dict(
            conn.execute("SELECT status, COUNT(*) FROM videos GROUP BY status").fetchall()
        )
        for status, label in self._count_labels.items():
            label.configure(text=str(counts.get(status, 0)))
        clips_ready = conn.execute(
            "SELECT COUNT(*) FROM clips WHERE status = 'ready'"
        ).fetchone()[0]
        published = conn.execute(
            "SELECT COUNT(*) FROM publish_log WHERE status = 'published'"
        ).fetchone()[0]
        self._clips_label.configure(
            text=f"Clips listos: {clips_ready} · Publicados: {published}"
        )

    def _open_settings(self) -> None:
        from shorts_factory.gui.settings_window import SettingsWindow

        def on_saved() -> None:
            self._log("Configuración guardada en .env")
            self._refresh_status()

        SettingsWindow(self, on_saved=on_saved)

    def _open_publish_panel(self) -> None:
        from shorts_factory.gui.publish_panel import PublishPanel

        PublishPanel(self)

    def _open_media_panel(self) -> None:
        from shorts_factory.gui.media_panel import MediaPanel

        MediaPanel(self)

    def _open_data_dir(self) -> None:
        data_dir = load_settings().data_dir
        data_dir.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(data_dir)  # noqa: S606
        else:
            subprocess.run(["xdg-open", str(data_dir)], check=False)

    def _set_busy(self, busy: bool, phase_text: str = "Listo") -> None:
        self._busy = busy
        state = "disabled" if busy else "normal"
        for btn in self._action_buttons:
            btn.configure(state=state)
        self._phase_label.configure(text=phase_text)
        if busy:
            self._progress.start()
        else:
            self._progress.stop()
            self._progress.set(0)

    # ------------------------------------------------------------- acciones

    def _on_add_channel(self) -> None:
        from shorts_factory.domain.use_cases.register_channel import ChannelAlreadyExistsError

        channel_id = self._channel_id.get().strip()
        name = self._channel_name.get().strip()
        niche = self._channel_niche.get().strip() or None
        include_latest = self._channel_include_latest.get()
        if not channel_id or not name:
            self._log("Faltan datos: canal y nombre son obligatorios.")
            return
        try:
            container = Container(load_settings())
            channel = container.register_channel.execute(channel_id, name, niche)
        except ChannelAlreadyExistsError as exc:
            self._log(str(exc))
            return
        self._log(f"Canal registrado: {channel.name} ({channel.youtube_channel_id})")
        self._channel_id.delete(0, "end")
        self._channel_name.delete(0, "end")
        self._channel_niche.delete(0, "end")
        self._channel_include_latest.set(False)
        self._refresh_channels()
        if include_latest:
            self._start_task("bootstrap", payload=channel.id)

    def _on_bootstrap_channel(self, channel_id: int) -> None:
        self._start_task("bootstrap", payload=channel_id)

    def _on_bootstrap_from_field(self) -> None:
        raw_id = self._channel_bootstrap_id.get().strip()
        if not raw_id.isdigit():
            self._log("Escribe el ID numérico del canal (ver lista arriba).")
            return
        self._channel_bootstrap_id.delete(0, "end")
        self._on_bootstrap_channel(int(raw_id))

    def _on_remove_channel(self) -> None:
        from shorts_factory.domain.use_cases.remove_channel import ChannelNotFoundError

        raw_id = self._channel_remove_id.get().strip()
        if not raw_id.isdigit():
            self._log("Escribe el ID numérico del canal a eliminar (ver lista arriba).")
            return
        container = Container(load_settings())
        try:
            deleted = container.remove_channel.execute(int(raw_id))
        except ChannelNotFoundError as exc:
            self._log(str(exc))
            return
        if deleted:
            self._log(f"Canal #{raw_id} eliminado.")
        else:
            self._log(
                f"Canal #{raw_id} tiene videos asociados: se desactivó en vez de"
                " borrarse (deja de escanearse, conserva su historial)."
            )
        self._channel_remove_id.delete(0, "end")
        self._refresh_channels()

    def _start_task(self, action: str, payload=None) -> None:
        if self._busy:
            return
        titles = {
            "bootstrap": "Encolando el video más reciente…",
            "scan": "Escaneando canales…",
            "download": "Descargando videos…",
            "analyze": "Analizando y cortando clips…",
            "publish": "Publicando en redes…",
            "publish_selected": f"Publicando {len(payload or [])} clip(s) seleccionado(s)…",
            "cycle": "Ciclo completo en curso…",
        }
        self._set_busy(True, titles[action])
        self._log(titles[action])
        threading.Thread(target=self._worker, args=(action, payload), daemon=True).start()

    def _worker(self, action: str, payload=None) -> None:
        """Corre en hilo aparte: contenedor propio (SQLite = conexión por hilo)."""
        try:
            container = Container(load_settings())
            if action == "scan":
                results = container.scan_channels.execute()
                for r in results:
                    if r.error:
                        self._queue.put(("log", f"{r.channel_name}: ERROR — {r.error}"))
                    elif r.baseline_set:
                        self._queue.put(
                            ("log", f"{r.channel_name}: línea base establecida (primer escaneo)")
                        )
                    else:
                        self._queue.put(
                            ("log", f"{r.channel_name}: {len(r.new_videos)} video(s) nuevo(s)")
                        )
            elif action == "bootstrap":
                video = container.bootstrap_channel.execute(payload)
                if video:
                    self._queue.put(
                        ("log", f"Video encolado para descarga: {video.title} ({video.youtube_video_id})")
                    )
                else:
                    self._queue.put(("log", "El canal no tiene videos públicos para encolar."))
            elif action == "download":
                report = container.download_videos.execute()
                self._queue.put(
                    ("log", f"Descargados: {len(report.downloaded)} · Fallidos: {len(report.failed)}")
                )
            elif action == "analyze":
                report = container.analyze_videos.execute()
                self._queue.put(
                    ("log", f"Analizados: {len(report.analyzed)} · Clips: {report.clips_created}")
                )
            elif action == "publish":
                if not container.publishers:
                    self._queue.put(
                        ("log", "Sin plataformas habilitadas: define SF_PLATFORMS en .env")
                    )
                else:
                    report = container.publish_clips.execute()
                    self._queue.put(
                        ("log", f"Publicados: {len(report.published)} · Fallidos: {len(report.failed)}")
                    )
            elif action == "publish_selected":
                if not container.publishers:
                    self._queue.put(
                        ("log", "Sin plataformas habilitadas: define SF_PLATFORMS en .env")
                    )
                else:
                    for clip_id in payload or []:
                        report = container.publish_clips.execute(clip_id=clip_id)
                        for pub in report.published:
                            self._queue.put(
                                (
                                    "log",
                                    f"OK clip {pub.clip_id} -> {pub.platform.value}: {pub.post_url}",
                                )
                            )
                        for pub in report.failed:
                            self._queue.put(
                                (
                                    "log",
                                    f"FALLÓ clip {pub.clip_id} -> {pub.platform.value}"
                                    f" (intento {pub.retry_count}): {pub.error_message}",
                                )
                            )
            elif action == "cycle":
                report = container.run_pipeline.execute()
                self._queue.put(
                    (
                        "log",
                        f"Ciclo: {report.new_videos} nuevos, {report.downloaded} descargados,"
                        f" {report.analyzed} analizados, {report.clips_created} clips,"
                        f" {report.published} publicados",
                    )
                )
                for stage, error in report.stage_errors:
                    self._queue.put(("log", f"ERROR en {stage}: {error}"))
        except Exception as exc:  # noqa: BLE001 — la UI informa, no revienta
            self._queue.put(("log", f"ERROR: {exc}"))
        finally:
            self._queue.put(("done", None))

    # ------------------------------------------------------------- cola/UI

    def _drain_queue(self) -> None:
        try:
            while True:
                kind, payload = self._queue.get_nowait()
                if kind == "log":
                    self._log(payload)
                elif kind == "done":
                    self._set_busy(False)
                    self._refresh_channels()
                    self._refresh_status()
        except queue.Empty:
            pass
        if self._busy:
            self._refresh_status()  # progreso en vivo: conteos por fase mientras trabaja
        self.after(500 if self._busy else 120, self._drain_queue)


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
