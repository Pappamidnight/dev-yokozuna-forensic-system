from pathlib import Path
from typing import Dict, List, Any
from .common import everything_http_search, everything_http_count

class HelperProc3719:
    """Helper Forense Estruturante para o Processo 3719/24.3T8LSB (Procedimento Cautelar)."""

    NUMERO_PROCESSO = "3719/24.3T8LSB"
    TRIBUNAL = "Tribunal da Relacao de Lisboa / Juizo Local Civel de Lisboa"
    TIPO_ACAO = "Procedimento Cautelar Comum / Restituicao Provisoria de Posse"
    REQUERENTE = "Maria Teresa da Silva Ribeiro"
    REQUERIDO = "Nuno Miguel Silva Duarte"

    QUERIES_CANONICAS = [
        '3719 "Relacao de Lisboa"',
        'ext:pdf;docx;md "3719/24"',
        '"Contra-Alegacoes" "3719"',
        '"Providencia Cautelar" "Carnide"'
    ]

    FUNDAMENTOS_LEGAIS = [
        {"artigo": "Art. 368.º do Codigo de Processo Civil", "tema": "Caducidade e improcedencia de providencias cautelares sem periculum in mora"},
        {"artigo": "Art. 378.º do Codigo de Processo Civil", "tema": "Restituicao provisoria de posse e inversao do contencioso"},
        {"artigo": "Art. 640.º do Codigo de Processo Civil", "tema": "Impugnacao da materia de facto em sede de recurso para a Relacao"}
    ]

    AMOSTRAS_TREINO_ML = [
        {
            "texto": "Recurso de apelacao contra a decisao da providencia cautelar com comprovacao de que o Reu sempre possuiu titulo legitimo de ocupacao e benfeitorias.",
            "categoria": "RECURSO_RELACAO_PROVISORIA",
            "peso_probatorio": 0.98
        },
        {
            "texto": "Inexistencia de esbulho violento uma vez que a posse foi transmitida consensualmente e exercida de forma publica, pacifica e continuada.",
            "categoria": "INEXISTENCIA_ESBULHO_VIOLENTO",
            "peso_probatorio": 0.95
        }
    ]

    @classmethod
    def pesquisar_provas_ativas(cls) -> List[Dict[str, Any]]:
        query_completa = ' | '.join(cls.QUERIES_CANONICAS)
        return everything_http_search(query_completa, limit=50)

    @classmethod
    def total_documentos(cls) -> int:
        return everything_http_count('3719')
