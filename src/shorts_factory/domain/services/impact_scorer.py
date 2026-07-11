"""Puntaje de impacto: combina audio, escenas y transcripción en momentos candidatos.

Python puro (regla hexagonal: el dominio no importa librerías externas).
Resolución de 1 segundo — suficiente para clips de 10-60s y barato de calcular.

Hipótesis v1 (a calibrar con material real, ver análisis técnico §9):
- pico de audio = reacción probable (volumen, risa, grito)
- ráfaga de cambios de escena = énfasis de edición
- exclamaciones/palabras de reacción en el texto = confirmación semántica
"""

from dataclasses import dataclass

from shorts_factory.ports.analysis import AudioPeak
from shorts_factory.ports.inference_engine import TranscriptSegment

# Palabras que suelen acompañar reacciones (es/en); minúsculas, sin acentos estrictos
_REACTION_WORDS = (
    "increible", "increíble", "no puede ser", "no way", "oh my god", "omg", "wow",
    "que fuerte", "qué fuerte", "no mames", "brutal", "insane", "crazy", "jaja",
    "haha", "lol", "dios mio", "dios mío", "espera", "wait", "what", "qué",
)

_WEIGHT_AUDIO = 1.0
_WEIGHT_SCENE = 0.6
_WEIGHT_TEXT = 0.8
_AUDIO_SPREAD_SECONDS = 2  # un pico irradia puntaje a ±2s
_SCENE_BURST_WINDOW = 5.0  # cortes separados <5s cuentan como ráfaga


@dataclass(frozen=True)
class MomentCandidate:
    start_seconds: float
    end_seconds: float
    impact_score: float
    reason: str


def _text_signal(segment: TranscriptSegment) -> float:
    text = segment.text.lower()
    score = 0.0
    if "!" in text or "¡" in text:
        score += 0.5
    score += sum(0.5 for word in _REACTION_WORDS if word in text)
    return min(score, 1.5)


def score_moments(
    duration_seconds: float,
    transcript: list[TranscriptSegment],
    audio_peaks: list[AudioPeak],
    scene_changes: list[float],
    min_clip_seconds: float = 10.0,
    max_clip_seconds: float = 60.0,
    target_clip_seconds: float = 30.0,
    max_moments: int = 4,
) -> list[MomentCandidate]:
    total = int(duration_seconds) + 1
    if total <= 0:
        return []

    audio = [0.0] * total
    scene = [0.0] * total
    text = [0.0] * total

    for peak in audio_peaks:
        center = int(peak.time_seconds)
        for offset in range(-_AUDIO_SPREAD_SECONDS, _AUDIO_SPREAD_SECONDS + 1):
            t = center + offset
            if 0 <= t < total:
                falloff = 1.0 - abs(offset) / (_AUDIO_SPREAD_SECONDS + 1)
                audio[t] += peak.intensity * falloff

    for i, change in enumerate(scene_changes):
        t = int(change)
        if 0 <= t < total:
            scene[t] += 0.5
            # ráfaga: cortes cercanos entre sí valen más que cortes sueltos
            if i > 0 and change - scene_changes[i - 1] < _SCENE_BURST_WINDOW:
                scene[t] += 0.5

    for segment in transcript:
        signal = _text_signal(segment)
        if signal <= 0:
            continue
        for t in range(int(segment.start_seconds), min(int(segment.end_seconds) + 1, total)):
            text[t] += signal / max(segment.end_seconds - segment.start_seconds, 1.0)

    combined = [
        _WEIGHT_AUDIO * audio[t] + _WEIGHT_SCENE * scene[t] + _WEIGHT_TEXT * text[t]
        for t in range(total)
    ]
    # Suavizado (media móvil de 3) para que picos aislados formen mesetas seleccionables
    smoothed = [
        (combined[max(t - 1, 0)] + combined[t] + combined[min(t + 1, total - 1)]) / 3
        for t in range(total)
    ]

    window = int(min(max(target_clip_seconds, min_clip_seconds), max_clip_seconds, duration_seconds))
    if window < min_clip_seconds:
        return []

    # Umbral: un pico debe sobresalir del ruido de fondo para generar momento
    mean_score = sum(smoothed) / total
    variance = sum((s - mean_score) ** 2 for s in smoothed) / total
    threshold = mean_score + 0.5 * (variance**0.5)

    remaining = list(smoothed)
    candidates: list[MomentCandidate] = []
    taken: list[tuple[float, float]] = []
    for _ in range(max_moments * 10):  # guardia contra bucles con señales patológicas
        if len(candidates) >= max_moments:
            break
        t_star = max(range(total), key=lambda t: remaining[t])
        if remaining[t_star] <= threshold or remaining[t_star] <= 0:
            break

        # El pico cae al ~25% del clip: contexto antes, reacción y desenlace después
        naive_start = min(max(t_star - window * 0.25, 0.0), duration_seconds - window)
        start = _snap_start(naive_start, t_star, transcript)
        end = min(start + window, duration_seconds)

        # Enmascarar la zona del pico pase lo que pase, para que el bucle avance
        for t in range(max(int(start) - 1, 0), min(int(end) + 1, total)):
            remaining[t] = 0.0

        if end - start < min_clip_seconds:
            continue
        if any(not (end <= t0 or start >= t1) for t0, t1 in taken):
            continue

        window_score = sum(smoothed[int(start):int(end)]) / max(end - start, 1.0)
        reason = _dominant_reason(int(start), int(end), audio, scene, text)
        candidates.append(
            MomentCandidate(
                start_seconds=round(start, 3),
                end_seconds=round(end, 3),
                impact_score=round(window_score, 4),
                reason=reason,
            )
        )
        taken.append((start, end))

    candidates.sort(key=lambda m: m.start_seconds)
    return candidates


def _snap_start(
    naive_start: float, t_star: float, transcript: list[TranscriptSegment]
) -> float:
    """Arranca el clip al inicio de la frase más cercana al lead-in natural.

    Solo considera frases que empiezan entre el lead-in (con 2s de gracia) y el
    pico: nunca después del pico (cortaría la reacción a la mitad).
    """
    best: float | None = None
    best_dist = float("inf")
    for segment in transcript:
        if naive_start - 2.0 <= segment.start_seconds <= t_star:
            dist = abs(segment.start_seconds - naive_start)
            if dist < best_dist:
                best, best_dist = segment.start_seconds, dist
    return max(best if best is not None else naive_start, 0.0)


def _dominant_reason(
    start: int, end: int, audio: list[float], scene: list[float], text: list[float]
) -> str:
    sums = {
        "picos de audio": _WEIGHT_AUDIO * sum(audio[start:end]),
        "cambios de escena": _WEIGHT_SCENE * sum(scene[start:end]),
        "reacción en el habla": _WEIGHT_TEXT * sum(text[start:end]),
    }
    ranked = sorted(sums.items(), key=lambda kv: kv[1], reverse=True)
    strong = [name for name, value in ranked if value > 0.25 * ranked[0][1] and value > 0]
    return " + ".join(strong[:2]) if strong else "señal débil"
