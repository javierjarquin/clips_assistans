from shorts_factory.domain.use_cases.run_pipeline import RunPipeline


class StageOK:
    def __init__(self, result):
        self._result = result
        self.calls = 0

    def execute(self):
        self.calls += 1
        return self._result


class StageBoom:
    def execute(self):
        raise RuntimeError("fase rota")


class ScanResult:
    def __init__(self, n):
        self.new_videos = [object()] * n


class DownloadResult:
    downloaded = [object()]
    failed = []


class AnalyzeResult:
    analyzed = [object(), object()]
    clips_created = 3
    failed = []


class PublishResult:
    published = [object()]
    failed = []
    enqueued = 1


def test_full_cycle_aggregates_counts() -> None:
    pipeline = RunPipeline(
        StageOK([ScanResult(2)]),
        StageOK(DownloadResult()),
        StageOK(AnalyzeResult()),
        StageOK(PublishResult()),
    )

    report = pipeline.execute()

    assert report.new_videos == 2
    assert report.downloaded == 1
    assert report.analyzed == 2
    assert report.clips_created == 3
    assert report.published == 1
    assert report.stage_errors == []


def test_stage_error_does_not_stop_cycle() -> None:
    analyze = StageOK(AnalyzeResult())
    publish = StageOK(PublishResult())
    pipeline = RunPipeline(StageOK([ScanResult(0)]), StageBoom(), analyze, publish)

    report = pipeline.execute()

    assert ("download", "fase rota") in report.stage_errors
    assert analyze.calls == 1, "analyze corre aunque download falle"
    assert publish.calls == 1
    assert report.analyzed == 2


def test_publish_skipped_when_no_platforms() -> None:
    pipeline = RunPipeline(
        StageOK([ScanResult(0)]),
        StageOK(DownloadResult()),
        StageOK(AnalyzeResult()),
        publish=None,
    )

    report = pipeline.execute()

    assert report.published == 0
    assert report.stage_errors == []
