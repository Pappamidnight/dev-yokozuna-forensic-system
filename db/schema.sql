PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;
PRAGMA synchronous = NORMAL;

CREATE TABLE IF NOT EXISTS casos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo        TEXT UNIQUE NOT NULL,
    nome          TEXT NOT NULL,
    tribunal      TEXT,
    estado        TEXT DEFAULT 'ATIVO',
    criado_em     TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS partes (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    nome  TEXT NOT NULL,
    nif   TEXT,
    tipo  TEXT,
    papel TEXT
);

CREATE TABLE IF NOT EXISTS ficheiros (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    hash_sha256   TEXT UNIQUE NOT NULL,
    hash_blake3   TEXT,
    nome          TEXT NOT NULL,
    s3_key        TEXT NOT NULL,
    tamanho       INTEGER NOT NULL,
    mime          TEXT,
    tipo          TEXT,
    valor         TEXT,
    sensibilidade TEXT,
    caso_id       INTEGER REFERENCES casos(id),
    criado_em     TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS classificacoes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ficheiro_id INTEGER REFERENCES ficheiros(id),
    tipo        TEXT,
    valor       TEXT,
    confianca   REAL,
    criado_em   TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS refutacoes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    caso_id   INTEGER REFERENCES casos(id),
    tipo      TEXT,
    alegacao  TEXT,
    refutacao TEXT,
    norma     TEXT,
    criado_em TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS custody_ledger (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    evento      TEXT NOT NULL,
    ficheiro_id INTEGER REFERENCES ficheiros(id),
    hash_antes  TEXT,
    hash_depois TEXT,
    ator        TEXT,
    detalhes    TEXT,
    ts          TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS triggers_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger_id TEXT NOT NULL,
    evento     TEXT NOT NULL,
    dados      TEXT,
    resultado  TEXT,
    ts         TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_ficheiros_hash ON ficheiros(hash_sha256);
CREATE INDEX IF NOT EXISTS idx_ficheiros_tipo ON ficheiros(tipo);
CREATE INDEX IF NOT EXISTS idx_class_ficheiro ON classificacoes(ficheiro_id);
CREATE INDEX IF NOT EXISTS idx_custody_ficheiro ON custody_ledger(ficheiro_id);
