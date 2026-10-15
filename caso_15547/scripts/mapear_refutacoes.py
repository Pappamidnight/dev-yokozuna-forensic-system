# -*- coding: utf-8 -*-
"""mapear_refutacoes.py - Mostra as 12 alegacoes AL-01 a AL-12"""
import argparse
from collections import Counter

ALEGACOES = [
 {"id":"AL-01","artigos":"1-2","tema":"Titularidade","classificacao":"CONFIRMADA",
  "alegacao":"Autora alega propriedade do predio n.os 27-31.","suporte":["SRC-15547 pp.3-4","SRC-3719 pp.293-294"],
  "contradicao":[],"lacunas":["Conferir plantas/descricao predial"],
  "resposta":"Nao negar genericamente a titularidade. Separar propriedade registral de detencao/credito.",
  "risco":"Titularidade registral bem suportada."},
 {"id":"AL-02","artigos":"3-4","tema":"Contratos LEA","classificacao":"PARCIAL",
  "alegacao":"Autora alega contratos LEA com subarrendamento.","suporte":["SRC-15547 p.3, pp.22-24 (doc.3)"],
  "contradicao":[],"lacunas":["Contrato original LEA 31-4","Autorizacao subarrendamento"],
  "resposta":"Pedir originais, aditamentos e autorizacao escrita para cada unidade.",
  "risco":"Falta do original nao prova inexistencia."},
 {"id":"AL-03","artigos":"5-6","tema":"Revogacao 05/04/2024","classificacao":"CONTRADITA",
  "alegacao":"Revogacao em 05/04/2024, entrega devoluta.","suporte":["SRC-15547 pp.22-24","pp.26-30","SRC-3719 pp.293-294"],
  "contradicao":["Clausula F: renda direta ao titular atual desde 01/04/2024"],
  "lacunas":["Identidade do titular","Termo entrega 31-4","Recibos 01/04/2024+"],
  "resposta":"Clausula F contradiz entrega devoluta. Nao identificar titular como Nuno sem prova.",
  "risco":"Sentenca cautelar contem facto generico de entrega devoluta."},
 {"id":"AL-04","artigos":"7-8","tema":"Contratos outros andares","classificacao":"PARCIAL",
  "alegacao":"Contratos outros andares, rendas 1.125-2.500 EUR.","suporte":["SRC-15547 pp.32-40","pp.41-46"],
  "contradicao":["SRC-3719: nao indiciou arrendamento pretendido do 4.o"],
  "lacunas":["Comparabilidade","Explicacao data assinatura Ingo"],
  "resposta":"Contratos sao de outras unidades. Ingo e do 5.o Direito.",
  "risco":"Nao excluir a transferencia."},
 {"id":"AL-05","artigos":"9,16","tema":"Obras","classificacao":"CONTRADITA",
  "alegacao":"Obras nos 2.o e 3.o; ocupacao impede 31-4.","suporte":["SRC-15547 pp.47-48 (n.o 33)","pp.49-50 (n.o 20)"],
  "contradicao":["Faturas referem n.o 33 e n.o 20, nao n.o 31"],
  "lacunas":["Orcamento 31-4","Notificacao acesso"],
  "resposta":"Faturas nao identificam o 31-4. Doc. 7 e fatura, nao contrato.",
  "risco":"Morada n.o 20 a conferir."},
 {"id":"AL-06","artigos":"10","tema":"Descoberta junho 2024","classificacao":"CONTRADITA",
  "alegacao":"So soube em junho de 2024.","suporte":["SRC-3719 pp.294-298","SRC-15547 p.23 (clausula F)","SRC-WA-FILIPE","SRC-TRANSFER"],
  "contradicao":["Residencia desde 2021 + LEA sabia (indiciado em 3719)"],
  "lacunas":["Identidade titular clausula F","Recibos 01/04/2024+"],
  "resposta":"3719 e a refutacao judicial mais forte. Tribunal nao deu por indiciada a surpresa.",
  "risco":"3719 e cautelar, nao decisao final."},
 {"id":"AL-07","artigos":"11-13","tema":"Recusa/hostilidade","classificacao":"PARCIAL",
  "alegacao":"Recusou sair, atuou de forma hostil.","suporte":["SRC-3719 p.294"],
  "contradicao":["Hostilidade nao indiciada"],
  "lacunas":["Gravacao audiencia","Data exata"],
  "resposta":"Condicionamento da saida foi indiciado. Contestar data, palavras, hostilidade.",
  "risco":"Decisao reconheceu o condicionamento."},
 {"id":"AL-08","artigos":"14","tema":"Art. 1311 CC","classificacao":"CONFIRMADA",
  "alegacao":"Reivindicacao + restituicao.","suporte":["SRC-15547 pp.4,10"],
  "contradicao":[],"lacunas":["Credor/devedor/nexo"],
  "resposta":"Art. 1311 permite exigir. Sustentar detencao e retencao documentalmente.",
  "risco":"Retencao nao foi reconhecida em 3719."},
 {"id":"AL-09","artigos":"15","tema":"Ligacao eletrica","classificacao":"PARCIAL",
  "alegacao":"Ligacao clandestina + risco incendio.","suporte":["SRC-15547 p.51"],
  "contradicao":["Risco incendio nao indiciado"],
  "lacunas":["Relatorio E-REDES","Inspecao","Fotografias"],
  "resposta":"Doc. 9 so prova submissao de pedido. Nao prova origem/autoria/risco.",
  "risco":"Fonte da energia desconhecida."},
 {"id":"AL-10","artigos":"17","tema":"Renda 2.500 EUR","classificacao":"CONTRADITA",
  "alegacao":"Renda >= 2.500 EUR; 57.500 EUR danos.","suporte":["SRC-15547 pp.33-34","pp.41-43"],
  "contradicao":["24x2.500 = 60.000, nao 57.500","Contrato e do 5.o, nao do 4.o"],
  "lacunas":["Contrato 31-4","Calculo mensal"],
  "resposta":"Exigir discriminacao. Inconsistencia aritmetica e facto relevante.",
  "risco":"Diferenca nao prova inexistencia de dano."},
 {"id":"AL-11","artigos":"18-19","tema":"Danos morais","classificacao":"LACUNA",
  "alegacao":"Ansiedade/tristeza; 7.500 EUR.","suporte":["SRC-15547 p.9"],
  "contradicao":[],"lacunas":["Relatorio clinico","Deslocacoes"],
  "resposta":"Impugnar com especificidade. Nao alegar ausencia como prova.",
  "risco":"Pedido nao julgado em 3719."},
 {"id":"AL-12","artigos":"pedido/valor","tema":"Valor da causa","classificacao":"CONFIRMADA",
  "alegacao":"65.000 EUR (57.500 + 7.500).","suporte":["SRC-15547 pp.1,10"],
  "contradicao":[],"lacunas":["Discriminacao parcela patrimonial"],
  "resposta":"Soma esta correta. Inconsistencia esta na parcela mensal.",
  "risco":"Nao confundir calculo mensal com soma final."},
]

