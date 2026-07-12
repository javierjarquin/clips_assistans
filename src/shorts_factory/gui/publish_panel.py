"""Panel de publicación manual: elegir qué clips salen, no "publicar todo".

Muestra los clips listos con su motivo/puntaje, si el archivo sigue en disco,
y en qué redes ya se publicaron (para no repetir). Si ya se publicó algo en
las últimas 24h, sugiere esperar — es una sugerencia, no bloquea.
"""

import customtkinter as ctk

from shorts_factory.infrastructure.config import load_settings
from shorts_factory.infrastructure.container import Container


class PublishPanel(ctk.CTkToplevel):
    def __init__(self, master) -> None:
        super().__init__(master)
        self._app = master
        self.title("Publicar clips")
        self.geometry("720x560")
        self.transient(master)
        self.grab_set()

        self._vars: dict[int, ctk.BooleanVar] = {}
        self._checkable_ids: set[int] = set()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(12, 4))
        self._banner = ctk.CTkLabel(header, text="", wraplength=680, justify="left", text_color="#e0a83a")
        self._banner.pack(anchor="w")

        self._list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._list_frame.pack(fill="both", expand=True, padx=12, pady=4)

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=12, pady=12)
        ctk.CTkButton(footer, text="Actualizar", fg_color="gray30", command=self._refresh).pack(
            side="left"
        )
        ctk.CTkButton(
            footer, text="Publicar seleccionados", command=self._on_publish_selected
        ).pack(side="right")
        ctk.CTkButton(
            footer, text="Cerrar", fg_color="gray30", command=self.destroy
        ).pack(side="right", padx=8)

        self._refresh()

    def _refresh(self) -> None:
        for child in self._list_frame.winfo_children():
            child.destroy()
        self._vars.clear()
        self._checkable_ids.clear()

        container = Container(load_settings())
        use_case = container.list_publishable_clips
        items = use_case.execute()
        enabled_platforms = set(container.settings.enabled_platforms)

        if use_case.should_suggest_waiting():
            last = use_case.last_published_at()
            self._banner.configure(
                text=(
                    f"⚠ Ya se publicó algo hace menos de 24h (última: {last:%Y-%m-%d %H:%M})."
                    " Sugerencia: 1 clip por día — puedes seguir de todas formas."
                )
            )
        else:
            self._banner.configure(text="")

        if not items:
            ctk.CTkLabel(
                self._list_frame, text="Sin clips listos. Corre primero: Analizar y cortar clips."
            ).pack(anchor="w", pady=8)
            return

        for c in items:
            row = ctk.CTkFrame(self._list_frame, fg_color="gray17")
            row.pack(fill="x", pady=4)

            pending_platforms = enabled_platforms - c.published_on
            already_done = enabled_platforms and not pending_platforms
            checkable = c.file_exists and not already_done

            var = ctk.BooleanVar(value=False)
            check = ctk.CTkCheckBox(row, text="", variable=var, width=20)
            check.pack(side="left", padx=(10, 6), pady=10)
            if not checkable:
                check.configure(state="disabled")
            else:
                self._vars[c.clip_id] = var
                self._checkable_ids.add(c.clip_id)

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, pady=8)
            ctk.CTkLabel(
                info, text=f"#{c.clip_id} [{c.channel_name}] {c.video_title}",
                anchor="w", font=("", 13, "bold"), wraplength=520,
            ).pack(anchor="w")
            duration = f"{c.duration_seconds:.0f}s" if c.duration_seconds else "?"
            score = f"{c.impact_score:.2f}" if c.impact_score is not None else "?"
            ctk.CTkLabel(
                info, text=f"{duration} · score {score} · {c.reason or 'sin motivo registrado'}",
                anchor="w", font=("", 11), text_color="gray70",
            ).pack(anchor="w")

            status_bits = []
            if not c.file_exists:
                status_bits.append("✘ archivo no encontrado en disco")
            if c.published_on:
                status_bits.append(f"ya publicado en: {', '.join(sorted(c.published_on))}")
            if already_done:
                status_bits.append("nada pendiente en las redes habilitadas")
            if status_bits:
                ctk.CTkLabel(
                    info, text=" · ".join(status_bits), anchor="w",
                    font=("", 11), text_color="#c95050" if not c.file_exists else "gray60",
                ).pack(anchor="w")

    def _on_publish_selected(self) -> None:
        selected = [clip_id for clip_id, var in self._vars.items() if var.get()]
        if not selected:
            self._app._log("Panel de publicación: no marcaste ningún clip.")
            return
        if len(selected) > 1:
            self._app._log(
                f"Panel de publicación: publicando {len(selected)} clips de una vez"
                " (la sugerencia es 1 por día)."
            )
        self._app._start_task("publish_selected", payload=selected)
        self.destroy()
