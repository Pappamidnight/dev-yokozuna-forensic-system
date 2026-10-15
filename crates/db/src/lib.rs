//! acervo-db — SQLite client

use r2d2::Pool;
use r2d2_sqlite::SqliteConnectionManager;
use acervo_core::Result;

pub type DbPool = Pool<SqliteConnectionManager>;

pub fn init(caminho: &str) -> Result<DbPool> {
    let manager = SqliteConnectionManager::file(caminho);
    let pool = Pool::builder()
        .max_size(10)
        .build(manager)
        .map_err(|e| acervo_core::AcervoError::Db(e.to_string()))?;

    // Aplicar PRAGMAs
    let conn = pool.get().map_err(|e| acervo_core::AcervoError::Db(e.to_string()))?;
    conn.execute_batch("
        PRAGMA journal_mode = WAL;
        PRAGMA foreign_keys = ON;
        PRAGMA synchronous = NORMAL;
    ").map_err(|e| acervo_core::AcervoError::Db(e.to_string()))?;

    Ok(pool)
}
