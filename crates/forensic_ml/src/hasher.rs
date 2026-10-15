use std::fs::File;
use std::io::{BufReader, Read};
use std::path::Path;
use sha2::{Digest, Sha256};
use anyhow::{Context, Result};

pub struct HashesForense {
    pub blake3_hex: String,
    pub sha256_hex: String,
    pub tamanho_bytes: u64,
}

pub fn calcular_hashes_duplos(caminho: &Path) -> Result<HashesForense> {
    let file = File::open(caminho)
        .with_context(|| format!("Falha ao abrir ficheiro: {:?}", caminho))?;
    let mut reader = BufReader::with_capacity(128 * 1024, file);

    let mut hasher_b3 = blake3::Hasher::new();
    let mut hasher_sha = Sha256::new();
    let mut buffer = [0u8; 64 * 1024];
    let mut tamanho_total = 0u64;

    loop {
        let n = reader.read(&mut buffer)?;
        if n == 0 {
            break;
        }
        let pedaco = &buffer[..n];
        hasher_b3.update(pedaco);
        hasher_sha.update(pedaco);
        tamanho_total += n as u64;
    }

    let b3_hex = hasher_b3.finalize().to_hex().to_string();
    let sha_hex = format!("{:x}", hasher_sha.finalize());

    Ok(HashesForense {
        blake3_hex: b3_hex,
        sha256_hex: sha_hex,
        tamanho_bytes: tamanho_total,
    })
}

pub fn calcular_hash_blake3_rapido(caminho: &Path) -> Result<String> {
    let file = File::open(caminho)
        .with_context(|| format!("Falha ao abrir ficheiro: {:?}", caminho))?;
    let mut reader = BufReader::with_capacity(128 * 1024, file);
    let mut hasher = blake3::Hasher::new();
    let mut buffer = [0u8; 64 * 1024];

    loop {
        let n = reader.read(&mut buffer)?;
        if n == 0 {
            break;
        }
        hasher.update(&buffer[..n]);
    }

    Ok(hasher.finalize().to_hex().to_string())
}
