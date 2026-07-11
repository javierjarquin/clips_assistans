from shorts_factory.domain.services.impact_scorer import score_moments
from shorts_factory.ports.analysis import AudioPeak
from shorts_factory.ports.inference_engine import TranscriptSegment


def _peaks_at(*times: float, intensity: float = 1.0) -> list[AudioPeak]:
    return [AudioPeak(time_seconds=t, intensity=intensity) for t in times]


def test_no_signals_no_moments() -> None:
    assert score_moments(300, [], [], []) == []


def test_audio_cluster_produces_moment_around_peak() -> None:
    moments = score_moments(
        duration_seconds=300,
        transcript=[],
        audio_peaks=_peaks_at(118, 120, 122, 124),
        scene_changes=[],
        target_clip_seconds=30,
    )
    assert len(moments) == 1
    m = moments[0]
    assert m.start_seconds <= 118 <= m.end_seconds
    assert m.end_seconds - m.start_seconds <= 60
    assert "audio" in m.reason


def test_respects_max_moments_and_no_overlap() -> None:
    peaks = _peaks_at(30, 32, 34, 150, 152, 154, 270, 272, 274)
    moments = score_moments(
        duration_seconds=400,
        transcript=[],
        audio_peaks=peaks,
        scene_changes=[],
        max_moments=2,
        target_clip_seconds=20,
    )
    assert len(moments) <= 2
    for a, b in zip(moments, moments[1:]):
        assert a.end_seconds <= b.start_seconds  # sin traslape, ordenados


def test_transcript_reaction_words_contribute() -> None:
    transcript = [
        TranscriptSegment(100, 104, "¡No puede ser! ¡Increíble!"),
        TranscriptSegment(104, 108, "wow no way"),
    ]
    moments = score_moments(
        duration_seconds=300,
        transcript=transcript,
        audio_peaks=_peaks_at(102, 105, intensity=0.5),
        scene_changes=[100.5, 103.0, 106.0],
        target_clip_seconds=20,
    )
    assert len(moments) >= 1
    assert moments[0].start_seconds <= 102 <= moments[0].end_seconds


def test_clip_never_exceeds_max_seconds() -> None:
    moments = score_moments(
        duration_seconds=500,
        transcript=[],
        audio_peaks=_peaks_at(*range(100, 200, 3)),
        scene_changes=[],
        target_clip_seconds=90,  # pide más del máximo
        max_clip_seconds=60,
    )
    for m in moments:
        assert m.end_seconds - m.start_seconds <= 60


def test_start_snaps_to_transcript_boundary() -> None:
    transcript = [TranscriptSegment(118.4, 125.0, "esto está pasando de verdad")]
    moments = score_moments(
        duration_seconds=300,
        transcript=transcript,
        audio_peaks=_peaks_at(119, 121, 123),
        scene_changes=[],
        target_clip_seconds=30,
    )
    assert moments and abs(moments[0].start_seconds - 118.4) < 0.01
