import settings
from statsd import StatsClient

client = StatsClient('127.0.0.1', 8125, prefix=settings.STATSD_PREFIX)

if not settings.STATSD:
    client._send = lambda data: None
