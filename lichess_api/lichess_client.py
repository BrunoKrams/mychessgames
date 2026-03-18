import json
from datetime import datetime
from typing import Iterator, Optional

import requests

from utils.datatime_converter import DateTimeConverter
from lichess_api.mapper import GameMapper, RatingMapper
from model import Game


class UserRatingHistory:
    def __init__(self, username: str, token: str) -> None:
        self.username = username
        self.token = token
        self.mapper = RatingMapper(self.username)
        self.session = requests.Session()

    def execute(self):
        url = f"https://lichess.org/api/user/{self.username}/rating-history"

        headers = {"Accept": "application/x-ndjson"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        resp = self.session.get(url, headers=headers)
        resp.raise_for_status()

        return self.mapper.map(resp.json())

class GamesUser:
    def __init__(self, username, token=None):
        self.username = username
        self.token = token
        self.session = requests.Session()
        self.mapper = GameMapper()
        self.converter = DateTimeConverter()

    def execute(self, since: Optional[datetime] = None) -> Iterator[Game]:
        url = f"https://lichess.org/api/games/user/{self.username}"

        params = {}
        if since:
            params["since"] = self.converter.to_unix_epoch(since)
        params["opening"] = True
        params["tags"] = False
        params["accuracy"] = True

        headers = {"Accept": "application/x-ndjson"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        resp = self.session.get(url, params=params, headers=headers, stream=True)
        resp.raise_for_status()

        for line in resp.iter_lines(decode_unicode=True):
            if line.strip():
                data = json.loads(line)
                yield self.mapper.map(data)
