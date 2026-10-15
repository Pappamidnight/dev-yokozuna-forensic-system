pub mod entropy;
pub mod hasher;
pub mod features;
pub mod cross_matcher;

pub use entropy::{calcular_entropia_buffer, calcular_histograma_bytes};
pub use hasher::{calcular_hashes_duplos, calcular_hash_blake3_rapido, HashesForense};
pub use features::{extrair_features_ficheiro, FeaturesForenseML};
pub use cross_matcher::{cruzar_caminhos_com_blake3, RelatorioCruzamentoForense, ResultadoCruzamento};
