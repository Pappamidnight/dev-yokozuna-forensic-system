use std::path::Path;
use std::env;
use std::fs::File;
use std::io::{BufRead, BufReader, Write};
use anyhow::{Context, Result};
use acervo_forensic_ml::{calcular_hashes_duplos, extrair_features_ficheiro, cruzar_caminhos_com_blake3};

fn main() -> Result<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("==============================================================================");
        eprintln!("  ACERVO FORENSE V8 — MOTOR RUST DE ALTA VELOCIDADE & MACHINE LEARNING");
        eprintln!("==============================================================================");
        eprintln!("Uso:");
        eprintln!("  forensic-ml hash <ficheiro>                     Calcula BLAKE3 e SHA-256");
        eprintln!("  forensic-ml features <ficheiro>                 Extrai features binarias e estatisticas");
        eprintln!("  forensic-ml cross-match <origem.txt> <dest.txt> Executa cruzamento atomico em 3 niveis");
        eprintln!("  forensic-ml scan-features <diretorio> <saida>   Extrai dataset de features para ML");
        return Ok(());
    }

    let comando = &args[1];

    match comando.as_str() {
        "hash" => {
            if args.len() < 3 {
                eprintln!("Erro: Especifique o caminho do ficheiro.");
                std::process::exit(1);
            }
            let caminho = Path::new(&args[2]);
            let res = calcular_hashes_duplos(caminho)?;
            println!("{{");
            println!("  \"ficheiro\": {:?},", caminho.display().to_string());
            println!("  \"tamanho_bytes\": {},", res.tamanho_bytes);
            println!("  \"blake3\": {:?},", res.blake3_hex);
            println!("  \"sha256\": {:?}", res.sha256_hex);
            println!("}}");
        }
        "features" => {
            if args.len() < 3 {
                eprintln!("Erro: Especifique o caminho do ficheiro.");
                std::process::exit(1);
            }
            let caminho = Path::new(&args[2]);
            let feats = extrair_features_ficheiro(caminho)?;
            let json = serde_json::to_string_pretty(&feats)?;
            println!("{}", json);
        }
        "cross-match" => {
            if args.len() < 4 {
                eprintln!("Erro: Uso: forensic-ml cross-match <origem.txt> <dest.txt>");
                std::process::exit(1);
            }
            let arq_orig = File::open(&args[2])?;
            let origens: Vec<String> = BufReader::new(arq_orig).lines().filter_map(|l| l.ok()).collect();

            let arq_dest = File::open(&args[3])?;
            let destinos: Vec<String> = BufReader::new(arq_dest).lines().filter_map(|l| l.ok()).collect();

            let relatorio = cruzar_caminhos_com_blake3(&origens, &destinos)?;
            let json = serde_json::to_string_pretty(&relatorio)?;
            println!("{}", json);
        }
        "scan-features" => {
            if args.len() < 4 {
                eprintln!("Erro: Uso: forensic-ml scan-features <diretorio> <saida.jsonl>");
                std::process::exit(1);
            }
            let dir = Path::new(&args[2]);
            let mut out = File::create(&args[3])?;
            let mut contagem = 0;

            if dir.is_dir() {
                for entry in std::fs::read_dir(dir)? {
                    if let Ok(entry) = entry {
                        let path = entry.path();
                        if path.is_file() {
                            if let Ok(feats) = extrair_features_ficheiro(&path) {
                                if let Ok(linha) = serde_json::to_string(&feats) {
                                    writeln!(out, "{}", linha)?;
                                    contagem += 1;
                                }
                            }
                        }
                    }
                }
            }
            println!("Sucesso: {} ficheiros analisados e gravados em {:?}", contagem, args[3]);
        }
        _ => {
            eprintln!("Comando desconhecido: {}", comando);
            std::process::exit(1);
        }
    }

    Ok(())
}
