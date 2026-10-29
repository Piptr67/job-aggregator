class IngestionError(Exception):
    """An expected failure while fetching or parsing an ingestion source."""

    def __init__(
        self,
        message: str,
        *,
        jobs_inserted: int = 0,
        failed_sources: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.jobs_inserted = jobs_inserted
        self.failed_sources = failed_sources or []
