/// Calculo de Entropia de Shannon para analise forense de ficheiros
/// Formula: H(X) = - sum(P(x) * log2(P(x)))

pub fn calcular_entropia_buffer(buffer: &[u8]) -> f64 {
    if buffer.is_empty() {
        return 0.0;
    }

    let mut contagens = [0u64; 256];
    for &byte in buffer {
        contagens[byte as usize] += 1;
    }

    let total = buffer.len() as f64;
    let mut entropia = 0.0;

    for &contagem in &contagens {
        if contagem > 0 {
            let p = contagem as f64 / total;
            entropia -= p * p.log2();
        }
    }

    entropia
}

pub fn calcular_histograma_bytes(buffer: &[u8]) -> [f32; 256] {
    let mut histograma = [0f32; 256];
    if buffer.is_empty() {
        return histograma;
    }

    let mut contagens = [0u64; 256];
    for &byte in buffer {
        contagens[byte as usize] += 1;
    }

    let total = buffer.len() as f32;
    for (i, &c) in contagens.iter().enumerate() {
        histograma[i] = c as f32 / total;
    }

    histograma
}
