# -*- coding: utf-8 -*-
"""sdk_client.py - Cliente SDK (DLL Everything via ctypes)"""
import os
import json
import ctypes
from ctypes import c_uint32, c_uint64, c_bool, c_wchar_p, POINTER
from datetime import datetime, timedelta

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

DLL = CONFIG["sdk_dll"]
INST = CONFIG["instance"]


class EverythingSDK:
    def __init__(self):
        self.disponivel = False
        if not os.path.isfile(DLL):
            return
        try:
            self.dll = ctypes.WinDLL(DLL)
            self._setup()
            self.disponivel = True
        except OSError:
            self.disponivel = False

    def _setup(self):
        d = self.dll
        d.Everything_SetSearchW.argtypes = [c_wchar_p]
        d.Everything_SetInstanceNameW.argtypes = [c_wchar_p]
        d.Everything_QueryW.argtypes = [c_bool]
        d.Everything_QueryW.restype = c_bool
        d.Everything_GetNumResults.restype = c_uint32
        d.Everything_GetTotResults.restype = c_uint32
        d.Everything_SetMax.argtypes = [c_uint32]
        d.Everything_SetSort.argtypes = [c_uint32]
        d.Everything_SetRequestFlags.argtypes = [c_uint32]
        d.Everything_GetResultFullPathNameW.argtypes = [c_uint32, c_wchar_p, c_uint32]
        d.Everything_GetResultSize.argtypes = [c_uint32, POINTER(c_uint64)]
        d.Everything_GetResultDateModified.argtypes = [c_uint32, POINTER(c_uint64)]
        d.Everything_GetResultDateCreated.argtypes = [c_uint32, POINTER(c_uint64)]
        d.Everything_GetResultExtensionW.argtypes = [c_uint32, c_wchar_p, c_uint32]
        d.Everything_IsFileResult.argtypes = [c_uint32]
        d.Everything_IsFileResult.restype = c_bool
        d.Everything_CleanUp.restype = None

        if INST:
            try:
                d.Everything_SetInstanceNameW(INST)
            except Exception:
                pass

    def search(self, query: str, limit: int = 100) -> list:
        if not self.disponivel:
            return []
        d = self.dll
        d.Everything_Reset()
        d.Everything_SetSearchW(query)
        d.Everything_SetRequestFlags(0x04 | 0x10 | 0x40 | 0x20 | 0x08)
        if limit > 0:
            d.Everything_SetMax(limit)
        if not d.Everything_QueryW(True):
            return []
        n = d.Everything_GetNumResults()
        res = []
        for i in range(n):
            buf = ctypes.create_unicode_buffer(2048)
            d.Everything_GetResultFullPathNameW(i, buf, 2048)
            caminho = buf.value

            tam = c_uint64(0)
            d.Everything_GetResultSize(i, ctypes.byref(tam))
            dm = c_uint64(0)
            d.Everything_GetResultDateModified(i, ctypes.byref(dm))
            ext = ctypes.create_unicode_buffer(32)
            d.Everything_GetResultExtensionW(i, ext, 32)

            res.append({
                "path": caminho,
                "name": os.path.basename(caminho),
                "size": tam.value,
                "extension": ext.value,
                "is_file": bool(d.Everything_IsFileResult(i)),
                "date_modified": self._filetime_to_dt(dm.value),
            })
        return res

    def count(self, query: str) -> int:
        if not self.disponivel:
            return 0
        d = self.dll
        d.Everything_Reset()
        d.Everything_SetSearchW(query)
        if not d.Everything_QueryW(True):
            return 0
        return d.Everything_GetTotResults()

    @staticmethod
    def _filetime_to_dt(ft):
        if not ft:
            return None
        try:
            return (datetime(1601, 1, 1) + timedelta(microseconds=ft // 10)).isoformat()
        except (OverflowError, OSError):
            return None

    def cleanup(self):
        if self.disponivel:
            try:
                self.dll.Everything_CleanUp()
            except Exception:
                pass
