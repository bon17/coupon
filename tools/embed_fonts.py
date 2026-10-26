#!/usr/bin/env python3
"""fonts/ 폴더의 나눔스퀘어라운드 글꼴을 index.html 안에 넣는다 (인터넷 없이도 글꼴이 나오게).

사용법: python3 tools/embed_fonts.py
"""
import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FACES = [('NanumSquareRound', 400, 'NanumSquareRoundR.woff2'),
         ('NanumSquareRound', 800, 'NanumSquareRoundEB.woff2')]


def main():
    css = ''.join(
        f"@font-face{{font-family:'{family}';font-weight:{weight};font-display:swap;"
        f"src:url(data:font/woff2;base64,{base64.b64encode((ROOT / 'fonts' / name).read_bytes()).decode()}) format('woff2')}}\n"
        for family, weight, name in FACES)
    block = ('/* EMBEDDED_FONTS:BEGIN — tools/embed_fonts.py가 fonts/ 폴더의 글꼴로 채움 (OFL, fonts/OFL.txt) */\n'
             f'{css}/* EMBEDDED_FONTS:END */')
    html_path = ROOT / 'index.html'
    html = html_path.read_text(encoding='utf-8')
    html, n = re.subn(r'/\* EMBEDDED_FONTS:BEGIN.*?EMBEDDED_FONTS:END \*/', lambda _: block, html, flags=re.S)
    if n != 1:
        raise SystemExit('index.html에서 EMBEDDED_FONTS 표시를 찾지 못했어요')
    html_path.write_text(html, encoding='utf-8')
    print('embedded:', ', '.join(name for *_, name in FACES))


if __name__ == '__main__':
    main()
