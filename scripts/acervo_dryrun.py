# -*- coding: utf-8 -*-
"""
acervo_sdk.py - Wrapper Python sobre o SDK do Everything
=========================================================
Chama o Everything via DLL (IPC), sem subprocess.
Requer: C:\ACERVO\bin\SDK\Everything64.dll

Uso:
    python acervo_sdk.py
    python acervo_sdk.py "ext:pdf size:>10mb"
    python acervo_sdk.py "dupe:name;size" --limit 20
"""
import os
import sys
import ctypes
import argparse
from ctypes import c_uint32, c_uint64, c_bool, c_wchar_p, c_int, POINTER
from datetime import datetime, timedelta

DLL_PATH = r"C:\ACERVO\bin\SDK\Everything64.dll"

# Sort modes
SORT_NAME = 1
SORT_PATH = 2
SORT_SIZE = 3
SORT_EXT = 4
SORT_DATE_MODIFIED = 5
SORT_DATE_CREATED = 6
SORT_DATE_ACCESSED = 7
SORT_ATTRIBUTES = 8

# Request flags
REQUEST_FILE_NAME = 0x00000001
REQUEST_PATH = 0x00000002
REQUEST_FULL_PATH_AND_FILE_NAME = 0x00000004
REQUEST_EXTENSION = 0x00000008
REQUEST_SIZE = 0x00000010
REQUEST_DATE_CREATED = 0x00000020
REQUEST_DATE_MODIFIED = 0x00000040
REQUEST_DATE_ACCESSED = 0x00000080
REQUEST_ATTRIBUTES = 0x00000100
REQUEST_FILE_LIST_FILE_NAME = 0x00000200
REQUEST_RUN_COUNT = 0x00000400
REQUEST_DATE_RUN = 0x00000800
REQUEST_DATE_RECENTLY_CHANGED = 0x00001000


def humano(b):
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} PB"


