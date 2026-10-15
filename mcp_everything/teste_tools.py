import sys
sys.path.insert(0, r"C:\ACERVO\mcp_everything")

print("=== TESTE 1: Versao ===")
import tools
print(tools.everything_version())

print()
print("=== TESTE 2: Contagem PDFs ===")
print(tools.everything_count("ext:pdf"))

print()
print("=== TESTE 3: Tamanho videos ===")
print(tools.everything_size("video:"))

print()
print("=== TESTE 4: Top 3 PDFs ===")
print(tools.everything_top("ext:pdf", 3))

print()
print("=== TESTE 5: Ghosts ===")
print(tools.everything_ghosts())

print()
print("=== OK: todos os testes passaram ===")
