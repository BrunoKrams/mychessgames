from datetime import datetime, timezone


class DateTimeConverter:

    def to_datetime(self, unix_epoch_ms: int, tz: timezone = timezone.utc) -> datetime:
        return datetime.fromtimestamp(unix_epoch_ms / 1000, tz)

    def to_unix_epoch(self, dt: datetime) -> int:
        return int(dt.timestamp() * 1000)

