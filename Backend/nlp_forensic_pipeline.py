#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nlp_forensic_pipeline.py - Pipeline de NLP, Scikit-Learn (TF-IDF), NER e Classificacao Semantica de Documentos Judiciais.
Extrai entidades nomeadas, vetoriza textos com TF-IDF e calcula similaridade semantica no acervo forense.
"""

import os
import sys
import re
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
DB_PATH = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "02_DADOS_ESTRUTURADOS" / "memoria_forense_unificada.db"
TRIBUNAL_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "04_DOCUMENTOS_CITIUS_E_PECAS" / "ARQUIVO_OFICIAL_TRIBUNAL"
OUTPUT_REPORT = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "01_INDEX_E_RELATORIOS" / "RELATORIO_NLP_NER_SCIKIT.json"

# Padroes RegEx de NER Forense (Reconhecimento de Entidades Nomeadas)
NER_PATTERNS = {
    "NIF": re.compile(r"\b(?:NIF|NIPC)[:\s]*([125689]\d{8})\b", re.IGNORECASE),
    "REF_CITIUS": re.compile(r"\b(?:Ref\.|Referência)[:\s]*(\d{8,10})\b", re.IGNORECASE),
    "VALOR_EUR": re.compile(r"(?:€|EUR)\s*([\d.,]+)|([\d.,]+)\s*(?:€|EUR)", re.IGNORECASE),
    "ARTIGO_LEI": re.compile(r"\b(?:Art\.?|Artigo)\s*(\d{1,4}(?:[º°]|.º)?(?:\s*n\.º\s*\d+)?(?:\s*al\.?\s*[a-z]\)?)?)\s*(?:do\s+)?(CPC|CC|CP|CRP|Código do Notariado|CIRE)\b", re.IGNORECASE),
    "PROCESSO": re.compile(r"\b(\d{1,6}/\d{2}\.\d[A-Z0-9]{0,4}(?:\.[A-Z0-9]+)?)\b", re.IGNORECASE),
    "AGENTE_EXECUCAO": re.compile(r"(?:Agente de Execução|Sol\(a\)\.?)[:\s]*([A-ZÁÉÍÓÚÂÊÔÃÕ][a-záéíóúâêôãõ\s]+(?:Santos|Catrau|Miranda))", re.IGNORECASE),
    "ADVOGADO": re.compile(r"(?:Dr\.|Dra\.|Mandatário)[:\s]*([A-ZÁÉÍÓÚÂÊÔÃÕ][a-záéíóúâêôãõ\s]+(?:Matos|Forra|Piscarreta|Tavares|Nabais))", re.IGNORECASE)
}

class ForensicNlpPipeline:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1500,
            ngram_range=(1, 2),
            stop_words=["de", "a", "o", "que", "e", "do", "da", "em", "um", "para", "com", "nao", "uma", "os", "no", "se", "na", "por", "mais", "as", "dos", "como", "mas", "foi", "ao", "ele", "das", "tem", "a_"]
        )
        self.corpus_files: List[Path] = []
        self.corpus_texts: List[str] = []
        self.tfidf_matrix = None

    def extract_ner(self, text: str) -> Dict[str, List[str]]:
        entities = {}
        for ent_type, pattern in NER_PATTERNS.items():
            matches = pattern.findall(text)
            clean_matches = set()
            for m in matches:
                if isinstance(m, tuple):
                    m = " ".join([x for x in m if x])
                m_str = str(m).strip()
                if m_str and len(m_str) > 1:
                    clean_matches.add(m_str)
            entities[ent_type] = sorted(list(clean_matches))
        return entities

    def load_corpus(self, limit=200):
        print(f"[*] A carregar ficheiros de texto do arquivo: {TRIBUNAL_DIR}")
        if not TRIBUNAL_DIR.exists():
            return
        
        md_files = list(TRIBUNAL_DIR.rglob("*.md"))
        for f in md_files[:limit]:
            try:
                txt = f.read_text(encoding="utf-8", errors="ignore")
                if len(txt.strip()) > 50:
                    self.corpus_files.append(f)
                    self.corpus_texts.append(txt)
            except Exception:
                pass
        print(f"[+] Total de documentos carregados para o pipeline NLP: {len(self.corpus_texts)}")

    def build_tfidf_model(self):
        if not self.corpus_texts:
            return
        print("[*] A calcular matriz TF-IDF com Scikit-Learn...")
        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus_texts)
        print(f"[+] Modelo TF-IDF treinado: {self.tfidf_matrix.shape[0]} docs x {self.tfidf_matrix.shape[1]} termos.")

    def cluster_documents(self, n_clusters=4) -> Dict[int, List[str]]:
        if self.tfidf_matrix is None or len(self.corpus_texts) < n_clusters:
            return {}
        print(f"[*] A aplicar algoritmo K-Means para {n_clusters} clusters tematicos...")
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(self.tfidf_matrix)
        
        clusters = {i: [] for i in range(n_clusters)}
        for idx, label in enumerate(labels):
            clusters[label].append(self.corpus_files[idx].name)
        return clusters

    def search_semantic_similarity(self, query_str: str, top_k=5) -> List[Dict[str, Any]]:
        if self.tfidf_matrix is None or not self.corpus_texts:
            return []
        query_vec = self.vectorizer.transform([query_str])
        sims = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = sims.argsort()[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(sims[idx])
            if score > 0.01:
                results.append({
                    "filename": self.corpus_files[idx].name,
                    "filepath": str(self.corpus_files[idx]),
                    "score_similaridade": round(score, 4),
                    "entidades_ner": self.extract_ner(self.corpus_texts[idx][:2000])
                })
        return results

    def run_pipeline(self):
        self.load_corpus(limit=250)
        self.build_tfidf_model()
        clusters = self.cluster_documents(n_clusters=4)
        
        print("\n[*] Exemplo de Pesquisa Semantica Scikit-Learn (TF-IDF + Cosine):")
        test_queries = [
            "indeferimento liminar titulo inexistente luisa santos",
            "corte de agua 2 anos retencao palmeira vistoria",
            "falta de citacao unicre certidao negativa suspensao"
        ]
        
        relatorio = {
            "total_docs_analisados": len(self.corpus_texts),
            "termos_vocabulario": len(self.vectorizer.vocabulary_) if hasattr(self.vectorizer, "vocabulary_") else 0,
            "clusters_kmeans": {f"Cluster_{k}": len(v) for k, v in clusters.items()},
            "amostras_pesquisa_semantica": {}
        }
        
        for tq in test_queries:
            matches = self.search_semantic_similarity(tq, top_k=3)
            relatorio["amostras_pesquisa_semantica"][tq] = matches
            print(f"\n-> Query: '{tq}'")
            for m in matches:
                print(f"   • [{m['score_similaridade']}] {m['filename']}")
                
        with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        print(f"\n[+] Relatorio de analise NLP/NER guardado em: {OUTPUT_REPORT}")

if __name__ == "__main__":
    nlp = ForensicNlpPipeline()
    nlp.run_pipeline()
