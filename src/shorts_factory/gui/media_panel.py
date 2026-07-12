"""Panel de gestión de archivos: qué videos/clips hay en disco y borrarlos
desde la app — borrar la carpeta a mano deja la base de datos apuntando a
archivos que ya no existen (justo lo que pasó y motivó este panel).
"""

from tkinter import messagebox

import customtkinter as ctk

from shorts_factory.infrastructure.config import load_settings
from shorts_factory.infrastructure.container import Container

STATUS_LABELS = {
    "detected": "Detectado",
    "downloading": "Descargando",
    "downloaded": "Descargado",
    "analyzing": "Analizando",
    "analyzed": "Analizado",
    "done": "Terminado",
    "error": "Error",
}


def _format_size(num_bytes: int | None) -> str:
    if not num_bytes:
        return "0 B"
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


class MediaPanel(ctk.CTkToplevel):
    def __init__(self, master) -> None:
        super().__init__(master)
        self._app = master
        self.title("Gestionar archivos")
        self.geometry("760x580")
        self.transient(master)
        self.grab_set()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(12, 4))
        self._summary = ctk.CTkLabel(header, text="", font=("", 13, "bold"), anchor="w")
        self._summary.pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Borrar aquí limpia también la base de datos. Borrar la carpeta a mano no —"
            " por eso los clips quedan huérfanos y el panel de publicación los marca como"
            " 'archivo no encontrado'.",
            wraplength=720, justify="left", font=("", 11), text_color="gray70",
        ).pack(anchor="w", pady=(2, 0))

        self._list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._list_frame.pack(fill="both", expand=True, padx=12, pady=4)

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=12, pady=12)
        ctk.CTkButton(footer, text="Actualizar", fg_color="gray30", command=self._refresh).pack(
            side="left"
        )
        ctk.CTkButton(
            footer, text="Cerrar", fg_color="gray30", command=self.destroy
        ).pack(side="right")

        self._refresh()

    def _refresh(self) -> None:
        for child in self._list_frame.winfo_children():
            child.destroy()

        container = Container(load_settings())
        assets = container.list_media_assets.execute()

        total = sum(a.total_size_bytes for a in assets)
        self._summary.configure(
            text=f"{len(assets)} video(s) en la base de datos · {_format_size(total)} en disco"
        )

        if not assets:
            ctk.CTkLabel(self._list_frame, text="Sin videos registrados.").pack(
                anchor="w", pady=8
            )
            return

        for asset in assets:
            row = ctk.CTkFrame(self._list_frame, fg_color="gray17")
            row.pack(fill="x", pady=4)

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=10, pady=8)
            ctk.CTkLabel(
                info, text=f"[{asset.channel_name}] {asset.title}",
                anchor="w", font=("", 13, "bold"), wraplength=520,
            ).pack(anchor="w")

            estado = STATUS_LABELS.get(asset.status, asset.status)
            raw_bit = "✔ raw.mp4" if asset.raw_exists else "✘ sin raw.mp4"
            existing_clips = sum(1 for c in asset.clips if c.exists)
            clips_bit = f"clips: {existing_clips}/{len(asset.clips)} en disco" if asset.clips else "sin clips"
            ctk.CTkLabel(
                info,
                text=f"Estado: {estado} · {raw_bit} · {clips_bit} · {_format_size(asset.total_size_bytes)}",
                anchor="w", font=("", 11), text_color="gray70",
            ).pack(anchor="w")

            if not asset.raw_exists and not existing_clips and (asset.raw_path or asset.clips):
                ctk.CTkLabel(
                    info, text="Archivos ausentes en disco — este registro ya no ocupa espacio,"
                    " pero conviene borrarlo para no verlo como 'roto' en el panel de publicar.",
                    anchor="w", font=("", 11), text_color="#c95050", wraplength=520,
                ).pack(anchor="w")

            ctk.CTkButton(
                row, text="🗑 Eliminar", fg_color="#8b2f2f", hover_color="#6e2424", width=100,
                command=lambda a=asset: self._on_delete(a),
            ).pack(side="right", padx=10, pady=8)

    def _on_delete(self, asset) -> None:
        confirm = messagebox.askyesno(
            "Eliminar video",
            f"¿Borrar \"{asset.title}\"?\n\n"
            f"Esto elimina raw.mp4 y sus {len(asset.clips)} clip(s) del disco"
            f" ({_format_size(asset.total_size_bytes)}) y todo su historial de la base de datos."
            " No se puede deshacer.",
            parent=self,
        )
        if not confirm:
            return
        container = Container(load_settings())
        had_files = container.delete_video_files.execute(asset.video_id)
        self._app._log(
            f"Eliminado: [{asset.channel_name}] {asset.title}"
            + (" (con archivos en disco)" if had_files else " (solo registro, sin archivos)")
        )
        self._refresh()
