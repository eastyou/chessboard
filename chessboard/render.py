from __future__ import annotations

# HTML 渲染：A4 棋盘页、棋子裁剪片与走法练习卡。
import html

from .model import PIECE_GLYPHS, PIECE_NAMES, Position, describe, square_color, square_name

_LIGHT: str = "#f0d9b5"
_DARK: str = "#b58863"

# 基础样式：A4 页面、棋盘配色、裁剪片与练习卡排版。
_STYLE: str = """
@page { size: A4; margin: 0 }
* { box-sizing: border-box }
html, body { margin: 0; padding: 0 }
body {
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  color: #222;
  background: #fff;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
.page { width: 210mm; min-height: 297mm; padding: 12mm; box-sizing: border-box; overflow: hidden; page-break-after: always }
.page:last-child { page-break-after: auto }
h1 { font-size: 7mm; text-align: center; margin: 0 0 6mm }
h2 { font-size: 5mm; margin: 0 0 4mm }
.board-table { border-collapse: collapse; margin: 0 auto; table-layout: fixed }
.board-table td.sq { width: 19mm; height: 19mm; text-align: center; vertical-align: middle; font-size: 12mm; line-height: 19mm }
.board-table td.light { background: #f0d9b5 }
.board-table td.dark { background: #b58863 }
.board-table td.coord { width: 7mm; height: 19mm; text-align: center; vertical-align: middle; font-size: 3.5mm; color: #555 }
.board-table tr.coord-row td.coord { width: 19mm; height: 7mm }
.piece { color: #111 }
.legend { margin-top: 6mm; font-size: 3.6mm; line-height: 1.6 }
.legend p { margin: 1mm 0 }
.swatch { display: inline-block; width: 4mm; height: 4mm; border: 0.2mm solid #888; vertical-align: middle }
.swatch.light { background: #f0d9b5 }
.swatch.dark { background: #b58863 }
.disc-grid { text-align: center }
.piece-disc { display: inline-flex; flex-direction: column; align-items: center; justify-content: center; width: 22mm; height: 22mm; border: 0.3mm dashed #999; border-radius: 50%; margin: 1.5mm; vertical-align: top }
.piece-disc .glyph { font-size: 10mm; line-height: 1 }
.piece-disc .name { font-size: 3mm; line-height: 1.2; margin-top: 0.5mm; color: #333 }
.piece-disc.white .glyph { color: #fff; text-shadow: 0 0 0.35mm #333, 0 0 0.35mm #333 }
.piece-disc.black .glyph { color: #111 }
.practice li { margin: 2mm 0; font-size: 4mm }
.answer-page ol { font-size: 3.8mm; line-height: 1.9 }
.hint { font-size: 3.4mm; color: #666; margin-top: 6mm }
"""

_BASE_LETTERS: tuple[str, ...] = ("K", "Q", "R", "B", "N", "P")

_PRACTICE_QUESTIONS: tuple[str, ...] = (
    "写出 a1、h1、a8、h8 四格分别是什么颜色。",
    "白马位于 b1，一步能走到哪些格子？请全部列出。",
    "开局时白兵与黑兵分别站在哪些格子？各有多少枚？",
    "白王位于 e1 且周围没有其他棋子时，一步能走到哪些格子？",
    "e4 格子的四个斜线相邻格分别是什么？",
)

_PRACTICE_ANSWERS: tuple[str, ...] = (
    "a1 深色，h1 浅色，a8 浅色，h8 深色。",
    "b1 的马一步可到 a3、c3、d2。",
    "白兵在 a2–h2，共 8 枚；黑兵在 a7–h7，共 8 枚。",
    "e1 的白王一步可到 d1、f1、d2、e2、f2。",
    "e4 的斜线相邻格为 d3、f3、d5、f5。",
)


def _document(title: str, body: str) -> str:
    """把页面内容包装成完整 HTML 文档。"""
    safe_title: str = html.escape(title)
    return (
        "<!DOCTYPE html>\n"
        '<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{safe_title}</title>\n"
        f"<style>{_STYLE}</style>\n</head>\n<body>\n{body}\n</body>\n</html>\n"
    )


def _square_html(row: int, col: int, piece: str) -> str:
    """渲染单个棋格。"""
    name: str = square_name(row, col)
    tone: str = square_color(name)
    glyph: str = PIECE_GLYPHS.get(piece, "")
    content: str = f'<span class="piece">{glyph}</span>' if glyph else ""
    return f'<td class="sq {tone}" data-square="{name}">{content}</td>'


def _coordinate_cells() -> str:
    """生成 a-h 文件坐标行。"""
    return "".join(f'<td class="coord">{file_char}</td>' for file_char in "abcdefgh")


