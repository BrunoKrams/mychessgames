CREATE TABLE IF NOT EXISTS games (
    id TEXT PRIMARY KEY,
    variant TEXT NOT NULL,
    speed TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    last_move_at INTEGER NOT NULL,
    winner TEXT,
    moves TEXT NOT NULL,
    opening_eco TEXT,
    FOREIGN KEY (opening_eco) REFERENCES openings(eco)
);

CREATE TABLE IF NOT EXISTS openings (
    eco TEXT PRIMARY KEY,
    name TEXT,
    ply INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS players (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    title TEXT
);

CREATE TABLE IF NOT EXISTS game_players (
    game_id TEXT NOT NULL,
    color TEXT NOT NULL,
    player_id TEXT NOT NULL,
    rating INTEGER NOT NULL,
    PRIMARY KEY (game_id, color),
    FOREIGN KEY (game_id) REFERENCES games(id),
    FOREIGN KEY (player_id) REFERENCES players(id)
);

CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id TEXT NOT NULL,
    name TEXT NOT NULL,
    UNIQUE(player_id, name),
    FOREIGN KEY (player_id) REFERENCES players(id)
);

CREATE TABLE IF NOT EXISTS rating_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rating_id INTEGER NOT NULL,
    date INTEGER NOT NULL,
    value INTEGER NOT NULL,
    UNIQUE(rating_id, date)
    FOREIGN KEY (rating_id) REFERENCES ratings(id)
);
