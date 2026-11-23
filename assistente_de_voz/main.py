"""Ponto de entrada do Aurora Voz."""

import sys
from pathlib import Path


PASTA_APLICATIVO = Path(__file__).resolve().parent / "aplicativo"
sys.path.insert(0, str(PASTA_APLICATIVO))

from nucleo_aurora.app import main


if __name__ == "__main__":
    main()
