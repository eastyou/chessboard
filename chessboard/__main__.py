from __future__ import annotations

# 模块入口：支持 python -m chessboard。
import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
