"""Ventana de configuración: credenciales de APIs y parámetros del pipeline.

Guarda en el .env del proyecto (env_store) — misma fuente que usan CLI y GUI.
Los tokens se muestran enmascarados con opción de ver.
"""

import customtkinter as ctk

from shorts_factory.infrastructure.env_store import read_env, save_env

PLATFORMS = ("facebook", "instagram", "tiktok", "x")

WHISPER_MODELS = ("tiny", "base", "small", "medium", "large-v3", "distil-large-v3")

TIKTOK_PRIVACY = (
    "SELF_ONLY",
    "PUBLIC_TO_EVERYONE",
    "MUTUAL_FOLLOW_FRIENDS",
    "FOLLOWER_OF_CREATOR",
)


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master, on_saved=None) -> None:
        super().__init__(master)
        self.title("Configuración")
        self.geometry("640x600")
        self.transient(master)
        self.grab_set()
        self._on_saved = on_saved
        self._values = read_env()
        self._entries: dict[str, ctk.CTkEntry] = {}
        self._secret_entries: list[ctk.CTkEntry] = []
        self._platform_vars: dict[str, ctk.BooleanVar] = {}

        tabs = ctk.CTkTabview(self)
        tabs.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        self._build_platforms_tab(tabs.add("Redes y llaves"))
        self._build_analysis_tab(tabs.add("Análisis y clips"))
        self._build_general_tab(tabs.add("General"))

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=10, pady=10)
        self._show_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            footer, text="Mostrar llaves", variable=self._show_var, command=self._toggle_secrets
        ).pack(side="left")
        ctk.CTkButton(footer, text="Guardar", command=self._save).pack(side="right")
        ctk.CTkButton(
            footer, text="Cancelar", fg_color="gray30", command=self.destroy
        ).pack(side="right", padx=8)

    # ---------------------------------------------------------------- tabs

    def _build_platforms_tab(self, tab) -> None:
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text="Plataformas habilitadas", font=("", 14, "bold")).pack(
            anchor="w", pady=(4, 2)
        )
        enabled = {
            p.strip().lower() for p in self._values.get("SF_PLATFORMS", "").split(",") if p.strip()
        }
        row = ctk.CTkFrame(scroll, fg_color="transparent")
        row.pack(anchor="w", pady=(0, 8))
        for platform in PLATFORMS:
            var = ctk.BooleanVar(value=platform in enabled)
            self._platform_vars[platform] = var
            ctk.CTkCheckBox(row, text=platform.capitalize(), variable=var).pack(
                side="left", padx=(0, 12)
            )

        self._section(scroll, "Meta — Facebook Reels + Instagram Reels (una sola app)")
        self._hint(
            scroll,
            "Requiere página de Facebook + cuenta IG empresa/creador vinculada."
            " El Page Access Token long-lived dura ~60 días; App ID/Secret sirven"
            " para renovarlo. IG User ID: GET /{page-id}?fields=instagram_business_account",
        )
        self._field(scroll, "App ID de Meta", "SF_META_APP_ID")
        self._field(scroll, "App Secret de Meta", "SF_META_APP_SECRET", secret=True)
        self._field(scroll, "ID de la página de Facebook", "SF_META_PAGE_ID")
        self._field(
            scroll,
            "Page Access Token (long-lived, de la página)",
            "SF_META_PAGE_ACCESS_TOKEN",
            secret=True,
        )
        self._field(
            scroll,
            "User Access Token (para renovación automática — mismo intercambio"
            " que dio el Page Access Token)",
            "SF_META_USER_ACCESS_TOKEN",
            secret=True,
        )
        self._field(scroll, "IG User ID (cuenta empresa/creador)", "SF_META_IG_USER_ID")
        self._field(scroll, "Versión de Graph API", "SF_META_GRAPH_VERSION", default="v23.0")

        self._section(scroll, "TikTok — Content Posting API (OAuth2)")
        self._hint(
            scroll,
            "Client Key/Secret salen del portal de desarrolladores; el Refresh Token"
            " del flujo OAuth inicial. El sistema renueva el access token solo (dura 24 h)"
            " y guarda aquí el refresh token cuando TikTok lo rota.",
        )
        self._field(scroll, "Client Key", "SF_TIKTOK_CLIENT_KEY")
        self._field(scroll, "Client Secret", "SF_TIKTOK_CLIENT_SECRET", secret=True)
        self._field(scroll, "Refresh Token", "SF_TIKTOK_REFRESH_TOKEN", secret=True)
        self._dropdown(
            scroll,
            "Privacidad (SELF_ONLY hasta pasar auditoría)",
            "SF_TIKTOK_PRIVACY_LEVEL",
            TIKTOK_PRIVACY,
            default="SELF_ONLY",
        )

        self._section(scroll, "X — API v2, OAuth2 con PKCE (pago por uso)")
        self._hint(
            scroll,
            "Client ID (y Secret si la app es confidencial) del portal de desarrolladores;"
            " Refresh Token del flujo OAuth con scope offline.access. El refresh token es"
            " de un solo uso: el sistema lo renueva y lo guarda aquí automáticamente."
            " Los enlaces se eliminan del texto (con enlace cuesta ~13x más).",
        )
        self._field(scroll, "Client ID", "SF_X_CLIENT_ID")
        self._field(scroll, "Client Secret (solo apps confidenciales)", "SF_X_CLIENT_SECRET", secret=True)
        self._field(scroll, "Refresh Token", "SF_X_REFRESH_TOKEN", secret=True)

    def _build_analysis_tab(self, tab) -> None:
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        self._dropdown(
            scroll, "Modelo de Whisper", "SF_WHISPER_MODEL", WHISPER_MODELS, default="small"
        )
        self._field(scroll, "Idioma forzado (vacío = auto)", "SF_WHISPER_LANGUAGE")
        self._field(scroll, "Duración objetivo del clip (s)", "SF_CLIP_TARGET_SECONDS", default="30")
        self._field(scroll, "Duración máxima del clip (s)", "SF_CLIP_MAX_SECONDS", default="60")
        self._field(scroll, "Duración mínima del clip (s)", "SF_CLIP_MIN_SECONDS", default="10")
        self._field(scroll, "Clips máximos por video", "SF_MAX_CLIPS_PER_VIDEO", default="4")

    def _build_general_tab(self, tab) -> None:
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        self._field(scroll, "Carpeta de datos (videos y clips)", "SF_DATA_DIR", default="data")
        self._field(scroll, "Videos recientes a revisar por escaneo", "SF_SCAN_LIMIT", default="10")
        self._field(
            scroll, "Minutos entre ciclos desatendidos", "SF_PIPELINE_INTERVAL_MINUTES", default="30"
        )
        self._field(
            scroll,
            "Navegador para cookies de yt-dlp (chrome/firefox/edge; vacío = sin cookies)",
            "SF_YTDLP_COOKIES_BROWSER",
        )

    # ------------------------------------------------------------- widgets

    def _section(self, parent, text: str) -> None:
        ctk.CTkLabel(parent, text=text, font=("", 14, "bold")).pack(anchor="w", pady=(14, 2))

    def _hint(self, parent, text: str) -> None:
        ctk.CTkLabel(
            parent, text=text, wraplength=540, justify="left",
            font=("", 11), text_color="gray70",
        ).pack(anchor="w", pady=(0, 4))

    def _field(self, parent, label: str, key: str, secret: bool = False, default: str = "") -> None:
        ctk.CTkLabel(parent, text=label).pack(anchor="w", pady=(6, 0))
        entry = ctk.CTkEntry(parent, width=560, show="•" if secret else "")
        entry.insert(0, self._values.get(key, default))
        entry.pack(anchor="w")
        self._entries[key] = entry
        if secret:
            self._secret_entries.append(entry)

    def _dropdown(self, parent, label: str, key: str, options: tuple, default: str) -> None:
        ctk.CTkLabel(parent, text=label).pack(anchor="w", pady=(6, 0))
        menu = ctk.CTkOptionMenu(parent, values=list(options), width=280)
        menu.set(self._values.get(key, default) or default)
        menu.pack(anchor="w")
        # Se registra como pseudo-entry con la misma interfaz get()
        self._entries[key] = menu

    def _toggle_secrets(self) -> None:
        show = "" if self._show_var.get() else "•"
        for entry in self._secret_entries:
            entry.configure(show=show)

    # ---------------------------------------------------------------- save

    def _save(self) -> None:
        updates = {key: widget.get().strip() for key, widget in self._entries.items()}
        updates["SF_PLATFORMS"] = ",".join(
            p for p, var in self._platform_vars.items() if var.get()
        )
        save_env(updates)
        if self._on_saved:
            self._on_saved()
        self.destroy()
