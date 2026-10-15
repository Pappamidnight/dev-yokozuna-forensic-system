//! acervo-core — Tipos, erros, config

use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    pub s3: S3Config,
    pub database: DbConfig,
    pub logging: LoggingConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct S3Config {
    pub endpoint: String,
    pub region: String,
    pub bucket: String,
    pub access_key: String,
    pub secret_key: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DbConfig {
    pub caminho: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LoggingConfig {
    pub nivel: String,
    pub path: String,
}

#[derive(Debug, thiserror::Error)]
pub enum AcervoError {
    #[error("Config: {0}")]
    Config(String),
    #[error("DB: {0}")]
    Db(String),
    #[error("Storage: {0}")]
    Storage(String),
    #[error("IO: {0}")]
    Io(#[from] std::io::Error),
    #[error("Serialization: {0}")]
    Serde(#[from] serde_json::Error),
}

pub type Result<T> = std::result::Result<T, AcervoError>;

/// Evento de domínio
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Evento {
    pub id: String,
    pub tipo: String,
    pub dados: serde_json::Value,
    pub timestamp: DateTime<Utc>,
    pub source: String,
}

impl Evento {
    pub fn novo(tipo: impl Into<String>, dados: serde_json::Value, source: impl Into<String>) -> Self {
        Self {
            id: uuid::Uuid::new_v4().to_string(),
            tipo: tipo.into(),
            dados,
            timestamp: Utc::now(),
            source: source.into(),
        }
    }
}
