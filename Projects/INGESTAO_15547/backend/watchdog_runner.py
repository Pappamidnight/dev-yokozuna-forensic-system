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
    parser = argparse.ArgumentParser(description="Watchdog local da fabrica de ingestao.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--seconds", type=int, default=900)
    parser.add_argument("--interval", type=int, default=30)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    raw_root = root / "raw"
    end_at = time.monotonic() + args.seconds
    last = snapshot(raw_root)

    subprocess.run([sys.executable, str(root / "ingestao.py"), "--root", str(root)], check=False)
    while time.monotonic() < end_at:
        time.sleep(args.interval)
        current = snapshot(raw_root)
        if current != last:
            subprocess.run([sys.executable, str(root / "ingestao.py"), "--root", str(root)], check=False)
            last = current


if __name__ == "__main__":
    main()
