from __future__ import annotations

# 国际象棋局面模型：FEN 解析、校验与描述工具。
# 仅依赖标准库，兼容 Python 3.9+。
from dataclasses import dataclass
from pathlib import Path

START_FEN: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# 棋子中文名：大写为白方，小写为黑方。
PIECE_NAMES: dict[str, str] = {
    "K": "白王",
    "Q": "白后",
    "R": "白车",
    "B": "白象",
    "N": "白马",
    "P": "白兵",
    "k": "黑王",
    "q": "黑后",
    "r": "黑车",
    "b": "黑象",
    "n": "黑马",
    "p": "黑兵",
}

# Unicode 棋子字符：白方 ♔♕♖♗♘♙，黑方 ♚♛♜♝♞♟。
PIECE_GLYPHS: dict[str, str] = {
    "K": "\u2654",
    "Q": "\u2655",
    "R": "\u2656",
    "B": "\u2657",
    "N": "\u2658",
    "P": "\u2659",
    "k": "\u265a",
    "q": "\u265b",
    "r": "\u265c",
    "b": "\u265d",
    "n": "\u265e",
    "p": "\u265f",
}

_FILES: str = "abcdefgh"
_RANKS: str = "12345678"


class ChessError(ValueError):
    """棋局数据非法时抛出的自定义异常。"""


@dataclass(frozen=True)
class Position:
    """不可变局面。

    board[row][col] 中 row 0 表示第 8 横排，col 0 表示 a 列；
    空格用空字符串表示，其余为 FEN 棋子字母。
    """

    board: tuple[tuple[str, ...], ...]
    turn: str
    castling: str
    en_passant: str
    halfmove: int
    fullmove: int


def _parse_non_negative_int(text: str, label: str) -> int:
    """把非负整数字段转成 int，非法时抛出中文异常。"""
    if not text or any(ch not in "0123456789" for ch in text):
        raise ChessError(f"{label}必须为非负整数，实际为 {text!r}")
    return int(text)


def _square_to_row_col(name: str) -> tuple[int, int]:
    """把 a1..h8 转成 (row, col)，非法格名抛异常。"""
    if not isinstance(name, str) or len(name) != 2:
        raise ChessError(f"棋格名称非法：{name!r}（应为 a1..h8）")
    file_char: str = name[0]
    rank_char: str = name[1]
    if file_char not in _FILES or rank_char not in _RANKS:
        raise ChessError(f"棋格名称非法：{name!r}（应为 a1..h8）")
    return 8 - int(rank_char), _FILES.index(file_char)


