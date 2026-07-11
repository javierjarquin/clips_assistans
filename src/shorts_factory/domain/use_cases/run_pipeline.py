"""Ciclo completo del pipeline: scan -> download -> analyze -> publish.

Cada fase está blindada: un error en una fase se registra y el ciclo continúa
con la siguiente (los estados en BD permiten retomar en el siguiente ciclo).
"""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CycleReport:
    new_videos: int = 0
    downloaded: int = 0
    analyzed: int = 0
    clips_created: int = 0
    published: int = 0
    stage_errors: list[tuple[str, str]] = field(default_factory=list)


class RunPipeline:
    def __init__(self, scan, download, analyze, publish=None) -> None:
        self._scan = scan
        self._download = download
        self._analyze = analyze
        self._publish = publish  # None si no hay plataformas habilitadas

    def execute(self) -> CycleReport:
        report = CycleReport()

        try:
            results = self._scan.execute()
            report.new_videos = sum(len(r.new_videos) for r in results)
        except Exception as exc:  # noqa: BLE001
            logger.error("Fase scan falló: %s", exc)
            report.stage_errors.append(("scan", str(exc)))

        try:
            dl = self._download.execute()
            report.downloaded = len(dl.downloaded)
        except Exception as exc:  # noqa: BLE001
            logger.error("Fase download falló: %s", exc)
            report.stage_errors.append(("download", str(exc)))

        try:
            an = self._analyze.execute()
            report.analyzed = len(an.analyzed)
            report.clips_created = an.clips_created
        except Exception as exc:  # noqa: BLE001
            logger.error("Fase analyze falló: %s", exc)
            report.stage_errors.append(("analyze", str(exc)))

        if self._publish is not None:
            try:
                pub = self._publish.execute()
                report.published = len(pub.published)
            except Exception as exc:  # noqa: BLE001
                logger.error("Fase publish falló: %s", exc)
                report.stage_errors.append(("publish", str(exc)))
        else:
            logger.info("Publicación omitida: sin plataformas habilitadas")

        return report
