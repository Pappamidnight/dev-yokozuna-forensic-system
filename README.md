# ACERVO — Rust Zero Custo

## Estrutura
- crates/     — Bibliotecas partilhadas
- services/   — Serviços
- db/         — SQLite
- config/     — Configuração
- logs/       — Logs
- bin/        — Binários

## Compilar
cargo build --release

## Correr
.\bin\acervo-gateway.exe

## DB
sqlite3 db\acervo.db ".read db\schema.sql"
