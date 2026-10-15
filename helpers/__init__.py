"""
Helpers Forenses Estruturantes por Litigio — Ecossistema Acervo Forense V8
Unificacao de metadados juridicos, queries Everything HTTP canonicas e amostras de treino ML.
"""

from .common import (
    everything_http_search,
    everything_http_count,
    calcular_sha256_custodia,
    extrair_texto_ficheiro,
    executar_comando_wsl
)

from .proc_15547 import HelperProc15547
from .proc_3719 import HelperProc3719
from .proc_20203 import HelperProc20203
from .proc_10153 import HelperProc10153
from .proc_23142 import HelperProc23142
from .proc_7620 import HelperProc7620

HELPERS_POR_PROCESSO = {
    "15547": HelperProc15547,
    "3719": HelperProc3719,
    "20203": HelperProc20203,
    "10153": HelperProc10153,
    "23142": HelperProc23142,
    "7620": HelperProc7620,
}
