"""Arquivo de início pra hospedagem (o MAIN do discloud.config). Em casa, o jeito é o do src/LEIA-ME.md."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from closure_bot.__main__ import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
