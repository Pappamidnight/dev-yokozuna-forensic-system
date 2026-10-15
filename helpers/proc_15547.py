from pathlib import Path
from typing import Dict, List, Any
from .common import everything_http_search, everything_http_count, calcular_sha256_custodia

class HelperProc15547:
    """Helper Forense Estruturante para o Processo 15547/26.0T8LSB."""

    NUMERO_PROCESSO = "15547/26.0T8LSB"
    TRIBUNAL = "Tribunal Judicial da Comarca de Lisboa - Juizo Local Civel de Lisboa - Juiz 14"
    AUTORA = "Maria Teresa da Silva Ribeiro"
    PROCURADOR_AUTORA = "Joao Pedro Carvalho"
    REU = "Nuno Miguel Silva Duarte"
    VALOR_RETENCAO = 1113840.74
    VALOR_FATURA_LEA = 80000.00
    IMOVEL = "Rua da Palmeira n.ºs 27 a 31, 4.º andar, Carnide, Lisboa"

    QUERIES_CANONICAS = [
        '15547 <"Palmeira" | "Carnide" | "Retencao">',
        'ext:pdf;docx;md "15547/26"',
        '"Direito de Retencao" "15547"',
        '"Fatura" "80.000" "Lisbon Experience"',
        '"Altar" "Memorias" "Carnide"'
    ]

    FUNDAMENTOS_LEGAIS = [
        {"artigo": "Art. 754.º do Codigo Civil", "tema": "Direito de Retencao por despesas necessarias e uteis"},
        {"artigo": "Art. 759.º do Codigo Civil", "tema": "Prevalencia do direito de retencao sobre a hipoteca e reivindicacao"},
        {"artigo": "Art. 1273.º do Codigo Civil", "tema": "Indemnizacao por benfeitorias necessarias e levantamento de uteis"},
        {"artigo": "Art. 1311.º, n.º 2 do Codigo Civil", "tema": "Recusa legitima de restituicao na acao de reivindicacao"},
        {"artigo": "Art. 573.º do Codigo de Processo Civil", "tema": "Principio da concentracao da defesa na contestacao"},
        {"artigo": "Art. 266.º do Codigo de Processo Civil", "tema": "Admissibilidade formal do pedido reconvencional"}
    ]

    AMOSTRAS_TREINO_ML = [
        {
            "texto": "Direito de retencao pelo credito de 1.113.840,74 euros decorrente de obras de conservacao profunda, substituicao do quadro eletrico e reparacoes estruturais no imovel da Rua da Palmeira.",
            "categoria": "DIREITO_RETENCAO_BENFEITORIAS",
            "peso_probatorio": 1.00
        },
        {
            "texto": "A Autora alega ser legitima proprietaria sem individualizacao das fracoes em regime de propriedade total sem propriedade horizontal instituida formalmente.",
            "categoria": "PROPRIEDADE_TOTAL_INDETERMINACAO",
            "peso_probatorio": 0.98
        },
        {
            "texto": "Presenca continuada, vivencia e custodia no imovel comprovada desde agosto de 2018 com o abrigo de animais de companhia e gestao diaria ininterrupta.",
            "categoria": "PROVA_RESIDENCIA_MEMORIAS",
            "peso_probatorio": 0.95
        },
        {
            "texto": "Corte violento e ilicito do fornecimento de agua potavel perpetrado em marco de 2024 pelo procurador Joao Pedro visando a coacao para desocupacao sem ordem judicial.",
            "categoria": "CRIME_COACAO_CORTE_AGUA",
            "peso_probatorio": 0.98
        }
    ]

    @classmethod
    def pesquisar_provas_ativas(cls) -> List[Dict[str, Any]]:
        query_completa = ' | '.join(cls.QUERIES_CANONICAS)
        return everything_http_search(query_completa, limit=50)

    @classmethod
    def total_documentos(cls) -> int:
        return everything_http_count('15547')
