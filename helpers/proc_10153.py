from pathlib import Path
from typing import Dict, List, Any
from .common import everything_http_search, everything_http_count

class HelperProc10153:
    """Helper Forense Estruturante para o Processo 10153/24.6T8LSB (Acao de Despejo)."""

    NUMERO_PROCESSO = "10153/24.6T8LSB"
    TRIBUNAL = "Balcao do Arrendamento / Juizo Local Civel de Lisboa"
    TIPO_ACAO = "Procedimento Especial de Despejo / Arrendamento"
    REQUERENTE = "Senhorios / Representantes"
    REQUERIDO = "Nuno Miguel Silva Duarte / Lisbon Experience"

    QUERIES_CANONICAS = [
        '10153 <"Despejo" | "BNA" | "Arrendamento">',
        'ext:pdf;docx;md "10153/24"',
        '"Cessacao de Arrendamento" "10153"'
    ]

    FUNDAMENTOS_LEGAIS = [
        {"artigo": "Art. 1083.º do Codigo Civil", "tema": "Fundamento da resolucao do contrato de arrendamento urbano"},
        {"artigo": "Art. 15.º do Novo Regime do Arrendamento Urbano (NRAU)", "tema": "Oposicao ao procedimento especial de despejo"},
        {"artigo": "Art. 1074.º do Codigo Civil", "tema": "Obras de conservacao ordinaria e extraordinária suportadas pelo inquilino"}
    ]

    AMOSTRAS_TREINO_ML = [
        {
            "texto": "Oposicao fundamentada a cessacao do arrendamento comercial face ao pagamento adiantado de despesas e retencao por obras de remodelacao profunda.",
            "categoria": "OPOSICAO_DESPEJO_BENFEITORIAS",
            "peso_probatorio": 0.98
        },
        {
            "texto": "Falsificacao dos pressupostos de mora resolutiva quando os senhorios recusaram emitir recibos de quitação e bloquearam contas de recebimento.",
            "categoria": "RECUSA_QUITACOES_MA_FE",
            "peso_probatorio": 0.95
        }
    ]

    @classmethod
    def pesquisar_provas_ativas(cls) -> List[Dict[str, Any]]:
        query_completa = ' | '.join(cls.QUERIES_CANONICAS)
        return everything_http_search(query_completa, limit=50)

    @classmethod
    def total_documentos(cls) -> int:
        return everything_http_count('10153')
