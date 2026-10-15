from pathlib import Path
from typing import Dict, List, Any
from .common import everything_http_search, everything_http_count

class HelperProc23142:
    """Helper Forense Estruturante para o Processo 23142/24.0T8LSB (Restituicao de Dinheiros Retidos)."""

    NUMERO_PROCESSO = "23142/24.0T8LSB"
    TRIBUNAL = "Tribunal Judicial da Comarca de Lisboa - Juizo de Execucao"
    TIPO_ACAO = "Incidente de Liquidacao e Restituicao de Dinheiros Penhorados"
    VALOR_RETIDO = 35000.00
    BENEFICIARIO_RETENCAO = "Nuno Miguel Silva Duarte"

    QUERIES_CANONICAS = [
        '23142 <"35000" | "35.000" | "Restituicao">',
        'ext:pdf;docx;md "23142/24"',
        '"Dinheiros Retidos" "23142"',
        '"Agente de Execucao" "Retencao Indevida"'
    ]

    FUNDAMENTOS_LEGAIS = [
        {"artigo": "Art. 785.º do Codigo de Processo Civil", "tema": "Levantamento imediato de penhora sobre quantias indevidamente retidas"},
        {"artigo": "Art. 847.º do Codigo Civil", "tema": "Compensacao legal de creditos liquidos e exigiveis"},
        {"artigo": "Art. 205.º do Codigo Penal", "tema": "Crime de abuso de confianca por retencao ilegitima de dinheiros em deposito"}
    ]

    AMOSTRAS_TREINO_ML = [
        {
            "texto": "Pedido de restituicao imediata de 35.000 euros retidos indevidamente em conta bancaria pelo agente de execucao sem titulo executivo valido ou despacho judicial autorizador.",
            "categoria": "RESTITUICAO_DINHEIROS_RETIDOS",
            "peso_probatorio": 1.00
        },
        {
            "texto": "Reserva de jurisdicao do juiz violada pela retencao prolongada de capital sem prestacao de contas ou homologacao de partilha.",
            "categoria": "RESERVA_JURISDICAO_FINANCEIRA",
            "peso_probatorio": 0.98
        }
    ]

    @classmethod
    def pesquisar_provas_ativas(cls) -> List[Dict[str, Any]]:
        query_completa = ' | '.join(cls.QUERIES_CANONICAS)
        return everything_http_search(query_completa, limit=50)

    @classmethod
    def total_documentos(cls) -> int:
        return everything_http_count('23142')