def filetime_to_dt(ft):
    if not ft:
        return None
    try:
        return datetime(1601, 1, 1) + timedelta(microseconds=ft // 10)
    except (OverflowError, OSError):
        return None


class Everything:
    def __init__(self, dll_path=DLL_PATH):
        if not os.path.isfile(dll_path):
            raise FileNotFoundError(f"DLL nao encontrada: {dll_path}")
        self.dll = ctypes.WinDLL(dll_path)
        self._setup()

    def _setup(self):
        d = self.dll
        # SetSearch
        d.Everything_SetSearchW.argtypes = [c_wchar_p]
        d.Everything_SetSearchW.restype = None
        # Query
        d.Everything_QueryW.argtypes = [c_bool]
        d.Everything_QueryW.restype = c_bool
        # NumResults
        d.Everything_GetNumResults.restype = c_uint32
        # TotalResults
        d.Everything_GetTotResults.restype = c_uint32
        # Flags
        d.Everything_SetMatchPath.argtypes = [c_bool]
        d.Everything_SetMatchCase.argtypes = [c_bool]
        d.Everything_SetMatchWholeWord.argtypes = [c_bool]
        d.Everything_SetRegex.argtypes = [c_bool]
        d.Everything_SetMax.argtypes = [c_uint32]
        d.Everything_SetOffset.argtypes = [c_uint32]
        d.Everything_SetSort.argtypes = [c_uint32]
        d.Everything_SetRequestFlags.argtypes = [c_uint32]
        # Result accessors
        d.Everything_GetResultFullPathNameW.argtypes = [c_uint32, c_wchar_p, c_uint32]
        d.Everything_GetResultSize.argtypes = [c_uint32, POINTER(c_uint64)]
        d.Everything_GetResultDateModified.argtypes = [c_uint32, POINTER(c_uint64)]
        d.Everything_GetResultDateCreated.argtypes = [c_uint32, POINTER(c_uint64)]
        d.Everything_GetResultDateAccessed.argtypes = [c_uint32, POINTER(c_uint64)]
        d.Everything_GetResultAttributes.argtypes = [c_uint32]
        d.Everything_GetResultAttributes.restype = c_uint32
        d.Everything_GetResultExtensionW.argtypes = [c_uint32, c_wchar_p, c_uint32]
        d.Everything_IsFileResult.argtypes = [c_uint32]
        d.Everything_IsFileResult.restype = c_bool
        d.Everything_IsFolderResult.argtypes = [c_uint32]
        d.Everything_IsFolderResult.restype = c_bool
        # Cleanup
        d.Everything_CleanUp.restype = None

    def search(self, query, limit=0, offset=0, sort=SORT_NAME,
               match_path=False, match_case=False, regex=False,
               request_flags=None):
        """Executa uma pesquisa e devolve lista de dicts."""
        d = self.dll

        # Configurar
        d.Everything_Reset()
        d.Everything_SetSearchW(query)
        d.Everything_SetMatchPath(match_path)
        d.Everything_SetMatchCase(match_case)
        d.Everything_SetRegex(regex)
        d.Everything_SetSort(sort)

        if request_flags is None:
            request_flags = (REQUEST_FULL_PATH_AND_FILE_NAME |
                             REQUEST_SIZE |
                             REQUEST_DATE_MODIFIED |
                             REQUEST_DATE_CREATED |
                             REQUEST_EXTENSION |
                             REQUEST_ATTRIBUTES)
        d.Everything_SetRequestFlags(request_flags)

        if limit > 0:
            d.Everything_SetMax(limit)
        if offset > 0:
            d.Everything_SetOffset(offset)

        # Executar (bloqueante)
        ok = d.Everything_QueryW(True)
        if not ok:
            return []

        n = d.Everything_GetNumResults()
        resultados = []

        for i in range(n):
            buf = ctypes.create_unicode_buffer(2048)
            d.Everything_GetResultFullPathNameW(i, buf, 2048)
            caminho = buf.value

            tam = c_uint64(0)
            d.Everything_GetResultSize(i, ctypes.byref(tam))

            dm_ft = c_uint64(0)
            d.Everything_GetResultDateModified(i, ctypes.byref(dm_ft))

            dc_ft = c_uint64(0)
            d.Everything_GetResultDateCreated(i, ctypes.byref(dc_ft))

            ext_buf = ctypes.create_unicode_buffer(32)
            d.Everything_GetResultExtensionW(i, ext_buf, 32)

            atrib = d.Everything_GetResultAttributes(i)
            e_file = bool(d.Everything_IsFileResult(i))
            e_pasta = bool(d.Everything_IsFolderResult(i))

            resultados.append({
                "caminho": caminho,
                "nome": os.path.basename(caminho),
                "tamanho": tam.value,
                "tamanho_humano": humano(tam.value),
                "dm": filetime_to_dt(dm_ft.value),
                "dc": filetime_to_dt(dc_ft.value),
                "ext": ext_buf.value,
                "atrib": atrib,
                "e_file": e_file,
                "e_pasta": e_pasta,
            })

        return resultados

    def count(self, query):
        """Conta resultados sem os listar."""
        self.dll.Everything_Reset()
        self.dll.Everything_SetSearchW(query)
        if not self.dll.Everything_QueryW(True):
            return 0
        return self.dll.Everything_GetTotResults()

    def cleanup(self):
        self.dll.Everything_CleanUp()


def main():
    parser = argparse.ArgumentParser(description="SDK Everything wrapper")
    parser.add_argument("query", nargs="?", default="", help="Query")
    parser.add_argument("--limit", type=int, default=0, help="Max resultados")
    parser.add_argument("--count", action="store_true", help="So contar")
    parser.add_argument("--regex", action="store_true", help="Regex")
    parser.add_argument("--path", action="store_true", help="Match path")
    args = parser.parse_args()

    ev = Everything()

    if args.count:
        n = ev.count(args.query)
        print(f"Total: {n:,}")
        return

    resultados = ev.search(
        args.query,
        limit=args.limit,
        regex=args.regex,
        match_path=args.path,
    )

    print()
    print("=" * 96)
    print(f"  Query: {args.query}")
    print(f"  Resultados: {len(resultados):,}")
    print("=" * 96)
    for r in resultados[:50]:
        dm = r["dm"].strftime("%Y-%m-%d") if r["dm"] else "—"
        print(f"  {r['tamanho_humano']:>12}  {dm}  {r['caminho']}")
    if len(resultados) > 50:
        print(f"  ... (+{len(resultados)-50})")
    print("=" * 96)


if __name__ == "__main__":
    main()
