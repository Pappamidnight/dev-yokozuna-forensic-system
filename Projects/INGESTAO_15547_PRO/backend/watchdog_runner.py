from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


def snapshot(raw_root: Path) -> dict[str, tuple[int, float]]:
    return {
        str(path): (path.stat().st_size, path.stat().st_mtime)
        for path in raw_root.rglob("*")
        if path.is_file()
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Watchdog local da fabrica de ingestao PRO.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--seconds", type=int, default=900)
    parser.add_argument("--interval", type=int, default=30)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    raw_root = root / "raw"
    start_time = time.monotonic()
    end_at = start_time + args.seconds
    last = snapshot(raw_root)

    print("==================================================================")
    print("INICIANDO SESSAO DE INGESTAO E WATCHDOG (15 MINUTOS / 900S)")
    print(f"Raiz do Projeto : {root}")
    print(f"Diretorio Raw   : {raw_root}")
    print("==================================================================")

    # Execucao inicial
    print("[INFO] Executando ciclo inicial de ingestao...")
    subprocess.run([sys.executable, str(root / "ingestao.py"), "--root", str(root)], check=False)

    cycle = 1
    while time.monotonic() < end_at:
        remaining = int(end_at - time.monotonic())
        elapsed = int(time.monotonic() - start_time)
        print(f"[STATUS] Ciclo #{cycle} | Decorrido: {elapsed}s | Restante: {remaining}s | Raw Files: {len(last)}")
        
        time.sleep(min(args.interval, max(1, remaining)))
        cycle += 1

        current = snapshot(raw_root)
        if current != last:
            print(f"[INFO] Alteracao detetada em raw/ ({len(current)} ficheiros). Reexecutando pipeline...")
            subprocess.run([sys.executable, str(root / "ingestao.py"), "--root", str(root)], check=False)
            last = current

    print("\n==================================================================")
    print("SESSAO DE 15 MINUTOS CONCLUIDA COM SUCESSO. WATCHDOG DESLIGADO.")
    print("==================================================================")


if __name__ == "__main__":
    main()
