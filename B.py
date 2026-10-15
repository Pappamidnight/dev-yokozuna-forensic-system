import os
import json
from datetime import datetime

BASE = r'C:\ACERVO\referencias'
os.makedirs(BASE, exist_ok=True)

# entidades.json
entidades = {
    'versao': '1.0.0',
    'data': datetime.now().isoformat(),
    'processo': '15547/26.0T8LSB',
    'entidades': {
        'AUTORA': {
            'nome_correto': 'Maria Teresa Castro Bangueses Ribeiro',
            'aliases_errados': [
                'CENTENARIO DA PALMEIRA - GESTAO DE IMOVEIS, S.A.',
                'Centenario da Palmeira - Gestao de Imoveis, S.A.',
                'Centenario da Palmeira'
            ],
            'papel': 'Autora'
        },
        'REU': {
            'nome_correto': 'Nuno Miguel Silva Duarte',
            'aliases_errados': [],
            'papel': 'Reu'
        },
        'PROCURADOR': {
            'nome_correto': 'Filipe',
            'aliases_errados': [],
            'papel': 'Procurador da Autora'
        },
        'ADVOGADO_AUTORA': {
            'nome_correto': 'Antonio Neto',
            'aliases_errados': [],
            'papel': 'Advogado'
        },
        'TESTEMUNHA_ARRENDATARIO': {
            'nome_correto': 'Ingo Schallig',
            'aliases_errados': [],
            'papel': 'Arrendatario 31-5 Direito'
        }
    }
}
with open(os.path.join(BASE, 'entidades.json'), 'w', encoding='utf-8') as f:
    json.dump(entidades, f, indent=2, ensure_ascii=False)
print('[OK] entidades.json')

# processos.json
processos = {
    'versao': '1.0.0',
    'data': datetime.now().isoformat(),
    'processos': {
        '15547': {
            'numero_completo': '15547/26.0T8LSB',
            'tribunal': 'Juizo Central Civel de Lisboa',
            'juiz': 'Juiz 17',
            'papel': 'Processo principal',
            'autora': 'Maria Teresa Castro Bangueses Ribeiro',
            'reu': 'Nuno Miguel Silva Duarte'
        },
        '3719': {
            'numero_completo': '3719/24.0T8LSB',
            'papel': 'Processo relacionado',
            'relevancia': 'CRITICA',
            'nota': 'Decisao transitada em julgado'
        },
        '20203': {'numero_completo': '20203/23.0T8LSB', 'papel': 'Relacionado', 'relevancia': 'MEDIA'},
        '10153': {'numero_completo': '10153/22.0T8LSB', 'papel': 'Relacionado', 'relevancia': 'MEDIA'},
        '23142': {'numero_completo': '23142/21.0T8LSB', 'papel': 'Relacionado', 'relevancia': 'BAIXA'}
    }
}
with open(os.path.join(BASE, 'processos.json'), 'w', encoding='utf-8') as f:
    json.dump(processos, f, indent=2, ensure_ascii=False)
print('[OK] processos.json')

# normas.json
normas = {
    'versao': '1.0.0',
    'data': datetime.now().isoformat(),
    'normas': {
        'CC': {
            'nome': 'Codigo Civil',
            'artigos': {
                '227': 'Culpa na formacao de contratos',
                '334': 'Abuso de direito',
                '342': 'Onus da prova',
                '429': 'Arrendamento - forma',
                '496': 'Dano moral',
                '564': 'Dano - calculo',
                '621': 'Autoridade do caso julgado',
                '625': 'Caso julgado',
                '754': 'Direito de retencao',
                '755': 'Requisitos da retencao',
                '1038': 'Subarrendamento',
                '1311': 'Acao de reivindicacao'
            }
        },
        'CPC': {
            'nome': 'Codigo de Processo Civil',
            'artigos': {
                '297': 'Valor da causa',
                '302': 'Correcao do valor',
                '429': 'Onus da prova',
                '542': 'Ma-fe processual',
                '576': 'Excecoes',
                '621': 'Autoridade do caso julgado',
                '625': 'Caso julgado'
            }
        }
    }
}
with open(os.path.join(BASE, 'normas.json'), 'w', encoding='utf-8') as f:
    json.dump(normas, f, indent=2, ensure_ascii=False)
print('[OK] normas.json')