CORES = {"CONFIRMADA":"\033[92m","PARCIAL":"\033[93m",
         "CONTRADITA":"\033[91m","LACUNA":"\033[96m"}
RESET = "\033[0m"

def mostrar(a, detalhado=True):
    c = CORES.get(a["classificacao"],"")
    print(); print("="*78)
    print(f"  {a['id']}  |  Art. {a['artigos']}  |  {a['tema']}")
    print("="*78)
    print(f"  Classificacao: {c}{a['classificacao']}{RESET}")
    print(); print(f"  ALEGACAO: {a['alegacao']}")
    if not detalhado: return
    if a["suporte"]:
        print(); print("  SUPORTE:")
        for s in a["suporte"]: print(f"    - {s}")
    if a["contradicao"]:
        print(); print(f"  {c}CONTRADICAO:{RESET}")
        for x in a["contradicao"]: print(f"    - {x}")
    if a["lacunas"]:
        print(); print("  LACUNAS:")
        for l in a["lacunas"]: print(f"    - {l}")
    print(); print("  RESPOSTA SUGERIDA:"); print(f"    {a['resposta']}")
    print(); print(f"  RISCO: {a['risco']}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--al"); p.add_argument("--resumo",action="store_true")
    p.add_argument("--classificacao")
    a = p.parse_args()
    if a.resumo:
        print(); print(f"  {'ID':<7} {'CLASSIFICACAO':<14} TEMA")
        print("  " + "-"*74)
        for x in ALEGACOES:
            print(f"  {x['id']:<7} {x['classificacao']:<14} {x['tema']}")
        c = Counter(x["classificacao"] for x in ALEGACOES)
        print(); print("  Resumo:", dict(c))
        return
    if a.al:
        for x in ALEGACOES:
            if x["id"] == a.al.upper(): mostrar(x); return
        print(f"[ERRO] {a.al}"); return
    if a.classificacao:
        for x in ALEGACOES:
            if x["classificacao"] == a.classificacao: mostrar(x, False)
        return
    for x in ALEGACOES: mostrar(x)

if __name__ == "__main__": main()
