from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

class Opening:
    def __init__(self, eco: str, name: str, ply: int):
        self.eco = eco
        self.name = name
        self.ply = ply


class User:
    def __init__(self, id: str, name: str, title: str):
        self.id = id
        self.name = name
        self.title = title


class GamePlayer:
    def __init__(self, rating: int, user: User):
        self.rating = rating
        self.user = user

class Color(Enum):
    WHITE = 0
    BLACK = 1

class Game:
    def __init__(self, id: str, variant: str, speed: str, created_at: datetime, last_move_at: datetime,
                 players: Dict[Color, GamePlayer], opening: Opening, winner: Color, moves: str):
        self.id = id
        self.variant = variant
        self.speed = speed
        self.created_at = created_at
        self.last_move_at = last_move_at
        self.players = players
        self.opening = opening
        self.winner = winner
        self.moves = moves

class RatingPoint:
    def __init__(self, date: datetime, value: int):
        self.date = date
        self.value = value

class RatingHistory:
    def __init__(self, username: str, ratings: Dict[str, List[RatingPoint]]):
        self.username = username
        self.ratings = ratings
