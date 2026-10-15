//! Files Service — upload, download, hash

use acervo_core::{Evento, Result};
use acervo_db::DbPool;
use acervo_events::EventBus;
use serde::{Deserialize, Serialize};
use std::path::Path;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FicheiroInfo {
    pub id: i64,
    pub nome: String,
    pub hash_sha256: String,
    pub tamanho: i64,
    pub s3_key: String,
}

pub struct FilesService {
    pool: DbPool,
    bus: EventBus,
    storage_dir: String,
}

impl FilesService {
    pub fn novo(pool: DbPool, bus: EventBus, storage_dir: impl Into<String>) -> Self {
        Self {
            pool,
            bus,
            storage_dir: storage_dir.into(),
        }
    }

    pub fn importar(&self, caminho: &Path) -> Result<FicheiroInfo> {
        let dados = std::fs::read(caminho)?;
        let hash = acervo_storage::Storage::hash_sha256(&dados);
        let blake3 = acervo_storage::Storage::hash_blake3(&dados);
        let nome = caminho.file_name()
            .and_then(|n| n.to_str())
            .unwrap_or("desconhecido")
            .to_string();
        let tamanho = dados.len() as i64;
        let s3_key = format!("files/{}/{}", &hash[..2], &hash);

        let destino = Path::new(&self.storage_dir).join(&s3_key);
        if let Some(parent) = destino.parent() {
            std::fs::create_dir_all(parent)?;
        }
        std::fs::write(&destino, &dados)?;

        let conn = self.pool.get()
            .map_err(|e| acervo_core::AcervoError::Db(e.to_string()))?;
        conn.execute(
            "INSERT OR IGNORE INTO ficheiros (hash_sha256, hash_blake3, nome, s3_key, tamanho) VALUES (?1, ?2, ?3, ?4, ?5)",
            rusqlite::params![&hash, &blake3, &nome, &s3_key, tamanho],
        ).map_err(|e| acervo_core::AcervoError::Db(e.to_string()))?;

        let id = conn.last_insert_rowid();

        let ev = Evento::novo("FILE_IMPORTED", serde_json::json!({
            "id": id,
            "nome": nome,
            "hash": hash,
            "tamanho": tamanho
        }), "files");
        self.bus.emitir(ev);

        Ok(FicheiroInfo { id, nome, hash_sha256: hash, tamanho, s3_key })
    }

    pub fn listar(&self) -> Result<Vec<FicheiroInfo>> {
        let conn = self.pool.get()
            .map_err(|e| acervo_core::AcervoError::Db(e.to_string()))?;
        let mut stmt = conn.prepare("SELECT id, nome, hash_sha256, tamanho, s3_key FROM ficheiros ORDER BY id DESC LIMIT 1000")
            .map_err(|e| acervo_core::AcervoError::Db(e.to_string()))?;
        let rows = stmt.query_map([], |row| {
            Ok(FicheiroInfo {
                id: row.get(0)?,
                nome: row.get(1)?,
                hash_sha256: row.get(2)?,
                tamanho: row.get(3)?,
                s3_key: row.get(4)?,
            })
        }).map_err(|e| acervo_core::AcervoError::Db(e.to_string()))?;

        let mut out = Vec::new();
        for r in rows {
            out.push(r.map_err(|e| acervo_core::AcervoError::Db(e.to_string()))?);
        }
        Ok(out)
    }
}
