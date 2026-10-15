//! acervo-vector — Vetores (stub)

pub struct VectorStore {
    pub url: String,
}

impl VectorStore {
    pub fn novo(url: &str) -> Self {
        Self { url: url.to_string() }
    }
}
