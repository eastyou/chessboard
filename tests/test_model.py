from __future__ import annotations

# model 模块单元测试。
import tempfile
import unittest
from pathlib import Path

from chessboard.model import (
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


class ParseFenTests(unittest.TestCase):
    """FEN 解析与校验测试。"""

    def test_start_fen_is_white_turn(self) -> None:
        position = parse_fen(START_FEN)
        self.assertEqual(position.turn, "w")
        self.assertEqual(position.castling, "KQkq")
        self.assertEqual(position.halfmove, 0)
        self.assertEqual(position.fullmove, 1)

    def test_start_fen_board_shape(self) -> None:
        position = parse_fen(START_FEN)
        self.assertEqual(len(position.board), 8)
        for row in position.board:
            self.assertEqual(len(row), 8)

    def test_start_fen_piece_count(self) -> None:
        position = parse_fen(START_FEN)
        count = sum(1 for row in position.board for cell in row if cell)
        self.assertEqual(count, 32)

    def test_start_fen_kings(self) -> None:
        position = parse_fen(START_FEN)
        self.assertEqual(position.board[7][4], "K")
        self.assertEqual(position.board[0][4], "k")

    def test_start_fen_back_rank(self) -> None:
        position = parse_fen(START_FEN)
        self.assertEqual("".join(position.board[7]), "RNBQKBNR")
        self.assertEqual("".join(position.board[6]), "PPPPPPPP")

    def test_parse_strips_whitespace(self) -> None:
        position = parse_fen("  \n" + START_FEN + "\n  ")
        self.assertEqual(position, parse_fen(START_FEN))

    def test_parse_returns_position(self) -> None:
        position = parse_fen(START_FEN)
        self.assertIsInstance(position, Position)
        self.assertIsInstance(position.board, tuple)
        self.assertIsInstance(position.board[0], tuple)

    def test_segment_count_error(self) -> None:
        with self.assertRaises(ChessError) as ctx:
            parse_fen("8/8/8/8/8/8/8/8 w - - 0")
        self.assertIn("6 个字段", str(ctx.exception))

    def test_row_count_error(self) -> None:
        with self.assertRaises(ChessError) as ctx:
            parse_fen("8/8/8/8/8/8/8 w - - 0 1")
        self.assertIn("8 行", str(ctx.exception))

    def test_row_width_error(self) -> None:
        with self.assertRaises(ChessError) as ctx:
            parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBN w KQkq - 0 1")
        self.assertIn("8 格", str(ctx.exception))

    def test_invalid_character(self) -> None:
        with self.assertRaises(ChessError) as ctx:
            parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNX w KQkq - 0 1")
        self.assertIn("非法字符", str(ctx.exception))

    def test_two_white_kings(self) -> None:
        with self.assertRaises(ChessError) as ctx:
            parse_fen("KK6/8/8/8/8/8/8/7k w - - 0 1")
        self.assertIn("白方王", str(ctx.exception))

    def test_no_black_king(self) -> None:
        with self.assertRaises(ChessError) as ctx:
            parse_fen("K7/8/8/8/8/8/8/8 w - - 0 1")
        self.assertIn("黑方王", str(ctx.exception))

    def test_pawn_on_first_rank(self) -> None:
        with self.assertRaises(ChessError) as ctx:
            parse_fen("7k/8/8/8/8/8/8/P6K w - - 0 1")
        self.assertIn("第 1 横排", str(ctx.exception))

    def test_pawn_on_eighth_rank(self) -> None:
        with self.assertRaises(ChessError) as ctx:
            parse_fen("p6k/8/8/8/8/8/8/7K w - - 0 1")
        self.assertIn("第 8 横排", str(ctx.exception))

    def test_invalid_turn(self) -> None:
        with self.assertRaises(ChessError) as ctx:
            parse_fen(START_FEN.replace(" w ", " x "))
        self.assertIn("行棋方", str(ctx.exception))

    def test_negative_halfmove(self) -> None:
        with self.assertRaises(ChessError) as ctx:
            parse_fen("7k/8/8/8/8/8/8/K7 w - - -1 1")
        self.assertIn("半回合", str(ctx.exception))

    def test_negative_fullmove(self) -> None:
        with self.assertRaises(ChessError) as ctx:
            parse_fen("7k/8/8/8/8/8/8/K7 w - - 0 -5")
        self.assertIn("整数回合", str(ctx.exception))

    def test_non_integer_halfmove(self) -> None:
        with self.assertRaises(ChessError):
            parse_fen("7k/8/8/8/8/8/8/K7 w - - abc 1")

    def test_invalid_castling(self) -> None:
        with self.assertRaises(ChessError) as ctx:
            parse_fen("7k/8/8/8/8/8/8/K7 w KQxq - 0 1")
        self.assertIn("王车易位", str(ctx.exception))

    def test_invalid_en_passant(self) -> None:
        with self.assertRaises(ChessError) as ctx:
            parse_fen("7k/8/8/8/8/8/8/K7 w - e9 0 1")
        self.assertIn("吃过路兵", str(ctx.exception))

    def test_valid_en_passant(self) -> None:
        position = parse_fen("7k/8/8/8/8/8/8/K7 w - e3 0 1")
        self.assertEqual(position.en_passant, "e3")

    def test_round_trip(self) -> None:
        first = parse_fen(START_FEN)
        second = parse_fen(START_FEN)
        self.assertEqual(first, second)
        self.assertEqual(first.board, second.board)
        self.assertEqual(first.turn, second.turn)

    def test_board_from_fen(self) -> None:
        board = board_from_fen(START_FEN)
        self.assertEqual(board, parse_fen(START_FEN).board)
        self.assertEqual(len(board), 8)


class SquareTests(unittest.TestCase):
    """棋格命名与颜色测试。"""

    def test_square_name_corners(self) -> None:
        self.assertEqual(square_name(0, 0), "a8")
        self.assertEqual(square_name(0, 7), "h8")
        self.assertEqual(square_name(7, 0), "a1")
        self.assertEqual(square_name(7, 7), "h1")

    def test_square_name_out_of_range(self) -> None:
        for row, col in ((8, 0), (-1, 0), (0, 8), (0, -1)):
            with self.assertRaises(ChessError):
                square_name(row, col)

    def test_square_name_type_error(self) -> None:
        with self.assertRaises(ChessError):
            square_name(0.0, 1)  # type: ignore[arg-type]

    def test_square_color_corners(self) -> None:
        self.assertEqual(square_color("a1"), "dark")
        self.assertEqual(square_color("h1"), "light")
        self.assertEqual(square_color("a8"), "light")
        self.assertEqual(square_color("h8"), "dark")

    def test_square_color_alternates(self) -> None:
        for row in range(8):
            for col in range(7):
                left = square_color(square_name(row, col))
                right = square_color(square_name(row, col + 1))
                self.assertNotEqual(left, right)

    def test_square_color_invalid(self) -> None:
        for name in ("", "a", "a9", "i1", "a10", "A1"):
            with self.assertRaises(ChessError):
                square_color(name)


class DescribeTests(unittest.TestCase):
    """局面描述测试。"""

    def test_describe_start(self) -> None:
        self.assertEqual(describe(parse_fen(START_FEN)), "白方行棋，共 32 枚棋子")

    def test_describe_black_turn(self) -> None:
        position = parse_fen(START_FEN.replace(" w ", " b "))
        self.assertEqual(describe(position), "黑方行棋，共 32 枚棋子")

    def test_describe_empty(self) -> None:
        self.assertEqual(describe(empty_position()), "空棋盘，白方行棋")


class MappingTests(unittest.TestCase):
    """棋子名称与字符映射测试。"""

    def test_piece_names_mapping(self) -> None:
        self.assertEqual(len(PIECE_NAMES), 12)
        self.assertEqual(PIECE_NAMES["K"], "白王")
        self.assertEqual(PIECE_NAMES["p"], "黑兵")
        self.assertEqual(PIECE_NAMES["N"], "白马")
        for value in PIECE_NAMES.values():
            self.assertTrue(value.startswith(("白", "黑")))

    def test_piece_glyphs_unique(self) -> None:
        self.assertEqual(len(PIECE_GLYPHS), 12)
        self.assertEqual(len(set(PIECE_GLYPHS.values())), 12)
        self.assertEqual(PIECE_GLYPHS["K"], "\u2654")
        self.assertEqual(PIECE_GLYPHS["p"], "\u265f")

    def test_chess_error_is_value_error(self) -> None:
        self.assertTrue(issubclass(ChessError, ValueError))

    def test_empty_position(self) -> None:
        position = empty_position()
        self.assertEqual(len(position.board), 8)
        self.assertEqual(sum(1 for row in position.board for cell in row if cell), 0)
        self.assertEqual(position.turn, "w")


class ReadFenFileTests(unittest.TestCase):
    """FEN 文件读取测试。"""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def test_read_fen_file(self) -> None:
        path = self.root / "start.fen"
        path.write_text(START_FEN + "\n", encoding="utf-8")
        self.assertEqual(read_fen_file(path), START_FEN)

    def test_read_fen_file_bom(self) -> None:
        path = self.root / "bom.fen"
        path.write_bytes(("\ufeff" + START_FEN).encode("utf-8"))
        self.assertEqual(read_fen_file(path), START_FEN)

    def test_read_fen_file_strips(self) -> None:
        path = self.root / "spaces.fen"
        path.write_text("\n\n  " + START_FEN + "  \n\n", encoding="utf-8")
        self.assertEqual(read_fen_file(path), START_FEN)

    def test_read_fen_file_missing(self) -> None:
        with self.assertRaises(ChessError) as ctx:
            read_fen_file(self.root / "missing.fen")
        self.assertIn("找不到", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
