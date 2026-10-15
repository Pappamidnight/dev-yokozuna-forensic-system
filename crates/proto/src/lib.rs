//! acervo-proto — Tipos de mensagens

use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Mensagem {
    pub r#type: String,
    pub id: String,
    pub ts: DateTime<Utc>,
    pub source: String,
    pub data: serde_json::Value,
    pub v: u32,
}

impl Mensagem {
    pub fn nova(tipo: &str, data: serde_json::Value, source: &str) -> Self {
        Self {
            r#type: tipo.to_string(),
            id: uuid::Uuid::new_v4().to_string(),
            ts: Utc::now(),
            source: source.to_string(),
            data,
            v: 1,
        }
    }
}
