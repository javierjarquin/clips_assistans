"""Busca en TikTok con Playwright y lista videos con sus vistas, para estudiar
el formato de los que más funcionan.

    python tools/tiktok_buscar.py "peliculas de terror basadas en hechos reales" [salida.json]
"""

import json
import sys
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import sync_playwright

consulta = sys.argv[1]
salida = Path(sys.argv[2]) if len(sys.argv) > 2 else None
CARPETA = Path(__file__).resolve().parent.parent / "analisis" / "tiktok"
CARPETA.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    nav = p.chromium.launch(headless=True)
    ctx = nav.new_context(locale="es-MX", viewport={"width": 1280, "height": 900},
                          user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                     "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
    pag = ctx.new_page()
    respuestas = []

    def guardar(r):
        if "/api/search/" in r.url or "item_list" in r.url:
            try:
                respuestas.append(r.json())
            except Exception:
                pass

    pag.on("response", guardar)
    url = consulta if consulta.startswith("http") else f"https://www.tiktok.com/search/video?q={quote(consulta)}"
    pag.goto(url, wait_until="domcontentloaded", timeout=60000)
    pag.wait_for_timeout(8000)
    for _ in range(3):
        pag.mouse.wheel(0, 3000)
        pag.wait_for_timeout(2500)
    pag.screenshot(path=str(CARPETA / "busqueda.png"))

    videos = {}
    for r in respuestas:
        for it in r.get("item_list") or r.get("data") or []:
            it = it.get("item", it)
            if not isinstance(it, dict) or "id" not in it:
                continue
            autor = (it.get("author") or {}).get("uniqueId", "")
            st = it.get("stats") or {}
            videos[it["id"]] = {"url": f"https://www.tiktok.com/@{autor}/video/{it['id']}",
                                "vistas": st.get("playCount", 0), "likes": st.get("diggCount", 0),
                                "duracion": (it.get("video") or {}).get("duration"),
                                "desc": it.get("desc", "")[:150]}
    if not videos:  # sin API: los enlaces del DOM
        for a in pag.query_selector_all("a[href*='/video/']"):
            h = a.get_attribute("href")
            videos[h] = {"url": h, "vistas": None, "texto": (a.inner_text() or "")[:80]}
    nav.close()

lista = sorted(videos.values(), key=lambda v: v.get("vistas") or 0, reverse=True)
for v in lista[:25]:
    print(v)
if salida:
    salida.write_text(json.dumps(lista, ensure_ascii=False, indent=2), encoding="utf-8")