# documentos.json
documentos = {
    'versao': '1.0.0',
    'data': datetime.now().isoformat(),
    'documentos': {
        'SRC-15547': {
            'tipo': 'PECA_PROCESSUAL',
            'descricao': 'Peticao Inicial',
            'processo': '15547',
            'localizadores': {
                'pp. 1': 'valor da causa 65.000 EUR',
                'pp. 3-4': 'caderneta e certidao (docs. 1 e 2)',
                'p. 3': 'contrato LEA',
                'p. 9': 'alegacoes de sofrimento',
                'p. 10': 'pedido de restituicao',
                'pp. 22-24': 'doc. 3 - aditamento 05/04/2024',
                'pp. 26-30': 'doc. 4 - divida 105.633,75 EUR',
                'pp. 32-40': 'doc. 5 - contrato 31-1',
                'pp. 41-46': 'doc. 6 - Ingo Schallig',
                'pp. 47-48': 'doc. 7 - Rua Palmeira 33, 2.o',
                'pp. 49-50': 'doc. 8 - Rua Palmeira 20, 3.o',
                'p. 51': 'doc. 9 - email E-REDES'
            }
        },
        'SRC-3719': {
            'tipo': 'DECISAO_JUDICIAL',
            'descricao': 'Sentenca e Acordao',
            'processo': '3719',
            'localizadores': {
                'pp. 293-294': 'sentenca',
                'pp. 294-298': 'fundamentacao',
                'p. 295': 'rendas',
                'pp. 297-298': 'conclusoes',
                'p. 453': 'acordao',
                'pp. 454-457': 'fundamentos',
                'pp. 467-468': 'dispositivo'
            }
        },
        'SRC-WA-FILIPE': {
            'tipo': 'COMUNICACAO',
            'descricao': 'Mensagens WhatsApp Filipe',
            'localizadores': {'12-13/12/2023': 'mensagens'}
        },
        'SRC-TRANSFER': {
            'tipo': 'COMPROVATIVO_FINANCEIRO',
            'descricao': 'Captura transferencia',
            'localizadores': {'13/12/2023': 'captura'}
        }
    }
}
with open(os.path.join(BASE, 'documentos.json'), 'w', encoding='utf-8') as f:
    json.dump(documentos, f, indent=2, ensure_ascii=False)
print('[OK] documentos.json')

# refutacoes.json (referencias)
refutacoes = {
    'versao': '1.0.0',
    'data': datetime.now().isoformat(),
    'processo': '15547/26.0T8LSB',
    'autora': 'Maria Teresa Castro Bangueses Ribeiro',
    'reu': 'Nuno Miguel Silva Duarte',
    'total': 12,
    'refutacoes': {
        'AL-01': {'artigos': '1-2', 'classificacao': 'CONFIRMADA_QUANTO_A_TITULARIDADE_E_CONFIGURACAO', 'risco': 'BAIXO', 'entidades': ['AUTORA','REU'], 'documentos': ['SRC-15547','SRC-3719'], 'normas': ['CC.1311.2']},
        'AL-02': {'artigos': '3-4', 'classificacao': 'PARCIAL_CONTRATOS_PRIMITIVOS_OMISSOS', 'risco': 'MEDIO', 'entidades': ['AUTORA','REU'], 'documentos': ['SRC-15547'], 'normas': ['CPC.429','CC.1038']},
        'AL-03': {'artigos': '5-6', 'classificacao': 'CONTRADITA_PELA_CLAUSULA_F_E_PROC_3719', 'risco': 'ALTO', 'entidades': ['AUTORA','REU'], 'documentos': ['SRC-15547','SRC-3719'], 'normas': ['CC.227','CPC.625']},
        'AL-04': {'artigos': '7-8', 'classificacao': 'CONTRATOS_ESTRANHOS_AO_4_ANDAR', 'risco': 'BAIXO', 'entidades': ['AUTORA','TESTEMUNHA_ARRENDATARIO'], 'documentos': ['SRC-15547','SRC-3719'], 'normas': ['CC.342','CC.564.2']},
        'AL-05': {'artigos': '9 e 16', 'classificacao': 'FATURAS_REFEREM_OUTROS_PREDIOS_E_ANDARES', 'risco': 'CRITICO', 'entidades': ['AUTORA','REU'], 'documentos': ['SRC-15547'], 'normas': ['CPC.542']},
        'AL-06': {'artigos': '10', 'classificacao': 'CONTRADITA_POR_DECISAO_TRANSITADA_EM_3719', 'risco': 'CRITICO', 'entidades': ['AUTORA','REU','PROCURADOR'], 'documentos': ['SRC-3719','SRC-15547','SRC-WA-FILIPE','SRC-TRANSFER'], 'normas': ['CPC.625','CPC.621']},
        'AL-07': {'artigos': '11-13', 'classificacao': 'RECUSA_LEGITIMA_CONDICIONADA_A_PAGAMENTO', 'risco': 'MEDIO', 'entidades': ['AUTORA','REU','PROCURADOR'], 'documentos': ['SRC-3719'], 'normas': ['CC.334']},
        'AL-08': {'artigos': '14', 'classificacao': 'EXCECAO_PERENTORIA_DIREITO_DE_RETENCAO', 'risco': 'MEDIO', 'entidades': ['AUTORA','REU'], 'documentos': ['SRC-15547','SRC-3719'], 'normas': ['CC.1311.2','CC.754','CC.755.1.d','CPC.576.3']},
        'AL-09': {'artigos': '15', 'classificacao': 'RISCO_NAO_INDICIADO_CORTE_DE_AGUA_ABUSIVO', 'risco': 'BAIXO', 'entidades': ['AUTORA','REU'], 'documentos': ['SRC-15547','SRC-3719'], 'normas': ['CC.70']},
        'AL-10': {'artigos': '17', 'classificacao': 'ERRO_ARITMETICO_E_FALTA_DE_PROVA_DO_DANO', 'risco': 'ALTO', 'entidades': ['AUTORA','REU','TESTEMUNHA_ARRENDATARIO'], 'documentos': ['SRC-15547','SRC-3719'], 'normas': ['CC.564.2','CC.342']},
        'AL-11': {'artigos': '18-19', 'classificacao': 'MERA_ALEGACAO_SEM_SUPORTE_CLINICO', 'risco': 'BAIXO', 'entidades': ['AUTORA','REU'], 'documentos': ['SRC-15547','SRC-3719'], 'normas': ['CC.496.1']},
        'AL-12': {'artigos': 'Pedido/Valor', 'classificacao': 'SUBVALORIZACAO_DA_FRACAO_REIVINDICADA', 'risco': 'BAIXO', 'entidades': ['AUTORA'], 'documentos': ['SRC-15547'], 'normas': ['CPC.297.1','CPC.302']}
    }
}
with open(os.path.join(BASE, 'refutacoes.json'), 'w', encoding='utf-8') as f:
    json.dump(refutacoes, f, indent=2, ensure_ascii=False)