def parse_fen(fen: str) -> Position:
    """解析并校验 FEN，返回不可变 Position。"""
    if not isinstance(fen, str):
        raise ChessError("FEN 必须是字符串")
    text: str = fen.strip()
    if not text:
        raise ChessError("FEN 不能为空")
    fields: list[str] = text.split()
    if len(fields) != 6:
        raise ChessError(f"FEN 应包含 6 个字段，实际为 {len(fields)} 个")

    placement: str = fields[0]
    turn: str = fields[1]
    castling: str = fields[2]
    en_passant: str = fields[3]

    rows: list[str] = placement.split("/")
    if len(rows) != 8:
        raise ChessError(f"FEN 棋盘应为 8 行，实际为 {len(rows)} 行")

    board: list[list[str]] = []
    for row_index, row_text in enumerate(rows):
        cells: list[str] = []
        for char in row_text:
            if char in "12345678":
                cells.extend([""] * int(char))
            elif char in PIECE_GLYPHS:
                cells.append(char)
            else:
                raise ChessError(
                    f"第 {row_index + 1} 行出现非法字符 {char!r}（仅允许 1-8 与棋子字母）"
                )
        if len(cells) != 8:
            raise ChessError(f"第 {row_index + 1} 行应有 8 格，实际为 {len(cells)} 格")
        board.append(cells)

    white_kings: int = sum(1 for row in board for cell in row if cell == "K")
    black_kings: int = sum(1 for row in board for cell in row if cell == "k")
    if white_kings != 1:
        raise ChessError(f"白方王的数量应为 1，实际为 {white_kings}")
    if black_kings != 1:
        raise ChessError(f"黑方王的数量应为 1，实际为 {black_kings}")

    for col, cell in enumerate(board[0]):
        if cell in ("P", "p"):
            raise ChessError(f"兵不能位于第 8 横排（{square_name(0, col)}）")
    for col, cell in enumerate(board[7]):
        if cell in ("P", "p"):
            raise ChessError(f"兵不能位于第 1 横排（{square_name(7, col)}）")

    if turn not in ("w", "b"):
        raise ChessError(f"行棋方必须为 w 或 b，实际为 {turn!r}")

    if castling != "-":
        if (
            not castling
            or any(ch not in "KQkq" for ch in castling)
            or len(set(castling)) != len(castling)
        ):
            raise ChessError(f"王车易位字段非法：{castling!r}")

    if en_passant != "-":
        try:
            _square_to_row_col(en_passant)
        except ChessError as exc:
            raise ChessError(f"吃过路兵目标格非法：{en_passant!r}") from exc

    halfmove: int = _parse_non_negative_int(fields[4], "半回合计数")
    fullmove: int = _parse_non_negative_int(fields[5], "整数回合数")

    frozen_board: tuple[tuple[str, ...], ...] = tuple(tuple(row) for row in board)
    return Position(
        board=frozen_board,
        turn=turn,
        castling=castling,
        en_passant=en_passant,
        halfmove=halfmove,
        fullmove=fullmove,
    )


def read_fen_file(path: Path) -> str:
    """读取 FEN 文件，自动处理 BOM 与编码回退，返回去空白后的文本。"""
    file_path = Path(path)
    for encoding in ("utf-8-sig", "utf-8", "gbk"):
        try:
            content: str = file_path.read_text(encoding=encoding)
        except FileNotFoundError as exc:
            raise ChessError(f"找不到 FEN 文件：{file_path}") from exc
        except UnicodeDecodeError:
            continue
        except OSError as exc:
            reason: str = exc.strerror or str(exc)
            raise ChessError(f"读取 FEN 文件失败：{file_path}（{reason}）") from exc
        return content.strip()
    raise ChessError(f"无法识别 FEN 文件编码：{file_path}")


def square_name(row: int, col: int) -> str:
    """把行列表转成格名，row 0 为第 8 横排，col 0 为 a 列。"""
    if not isinstance(row, int) or not isinstance(col, int):
        raise ChessError("行列必须为整数")
    if not 0 <= row <= 7 or not 0 <= col <= 7:
        raise ChessError(f"行列越界：row={row}, col={col}")
    return f"{_FILES[col]}{8 - row}"


def square_color(name: str) -> str:
    """返回棋格颜色：light 或 dark。"""
    row, col = _square_to_row_col(name)
    # a1 为深色：列索引 + 横排号 为奇数时是深色。
    return "dark" if (col + (8 - row)) % 2 == 1 else "light"


def board_from_fen(fen: str) -> tuple[tuple[str, ...], ...]:
    """便捷函数：直接返回 FEN 对应的棋盘元组。"""
    return parse_fen(fen).board


def empty_position() -> Position:
    """构造空棋盘局面（--empty 使用，跳过王数量校验）。"""
    empty_row: tuple[str, ...] = tuple("" for _ in range(8))
    return Position(
        board=tuple(empty_row for _ in range(8)),
        turn="w",
        castling="-",
        en_passant="-",
        halfmove=0,
        fullmove=1,
    )


def describe(position: Position) -> str:
    """用一句中文描述局面，例如「白方行棋，共 32 枚棋子」。"""
    count: int = sum(1 for row in position.board for cell in row if cell)
    side: str = "白方" if position.turn == "w" else "黑方"
    if count == 0:
        return f"空棋盘，{side}行棋"
    return f"{side}行棋，共 {count} 枚棋子"
