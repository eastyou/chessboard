from __future__ import annotations

# render 模块单元测试。
import unittest

from chessboard.model import START_FEN, empty_position, parse_fen
from chessboard.render import (
    render_board,
    render_document,
    render_pieces,
    render_practice,
)


class BoardRenderTests(unittest.TestCase):
    """棋盘渲染测试。"""

    def setUp(self) -> None:
        self.position = parse_fen(START_FEN)
        self.html = render_board(self.position)

    def test_board_has_64_squares(self) -> None:
        self.assertEqual(self.html.count('class="sq '), 64)

    def test_board_coordinates_present(self) -> None:
        for file_char in "abcdefgh":
            self.assertIn(f'<td class="coord">{file_char}</td>', self.html)
        for rank in "12345678":
            self.assertIn(f'<td class="coord">{rank}</td>', self.html)

    def test_board_coordinates_can_be_hidden(self) -> None:
        html_text = render_board(self.position, show_coordinates=False)
        self.assertNotIn('class="coord"', html_text)
        self.assertEqual(html_text.count('class="sq '), 64)

    def test_board_contains_piece_glyphs(self) -> None:
        for glyph in ("♔", "♕", "♖", "♗", "♘", "♙", "♚", "♛", "♜", "♝", "♞", "♟"):
            self.assertIn(glyph, self.html)

    def test_board_colors(self) -> None:
        self.assertIn("#f0d9b5", self.html)
        self.assertIn("#b58863", self.html)
        self.assertIn('class="sq light"', self.html)
        self.assertIn('class="sq dark"', self.html)

    def test_board_legend(self) -> None:
        self.assertIn("图例", self.html)
        self.assertIn("白方行棋，共 32 枚棋子", self.html)

    def test_board_title_escaped(self) -> None:
        html_text = render_board(self.position, title="<b>棋盘</b>")
        self.assertNotIn("<b>棋盘</b>", html_text)
        self.assertIn("&lt;b&gt;棋盘&lt;/b&gt;", html_text)

    def test_board_a4_css(self) -> None:
        self.assertIn("@page { size: A4; margin: 0 }", self.html)
        self.assertIn(
            ".page { width: 210mm; min-height: 297mm; padding: 12mm; box-sizing: border-box; overflow: hidden",
            self.html,
        )

    def test_board_square_size_within_limit(self) -> None:
        self.assertIn("width: 19mm", self.html)
        self.assertIn("height: 19mm", self.html)

    def test_empty_board_has_no_pieces(self) -> None:
        html_text = render_board(empty_position())
        self.assertEqual(html_text.count('class="sq '), 64)
        self.assertNotIn('<span class="piece">', html_text)
        self.assertIn("空棋盘", html_text)

    def test_board_is_document(self) -> None:
        self.assertTrue(self.html.startswith("<!DOCTYPE html>"))
        self.assertIn('<html lang="zh-CN">', self.html)
        self.assertIn("</html>", self.html)


class PiecesRenderTests(unittest.TestCase):
    """棋子裁剪片测试。"""

    def setUp(self) -> None:
        self.html = render_pieces()

    def test_pieces_disc_count(self) -> None:
        self.assertEqual(self.html.count('class="piece-disc'), 24)

    def test_pieces_chinese_names(self) -> None:
        for name in ("白王", "白后", "白车", "白象", "白马", "白兵", "黑王", "黑兵"):
            self.assertIn(name, self.html)

    def test_pieces_cut_line_css(self) -> None:
        self.assertIn("22mm", self.html)
        self.assertIn("dashed", self.html)
        self.assertIn("border-radius: 50%", self.html)

    def test_pieces_title_escaped(self) -> None:
        html_text = render_pieces(title="<i>裁剪</i>")
        self.assertNotIn("<i>裁剪</i>", html_text)
        self.assertIn("&lt;i&gt;裁剪&lt;/i&gt;", html_text)


class PracticeRenderTests(unittest.TestCase):
    """走法练习卡测试。"""

    def setUp(self) -> None:
        self.html = render_practice()

    def test_practice_questions(self) -> None:
        self.assertIn("a1、h1、a8、h8", self.html)
        self.assertIn("白马位于 b1", self.html)
        self.assertIn("白兵与黑兵", self.html)

    def test_practice_has_answer_page(self) -> None:
        self.assertIn("参考答案", self.html)
        self.assertIn('class="page answer-page"', self.html)
        self.assertEqual(self.html.count('<section class="page'), 2)
        self.assertIn("a1 深色，h1 浅色", self.html)

    def test_practice_title_escaped(self) -> None:
        html_text = render_practice(title="<u>练习</u>")
        self.assertNotIn("<u>练习</u>", html_text)
        self.assertIn("&lt;u&gt;练习&lt;/u&gt;", html_text)


class DocumentRenderTests(unittest.TestCase):
    """组合文档测试。"""

    def test_render_document_full(self) -> None:
        html_text = render_document(parse_fen(START_FEN))
        self.assertEqual(html_text.count('class="sq '), 64)
        self.assertEqual(html_text.count('class="piece-disc'), 24)
        self.assertIn("参考答案", html_text)
        self.assertEqual(html_text.count('<section class="page'), 4)

    def test_render_document_minimal(self) -> None:
        html_text = render_document(
            parse_fen(START_FEN), show_pieces=False, show_practice=False
        )
        self.assertNotIn('class="piece-disc', html_text)
        self.assertNotIn("参考答案", html_text)
        self.assertEqual(html_text.count('<section class="page'), 1)

    def test_render_document_escapes_title(self) -> None:
        html_text = render_document(parse_fen(START_FEN), title="<script>alert(1)</script>")
        self.assertNotIn("<script>alert(1)</script>", html_text)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html_text)


if __name__ == "__main__":
    unittest.main()
