"""Detección de cambios de escena con PySceneDetect (ContentDetector)."""

import logging
from pathlib import Path

from shorts_factory.ports.analysis import SceneDetectorPort

logger = logging.getLogger(__name__)


class PySceneDetectAdapter(SceneDetectorPort):
    def __init__(self, threshold: float = 27.0) -> None:
        self._threshold = threshold

    def detect_scene_changes(self, media_path: Path) -> list[float]:
        from scenedetect import ContentDetector, detect

        scenes = detect(str(media_path), ContentDetector(threshold=self._threshold))
        # El inicio de cada escena (salvo la primera) es un cambio de plano
        changes = [float(start.get_seconds()) for start, _ in scenes[1:]]
        logger.info("Escenas de %s: %d cambios", media_path.name, len(changes))
        return changes
