from pathlib import Path
from typing import Dict, List, Any
from .common import everything_http_search, everything_http_count

class HelperProc20203:
    """Helper Forense Estruturante para o Processo 20203/24.0T8LSB (Execucao e Nulidade de Citacao)."""

    NUMERO_PROCESSO = "20203/24.0T8LSB"
    TRIBUNAL = "Juizo de Execucao de Lisboa"
    TIPO_ACAO = "Acao Executiva / Embargos de Executado"
    EXEQUENTE = "Manuel Varela / Cedentes Diversos"
    EXECUTADO = "Nuno Miguel Silva Duarte"

    QUERIES_CANONICAS = [
        '20203 <"Nulidade" | "Citacao" | "Execucao">',
        'ext:pdf;docx;md "20203/24"',
        '"Embargos" "20203"'
    ]

    FUNDAMENTOS_LEGAIS = [
        {"artigo": "Art. 188.º do Codigo de Processo Civil", "tema": "Nulidade insanavel da citacao por falta absoluta de conhecimento pessoal"},
        {"artigo": "Art. 191.º do Codigo de Processo Civil", "tema": "Arguicao da nulidade da citacao a todo o tempo antes do transito"},
        {"artigo": "Art. 728.º do Codigo de Processo Civil", "tema": "Oposicao a execucao por embargos baseada em titulo nulo"}
    ]

    AMOSTRAS_TREINO_ML = [
        {
            "texto": "Nulidade insanavel da citacao do executado, porquanto a carta postal foi enviada para morada onde o reu ja nao residia, resultando em certidao negativa omitida nos autos.",
            "categoria": "NULIDADE_CITACAO_INOPONIBILIDADE",
            "peso_probatorio": 1.00
        },
        {
            "texto": "Inexistencia de titulo executivo valido e oposicao por embargos com fundamento na extincao da divida por compensacao de creditos.",
            "categoria": "OPOSICAO_EMBARGOS_COMPENSACAO",
            "peso_probatorio": 0.95
        }
    ]

    @classmethod
    def pesquisar_provas_ativas(cls) -> List[Dict[str, Any]]:
        query_completa = ' | '.join(cls.QUERIES_CANONICAS)
        return everything_http_search(query_completa, limit=50)

    @classmethod
    def total_documentos(cls) -> int:
        return everything_http_count('20203')
