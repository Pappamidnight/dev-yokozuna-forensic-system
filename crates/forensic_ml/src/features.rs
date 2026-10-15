use std::fs::File;
use std::io::{BufReader, Read};
use std::path::Path;
use serde::{Deserialize, Serialize};
use anyhow::Result;
use crate::entropy::{calcular_entropia_buffer, calcular_histograma_bytes};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FeaturesForenseML {
    pub caminho: String,
    pub nome: String,
    pub extensao: String,
    pub tamanho_bytes: u64,
    pub magic_bytes_hex: String,
    pub tipo_magico_inferido: String,
    pub entropia_shannon: f64,
    pub ratio_ascii: f32,
    pub bytes_nulos: u64,
    pub histograma_frequencia: Vec<f32>,
    pub timestamp_analise: String,
}

pub fn inferir_tipo_por_magic_bytes(header: &[u8]) -> &'static str {
    if header.starts_with(b"%PDF") {
        "application/pdf"
    } else if header.starts_with(&[0xFF, 0xD8, 0xFF]) {
        "image/jpeg"
    } else if header.starts_with(&[0x89, b'P', b'N', b'G', 0x0D, 0x0A, 0x1A, 0x0A]) {
        "image/png"
    } else if header.starts_with(b"PK\x03\x04") {
        "application/zip_office_openxml"
    } else if header.starts_with(b"SQLite format 3\0") {
        "application/x-sqlite3"
    } else if header.starts_with(b"ID3") || header.starts_with(&[0xFF, 0xFB]) {
        "audio/mpeg"
    } else if header.starts_with(b"RIFF") && header.len() >= 12 && &header[8..12] == b"WAVE" {
        "audio/wav"
    } else if header.len() >= 12 && &header[4..8] == b"ftyp" {
        "video/mp4"
    } else if header.starts_with(b"{\n") || header.starts_with(b"{\r\n") || header.starts_with(b"{\"") {
        "application/json"
    } else if header.iter().all(|&b| b == 0x09 || b == 0x0A || b == 0x0D || (0x20..=0x7E).contains(&b)) {
        "text/plain_utf8"
    } else {
        "application/octet-stream"
    }
}

pub fn extrair_features_ficheiro(caminho: &Path) -> Result<FeaturesForenseML> {
    let file = File::open(caminho)?;
    let mut reader = BufReader::with_capacity(64 * 1024, file);

    let mut header = [0u8; 16];
    let n_header = reader.read(&mut header)?;
    let magic_bytes_hex = header[..n_header].iter().map(|b| format!("{:02X}", b)).collect::<Vec<_>>().join("");
    let tipo_inferido = inferir_tipo_por_magic_bytes(&header[..n_header]).to_string();

    let mut buffer = Vec::new();
    reader.read_to_end(&mut buffer)?;

    let mut full_buffer = Vec::with_capacity(n_header + buffer.len());
    full_buffer.extend_from_slice(&header[..n_header]);
    full_buffer.extend_from_slice(&buffer);

    let tamanho_bytes = full_buffer.len() as u64;
    let entropia = calcular_entropia_buffer(&full_buffer);
    let histograma = calcular_histograma_bytes(&full_buffer).to_vec();

    let mut bytes_ascii = 0u64;
    let mut bytes_nulos = 0u64;

    for &b in &full_buffer {
        if b == 0 {
            bytes_nulos += 1;
        }
        if (0x20..=0x7E).contains(&b) || b == 0x09 || b == 0x0A || b == 0x0D {
            bytes_ascii += 1;
        }
    }

    let ratio_ascii = if tamanho_bytes > 0 {
        bytes_ascii as f32 / tamanho_bytes as f32
    } else {
        0.0
    };

    let nome = caminho.file_name().unwrap_or_default().to_string_lossy().to_string();
    let extensao = caminho.extension().unwrap_or_default().to_string_lossy().to_string();

    Ok(FeaturesForenseML {
        caminho: caminho.to_string_lossy().to_string(),
        nome,
        extensao,
        tamanho_bytes,
        magic_bytes_hex,
        tipo_magico_inferido: tipo_inferido,
        entropia_shannon: entropia,
        ratio_ascii,
        bytes_nulos,
        histograma_frequencia: histograma,
        timestamp_analise: chrono::Utc::now().to_rfc3339(),
    })
}
