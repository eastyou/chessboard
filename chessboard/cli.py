from __future__ import annotations

# 命令行入口：解析参数、校验输入并生成可打印 HTML。
import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from .model import (
    START_FEN,
    ChessError,
    Position,
    describe,
    empty_position,
    parse_fen,
    read_fen_file,
)
from .render import render_document


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="chessboard",
        description="生成可打印的国际象棋棋盘、棋子裁剪片与走法练习卡",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="chessboard.html",
        help="输出 HTML 文件路径（默认 chessboard.html）",
    )
    parser.add_argument("--fen", help="直接指定 FEN 局面字符串")
    parser.add_argument("--fen-file", help="从文本文件读取 FEN 局面")
    parser.add_argument("--empty", action="store_true", help="生成空棋盘")
    parser.add_argument("--no-pieces", action="store_true", help="不生成棋子裁剪片")
    parser.add_argument("--no-practice", action="store_true", help="不生成走法练习卡")
    parser.add_argument(
        "--title",
        default="国际象棋课堂讲义",
        help="页面标题（默认：国际象棋课堂讲义）",
    )
    return parser


def _resolve_position(fen: Optional[str], fen_file: Optional[str], empty: bool) -> Position:
    """根据参数选择局面，包含互斥校验。"""
    if fen is not None and fen_file is not None:
        raise ChessError("不能同时指定 --fen 与 --fen-file")
    if empty and (fen is not None or fen_file is not None):
        raise ChessError("不能同时指定 --empty 与 --fen/--fen-file")
    if fen is not None:
        return parse_fen(fen)
    if fen_file is not None:
        return parse_fen(read_fen_file(Path(fen_file)))
    if empty:
        return empty_position()
    return parse_fen(START_FEN)


def _validate_title(title: str) -> str:
    """校验标题并返回去空白后的文本。"""
    if not isinstance(title, str) or not title.strip():
        raise ChessError("标题不能为空")
    cleaned: str = title.strip()
    if len(cleaned) > 200:
        raise ChessError("标题过长，最多 200 个字符")
    return cleaned


def main(argv: Optional[Sequence[str]] = None) -> int:
    """命令行主函数，返回进程退出码。"""
    parser: argparse.ArgumentParser = build_parser()
    args: argparse.Namespace = parser.parse_args(argv)
    output: Path = Path(args.output)
    try:
        title: str = _validate_title(args.title)
        position: Position = _resolve_position(args.fen, args.fen_file, args.empty)
        document: str = render_document(
            position,
            show_pieces=not args.no_pieces,
            show_practice=not args.no_practice,
            title=title,
        )
        try:
            output.write_text(document, encoding="utf-8")
        except OSError as exc:
            reason: str = exc.strerror or str(exc)
            print(f"错误：无法写入文件 {output}（{reason}）", file=sys.stderr)
            return 1
    except ChessError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2
    print(f"已生成 {output}（{describe(position)}）")
    return 0
