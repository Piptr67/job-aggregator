from config import Settings
from sources.himalayas.source import HimalayasSource
from sources.remotive.source import RemotiveSource
from sources.source import Source


def get_sources(settings: Settings) -> list[Source]:
    return [
        HimalayasSource(
            settings.himalayas_rss_url,
            settings.fetch_timeout,
        ),
        RemotiveSource(
            settings.remotive_api_url,
            settings.fetch_timeout,
        ),
    ]