#!/usr/bin/env python3
"""images/ 폴더의 기본 그림을 index.html 안에 넣는다 (앱을 파일 하나로 유지하기 위해).

파일 이름(확장자 제외)이 그림 키가 된다:
  c-clean, c-seat, c-nag, c-stash, c-miss,
  snack-mychew, snack-candy, snack-choco, snack-custom, stamp

사용법: python3 tools/embed_images.py
"""
import base64
import io
import re
from pathlib import Path

from PIL import Image, ImageDraw

KEYS = ['c-clean', 'c-seat', 'c-nag', 'c-stash', 'c-miss',
        'snack-mychew', 'snack-candy', 'snack-choco', 'snack-custom', 'stamp']
ROOT = Path(__file__).resolve().parent.parent
MAX_SIDE = 600


def to_data_url(path):
    im = Image.open(path).convert('RGBA')
    if im.getchannel('A').getextrema()[0] >= 250:      # 투명 배경이 아니면 가장자리 흰 배경을 지운다
        w, h = im.size
        for xy in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
            r, g, b, a = im.getpixel(xy)
            if a and min(r, g, b) >= 226:
                ImageDraw.floodfill(im, xy, (255, 255, 255, 0), thresh=36)
    bbox = im.getchannel('A').point(lambda a: 255 if a > 12 else 0).getbbox()
    if bbox:
        im = im.crop(bbox)
    im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=88, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()


def main():
    found = {}
    for p in sorted((ROOT / 'images').iterdir()):
        if p.stem in KEYS and p.suffix.lower() in ('.png', '.webp', '.jpg', '.jpeg'):
            found[p.stem] = to_data_url(p)
    body = ''.join(f"  '{k}': '{found[k]}',\n" for k in KEYS if k in found)
    html_path = ROOT / 'index.html'
    html = html_path.read_text(encoding='utf-8')
    block = ('/* DEFAULT_IMAGES:BEGIN — tools/embed_images.py가 images/ 폴더의 그림으로 채움 */\n'
             f'const DEFAULT_IMAGES = {{\n{body}}};\n/* DEFAULT_IMAGES:END */')
    html, n = re.subn(r'/\* DEFAULT_IMAGES:BEGIN.*?DEFAULT_IMAGES:END \*/', lambda _: block, html, flags=re.S)
    if n != 1:
        raise SystemExit('index.html에서 DEFAULT_IMAGES 표시를 찾지 못했어요')
    html_path.write_text(html, encoding='utf-8')
    print('embedded:', ', '.join(found) or '(none)')


if __name__ == '__main__':
    main()
