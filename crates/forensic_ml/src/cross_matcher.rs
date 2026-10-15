use std::collections::HashMap;
use std::path::Path;
use serde::{Deserialize, Serialize};
use anyhow::Result;
use crate::hasher::calcular_hashes_duplos;
use crate::features::extrair_features_ficheiro;

#[derive(Debug, Serialize, Deserialize)]
pub enum NivelCorrespondencia {
    Nivel1NomeTamanho,
    Nivel2HashExatoBlake3,
    Nivel3SimilaridadeForenseML,
    UnicoApenasOrigem,
    UnicoApenasDestino,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ResultadoCruzamento {
    pub ficheiro_origem: String,
    pub ficheiro_candidato: Option<String>,
    pub nivel: NivelCorrespondencia,
    pub hash_blake3: Option<String>,
    pub score_confianca: f32,
    pub justificacao: String,
}

#[derive(Debug, Default, Serialize, Deserialize)]
pub struct RelatorioCruzamentoForense {
    pub total_analisados: usize,
    pub duplicados_exatos_blake3: usize,
    pub candidatos_nivel1: usize,
    pub ficheiros_unicos: usize,
    pub detalhes: Vec<ResultadoCruzamento>,
}

pub fn cruzar_caminhos_com_blake3(
    caminhos_origem: &[String],
    caminhos_destino: &[String],
) -> Result<RelatorioCruzamentoForense> {
    let mut mapa_destino_blake3: HashMap<String, String> = HashMap::new();
    let mut relatorio = RelatorioCruzamentoForense::default();

    // 1. Indexar hashes BLAKE3 do destino
    for p in caminhos_destino {
        let path = Path::new(p);
        if path.is_file() {
            if let Ok(hashes) = calcular_hashes_duplos(path) {
                mapa_destino_blake3.insert(hashes.blake3_hex, p.clone());
            }
        }
    }

    // 2. Cruzar cada ficheiro de origem
    for p in caminhos_origem {
        let path = Path::new(p);
        if !path.is_file() {
            continue;
        }

        relatorio.total_analisados += 1;
        if let Ok(hashes_orig) = calcular_hashes_duplos(path) {
            if let Some(candidato_dest) = mapa_destino_blake3.get(&hashes_orig.blake3_hex) {
                relatorio.duplicados_exatos_blake3 += 1;
                relatorio.detalhes.push(ResultadoCruzamento {
                    ficheiro_origem: p.clone(),
                    ficheiro_candidato: Some(candidato_dest.clone()),
                    nivel: NivelCorrespondencia::Nivel2HashExatoBlake3,
                    hash_blake3: Some(hashes_orig.blake3_hex),
                    score_confianca: 1.0,
                    justificacao: "Identidade binaria absoluta via hash BLAKE3".to_string(),
                });
            } else {
                relatorio.ficheiros_unicos += 1;
                relatorio.detalhes.push(ResultadoCruzamento {
                    ficheiro_origem: p.clone(),
                    ficheiro_candidato: None,
                    nivel: NivelCorrespondencia::UnicoApenasOrigem,
                    hash_blake3: Some(hashes_orig.blake3_hex),
                    score_confianca: 0.0,
                    justificacao: "Ficheiro unico sem correspondencia no destino".to_string(),
                });
            }
        }
    }

    Ok(relatorio)
}
