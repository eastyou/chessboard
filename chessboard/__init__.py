from __future__ import annotations

# chessboard：可打印的国际象棋棋盘与棋子裁剪页。
from .model import (
    PIECE_GLYPHS,
    PIECE_NAMES,
    START_FEN,
    ChessError,
    Position,
    board_from_fen,
    describe,
    empty_position,
    parse_fen,
    read_fen_file,
    square_color,
    square_name,
)
from .render import render_board, render_document, render_pieces, render_practice

__version__: str = "0.1.0"

__all__ = [
    "ChessError",
    "PIECE_GLYPHS",
    "PIECE_NAMES",
    "Position",
    "START_FEN",
    "__version__",
    "board_from_fen",
    "describe",
    "empty_position",
    "parse_fen",
    "read_fen_file",
    "render_board",
    "render_document",
    "render_pieces",
    "render_practice",
    "square_color",
    "square_name",
]
