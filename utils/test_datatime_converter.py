from datetime import datetime, timezone
from unittest import TestCase

from datatime_converter import DateTimeConverter


class TestDateTimeConverter(TestCase):

    AS_UNIX_EPOCH = 1773779779286
    AS_DATETIME = datetime(2026, 3, 17, 20, 36, 19, 286000, tzinfo=timezone.utc)

    sut = DateTimeConverter()

    def test_to_datetime(self):
        # when
        result = self.sut.to_datetime(self.AS_UNIX_EPOCH)

        # then
        self.assertEqual(result, self.AS_DATETIME)

    def test_to_unix_epoch(self):
        # when
        result = self.sut.to_unix_epoch(self.AS_DATETIME)

        # then
        self.assertEqual(result, self.AS_UNIX_EPOCH)