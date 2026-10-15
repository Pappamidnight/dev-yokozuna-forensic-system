from pathlib import Path
from typing import Dict, List, Any
from .common import everything_http_search, everything_http_count

class HelperProc7620:
    """Helper Forense Estruturante para o Inquerito / Investigacao Fiscal 7620/24."""

    NUMERO_PROCESSO = "7620/24"
    ENTIDADE_INVESTIGADORA = "DIAP de Lisboa / Autoridade Tributaria e Aduaneira"
    TIPO_PROCESSO = "Inquerito Crime / Fraude Fiscal Qualificada"
    ALVOS = ["Manuel Varela", "Joao Pedro Carvalho", "Sociedades Instrumentais"]

    QUERIES_CANONICAS = [
        '7620 <"Fraude" | "Varela" | "Simulacao">',
        'ext:pdf;docx;md "7620/24"',
        '"Titulo Centenario" "Fraude"',
        '"Fatura Falsa" "Tributaria"'
    ]

    FUNDAMENTOS_LEGAIS = [
        {"artigo": "Art. 103.º e 104.º do RGIT", "tema": "Crime de fraude fiscal qualificada por utilizacao de faturas falsas e simulacoes"},
        {"artigo": "Art. 240.º do Codigo Civil", "tema": "Nulidade absoluta do negocio juridico simulado por conluio fraudulento"},
        {"artigo": "Art. 256.º do Codigo Penal", "tema": "Falsificacao de documentos autenticos e titulos de posse"}
    ]

    AMOSTRAS_TREINO_ML = [
        {
            "texto": "Simulacao de titulos de posse centenarios e utilizacao fraudulenta de faturas forjadas por Manuel Varela para instruir acoes de despejo e esquivar impostos de transmissao.",
            "categoria": "FRAUDE_FISCAL_SIMULACAO",
            "peso_probatorio": 1.00
        },
        {
            "texto": "Relatorio de cruzamento bancario revelando fluxos financeiros paralelos e emissao de documentos com datas adulteradas para lesar credores legitimos.",
            "categoria": "CRUZAMENTO_BANCARIO_FLUXOS",
            "peso_probatorio": 0.98
        }
    ]

    @classmethod
    def pesquisar_provas_ativas(cls) -> List[Dict[str, Any]]:
        query_completa = ' | '.join(cls.QUERIES_CANONICAS)
        return everything_http_search(query_completa, limit=50)

    @classmethod
    def total_documentos(cls) -> int:
        return everything_http_count('7620')
