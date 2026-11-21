# chessboard 国际象棋棋盘与棋子裁剪页

[![CI](https://github.com/eastyou/chessboard/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/chessboard/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)


面向课堂的开源小工具：用一条命令把 FEN 局面渲染成可打印的 A4 棋盘，并附带棋子裁剪片与走法练习卡。纯 Python 标准库实现，零第三方依赖，适合教师备课、学生练习与作品集展示。

## 功能

- FEN 解析与严格校验：6 段、8 行、每行 8 格、每方恰好一个王、兵不位于底线、回合/半回合/回合数合法。
- A4 打印棋盘：浅色 `#f0d9b5`、深色 `#b58863`，带 a-h / 1-8 坐标、图例与当前局面说明。
- 棋子裁剪片：24 枚圆形卡片（直径 22mm），带虚线剪切线与中文名，黑白两色。
- 走法练习卡：格色判断、马的走法、兵的初始位置等问题，答案单独成页。
- 命令行友好：非法输入返回码 2，写文件失败返回码 1，成功返回码 0。

## 安装

```bash
git clone https://github.com/eastyou/chessboard.git
cd chessboard
pip install -e .
```

也可以不安装，直接在仓库根目录用模块方式运行。

## 快速开始

```bash
# 默认起始局面，输出 chessboard.html
python3 -m chessboard -o board.html

# 指定 FEN 局面
python3 -m chessboard --fen "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" -o start.html

# 空棋盘
python3 -m chessboard --empty -o empty.html

# 从文件读取 FEN
python3 -m chessboard --fen-file position.fen -o from-file.html

# 只要棋盘，不要裁剪片与练习卡，并自定义标题
python3 -m chessboard --no-pieces --no-practice --title "第 1 课：棋盘与坐标" -o lesson.html
```

安装后也可直接使用 `chessboard` 命令，参数完全一致。

## 命令行参数

| 参数 | 说明 |
| --- | --- |
| `-o, --output` | 输出 HTML 路径，默认 `chessboard.html` |
| `--fen` | 直接指定 FEN 局面字符串 |
| `--fen-file` | 从文本文件读取 FEN（自动去首尾空白，支持 UTF-8/BOM/GBK 回退） |
| `--empty` | 生成空棋盘（8 行 `8`） |
| `--no-pieces` | 不生成棋子裁剪片 |
| `--no-practice` | 不生成走法练习卡 |
| `--title` | 页面标题，默认「国际象棋课堂讲义」 |

`--fen` 与 `--fen-file` 不能同时使用；`--empty` 也不能与二者同时使用。

## FEN 说明

FEN 由 6 段空格分隔的字段组成：

```
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

1. 棋盘布置：8 行（从第 8 横排到第 1 横排），`/` 分隔；大写为白方，小写为黑方，数字表示连续空格。
2. 行棋方：`w`（白）或 `b`（黑）。
3. 王车易位权：`KQkq` 的任意组合，或 `-`。
4. 吃过路兵目标格：格名或 `-`。
5. 半回合计数：非负整数。
6. 整数回合数：非负整数。

任一段非法都会抛出 `ChessError`（继承自 `ValueError`），错误信息为中文并指出具体行或格。

## 项目结构

```
chessboard/
├── chessboard/
│   ├── __init__.py     # 包导出
│   ├── __main__.py     # python -m chessboard 入口
│   ├── model.py        # FEN 解析、校验、棋格工具
│   ├── render.py       # HTML/SVG 渲染
│   └── cli.py          # 命令行入口
├── tests/              # unittest 测试
├── examples/board.html # 生成示例
└── pyproject.toml
```

## 测试

```bash
python3 -m unittest discover -s tests -v
```

## 许可

MIT License © 2026 eastyou
