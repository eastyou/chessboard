from __future__ import annotations

# cli 模块单元测试。
import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path

from chessboard.cli import main
from chessboard.model import START_FEN


class CliTests(unittest.TestCase):
    """命令行行为测试。"""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def run_cli(self, argv: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_default_output(self) -> None:
        old_cwd = os.getcwd()
        os.chdir(self.root)
        try:
            code, stdout, stderr = self.run_cli([])
            target = self.root / "chessboard.html"
            self.assertEqual(code, 0)
            self.assertEqual(stderr, "")
            self.assertTrue(target.exists())
            self.assertIn("已生成", stdout)
        finally:
            os.chdir(old_cwd)

    def test_custom_output(self) -> None:
        target = self.root / "custom.html"
        code, _, _ = self.run_cli(["-o", str(target)])
        self.assertEqual(code, 0)
        self.assertTrue(target.exists())
        self.assertIn("<!DOCTYPE html>", target.read_text(encoding="utf-8"))

    def test_success_message(self) -> None:
        target = self.root / "out.html"
        code, stdout, _ = self.run_cli(["-o", str(target), "--fen", START_FEN])
        self.assertEqual(code, 0)
        self.assertIn("已生成", stdout)
        self.assertIn("白方行棋，共 32 枚棋子", stdout)

    def test_bad_fen_returns_2(self) -> None:
        target = self.root / "bad.html"
        code, _, stderr = self.run_cli(["-o", str(target), "--fen", "not-a-fen"])
        self.assertEqual(code, 2)
        self.assertIn("错误", stderr)
        self.assertFalse(target.exists())

    def test_bad_fen_message_chinese(self) -> None:
        code, _, stderr = self.run_cli(["-o", str(self.root / "x.html"), "--fen", "8/8/8/8/8/8/8/8 w - - 0 1"])
        self.assertEqual(code, 2)
        self.assertIn("王", stderr)

    def test_conflict_fen_and_file(self) -> None:
        code, _, stderr = self.run_cli(
            ["-o", str(self.root / "x.html"), "--fen", START_FEN, "--fen-file", str(self.root / "a.fen")]
        )
        self.assertEqual(code, 2)
        self.assertIn("--fen", stderr)

    def test_empty_flag(self) -> None:
        target = self.root / "empty.html"
        code, stdout, _ = self.run_cli(["-o", str(target), "--empty"])
        self.assertEqual(code, 0)
        self.assertIn("空棋盘", stdout)
        content = target.read_text(encoding="utf-8")
        self.assertNotIn('<span class="piece">', content)
        self.assertEqual(content.count('class="sq '), 64)

    def test_empty_conflict_with_fen(self) -> None:
        code, _, stderr = self.run_cli(
            ["-o", str(self.root / "x.html"), "--empty", "--fen", START_FEN]
        )
        self.assertEqual(code, 2)
        self.assertIn("--empty", stderr)

    def test_fen_file(self) -> None:
        fen_path = self.root / "start.fen"
        fen_path.write_text(START_FEN + "\n", encoding="utf-8")
        target = self.root / "from-file.html"
        code, stdout, _ = self.run_cli(["-o", str(target), "--fen-file", str(fen_path)])
        self.assertEqual(code, 0)
        self.assertIn("32 枚棋子", stdout)
        self.assertTrue(target.exists())

    def test_missing_fen_file(self) -> None:
        code, _, stderr = self.run_cli(
            ["-o", str(self.root / "x.html"), "--fen-file", str(self.root / "missing.fen")]
        )
        self.assertEqual(code, 2)
        self.assertIn("找不到", stderr)

    def test_write_failure_returns_1(self) -> None:
        target = self.root / "no-such-dir" / "out.html"
        code, _, stderr = self.run_cli(["-o", str(target), "--empty"])
        self.assertEqual(code, 1)
        self.assertIn("无法写入", stderr)

    def test_no_pieces_flag(self) -> None:
        target = self.root / "board-only.html"
        code, _, _ = self.run_cli(["-o", str(target), "--no-pieces"])
        self.assertEqual(code, 0)
        content = target.read_text(encoding="utf-8")
        self.assertNotIn('class="piece-disc', content)
        self.assertIn("参考答案", content)

    def test_no_practice_flag(self) -> None:
        target = self.root / "no-practice.html"
        code, _, _ = self.run_cli(["-o", str(target), "--no-practice"])
        self.assertEqual(code, 0)
        content = target.read_text(encoding="utf-8")
        self.assertNotIn("参考答案", content)
        self.assertIn('class="piece-disc', content)

    def test_title_escaping(self) -> None:
        target = self.root / "title.html"
        code, _, _ = self.run_cli(["-o", str(target), "--title", "<b>第 1 课</b>", "--empty"])
        self.assertEqual(code, 0)
        content = target.read_text(encoding="utf-8")
        self.assertNotIn("<b>第 1 课</b>", content)
        self.assertIn("&lt;b&gt;第 1 课&lt;/b&gt;", content)

    def test_empty_title_returns_2(self) -> None:
        code, _, stderr = self.run_cli(["-o", str(self.root / "x.html"), "--title", "   "])
        self.assertEqual(code, 2)
        self.assertIn("标题", stderr)

    def test_output_contains_pieces(self) -> None:
        target = self.root / "pieces.html"
        code, _, _ = self.run_cli(["-o", str(target)])
        self.assertEqual(code, 0)
        content = target.read_text(encoding="utf-8")
        for glyph in ("♔", "♟"):
            self.assertIn(glyph, content)


if __name__ == "__main__":
    unittest.main()