print('[OK] refutacoes.json')

# referencias.yaml
yaml_out = []
yaml_out.append('versao: "1.0.0"')
yaml_out.append(f'data: "{datetime.now().isoformat()}"')
yaml_out.append('')
yaml_out.append('processo_principal:')
yaml_out.append('  numero: "15547/26.0T8LSB"')
yaml_out.append('  tribunal: "Juizo Central Civel de Lisboa"')
yaml_out.append('  juiz: "Juiz 17"')
yaml_out.append('')
yaml_out.append('entidades:')
yaml_out.append('  autora:')
yaml_out.append('    nome: "Maria Teresa Castro Bangueses Ribeiro"')
yaml_out.append('    aliases_errados:')
yaml_out.append('      - "CENTENARIO DA PALMEIRA - GESTAO DE IMOVEIS, S.A."')
yaml_out.append('      - "Centenario da Palmeira - Gestao de Imoveis, S.A."')
yaml_out.append('      - "Centenario da Palmeira"')
yaml_out.append('  reu:')
yaml_out.append('    nome: "Nuno Miguel Silva Duarte"')
yaml_out.append('  procurador:')
yaml_out.append('    nome: "Filipe"')
yaml_out.append('  advogado:')
yaml_out.append('    nome: "Antonio Neto"')
yaml_out.append('  testemunha_arrendatario:')
yaml_out.append('    nome: "Ingo Schallig"')
yaml_out.append('')
yaml_out.append('documentos:')
for k, v in documentos['documentos'].items():
    yaml_out.append(f'  {k}:')
    yaml_out.append(f'    tipo: {v["tipo"]}')
    yaml_out.append(f'    descricao: "{v["descricao"]}"')
yaml_out.append('')
yaml_out.append('normas:')
yaml_out.append('  CC:')
yaml_out.append('    nome: "Codigo Civil"')
yaml_out.append('    artigos: [227, 334, 342, 429, 496, 564, 621, 625, 754, 755, 1038, 1311]')
yaml_out.append('  CPC:')
yaml_out.append('    nome: "Codigo de Processo Civil"')
yaml_out.append('    artigos: [297, 302, 429, 542, 576, 621, 625]')
yaml_out.append('')
yaml_out.append('refutacoes:')
for k, v in refutacoes['refutacoes'].items():
    yaml_out.append(f'  {k}:')
    yaml_out.append(f'    risco: {v["risco"]}')
    yaml_out.append(f'    classificacao: {v["classificacao"]}')
yaml_out.append('')
yaml_out.append('estatisticas:')
yaml_out.append('  total_refutacoes: 12')
yaml_out.append('  riscos:')
yaml_out.append('    CRITICO: 2')
yaml_out.append('    ALTO: 2')
yaml_out.append('    MEDIO: 3')
yaml_out.append('    BAIXO: 5')

with open(os.path.join(BASE, 'referencias.yaml'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(yaml_out))
print('[OK] referencias.yaml')

print()
print('=' * 70)
print('  REFERENCIAS CRIADAS')
print('=' * 70)
for f in sorted(os.listdir(BASE)):
    p = os.path.join(BASE, f)
    print(f'  {f} ({os.path.getsize(p)} bytes)')
print('=' * 70)