def _board_table(position: Position, show_coordinates: bool) -> str:
    """生成 8x8 棋盘表格，可选边缘坐标。"""
    rows: list[str] = []
    if show_coordinates:
        rows.append(
            f'<tr class="coord-row"><td class="coord"></td>{_coordinate_cells()}<td class="coord"></td></tr>'
        )
    for row in range(8):
        cells: list[str] = []
        for col in range(8):
            cells.append(_square_html(row, col, position.board[row][col]))
        rank_label: str = f'<td class="coord">{8 - row}</td>' if show_coordinates else ""
        rows.append(f"<tr>{rank_label}{''.join(cells)}{rank_label}</tr>")
    if show_coordinates:
        rows.append(
            f'<tr class="coord-row"><td class="coord"></td>{_coordinate_cells()}<td class="coord"></td></tr>'
        )
    return f'<table class="board-table">{"".join(rows)}</table>'


def _legend(position: Position) -> str:
    """棋盘底部图例与局面说明。"""
    side: str = "白方" if position.turn == "w" else "黑方"
    return (
        '<div class="legend">'
        "<p><strong>图例：</strong>"
        '<span class="swatch light"></span> 浅色格 '
        '<span class="swatch dark"></span> 深色格 '
        "｜ 白方 ♔ ♕ ♖ ♗ ♘ ♙ ｜ 黑方 ♚ ♛ ♜ ♝ ♞ ♟</p>"
        f"<p><strong>局面：</strong>{html.escape(describe(position))}"
        f"　行棋方：{side}"
        f"　王车易位：{html.escape(position.castling)}"
        f"　吃过路兵：{html.escape(position.en_passant)}"
        f"　回合：{position.fullmove}</p>"
        "</div>"
    )


def _board_page(position: Position, title: str, show_coordinates: bool) -> str:
    """棋盘页片段。"""
    return (
        '<section class="page board-page">\n'
        f"<h1>{html.escape(title)}</h1>\n"
        f"{_board_table(position, show_coordinates)}\n"
        f"{_legend(position)}\n"
        "</section>"
    )


def _pieces_page(title: str) -> str:
    """棋子裁剪片页片段：每种棋子 4 枚（2 白 + 2 黑），共 24 枚。"""
    discs: list[str] = []
    for letter in _BASE_LETTERS:
        for piece_char in (letter, letter.lower()):
            tone: str = "white" if piece_char.isupper() else "black"
            glyph: str = PIECE_GLYPHS[piece_char]
            name: str = PIECE_NAMES[piece_char]
            for _ in range(2):
                discs.append(
                    f'<div class="piece-disc {tone}">'
                    f'<span class="glyph">{glyph}</span>'
                    f'<span class="name">{name}</span></div>'
                )
    return (
        '<section class="page pieces-page">\n'
        f"<h1>{html.escape(title)}</h1>\n"
        '<p class="hint">沿虚线剪下圆片，可配合棋盘页使用；每种棋子各 4 枚（白 2、黑 2）。</p>\n'
        f'<div class="disc-grid">{"".join(discs)}</div>\n'
        "</section>"
    )


def _practice_pages(title: str) -> str:
    """练习页 + 独立答案页片段。"""
    questions: str = "".join(f"<li>{item}</li>" for item in _PRACTICE_QUESTIONS)
    answers: str = "".join(f"<li>{item}</li>" for item in _PRACTICE_ANSWERS)
    practice_page: str = (
        '<section class="page practice-page">\n'
        f"<h1>{html.escape(title)}</h1>\n"
        f'<ol class="practice">{questions}</ol>\n'
        '<p class="hint">完成后再翻到下一页核对答案。</p>\n'
        "</section>"
    )
    answer_page: str = (
        '<section class="page answer-page">\n'
        "<h2>参考答案</h2>\n"
        f'<ol class="answers">{answers}</ol>\n'
        "</section>"
    )
    return f"{practice_page}\n{answer_page}"


def render_board(
    position: Position,
    title: str = "国际象棋棋盘",
    show_coordinates: bool = True,
) -> str:
    """渲染单页 A4 棋盘，返回完整 HTML 文档。"""
    return _document(title, _board_page(position, title, show_coordinates))


def render_pieces(title: str = "棋子裁剪片") -> str:
    """渲染棋子裁剪片页，返回完整 HTML 文档。"""
    return _document(title, _pieces_page(title))


def render_practice(title: str = "走法练习") -> str:
    """渲染走法练习卡与独立答案页，返回完整 HTML 文档。"""
    return _document(title, _practice_pages(title))


def render_document(
    position: Position,
    show_pieces: bool = True,
    show_practice: bool = True,
    title: str = "国际象棋课堂讲义",
) -> str:
    """组合棋盘、裁剪片与练习卡，返回完整 HTML 文档。"""
    pages: list[str] = [_board_page(position, title, True)]
    if show_pieces:
        pages.append(_pieces_page(f"{title} · 棋子裁剪片"))
    if show_practice:
        pages.append(_practice_pages(f"{title} · 走法练习"))
    return _document(title, "\n".join(pages))
