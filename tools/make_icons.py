"""PWA 用アイコンを生成する（依存ライブラリ無し・純 Python）。
アンテナと電波のモチーフ。濃紺の地にアンバー。

    python tools/make_icons.py

出力: web/icons/Icon-{192,512}.png, Icon-maskable-{192,512}.png,
      web/icons/apple-touch-icon.png (180), web/favicon.png (64)
"""
import math
import os
import struct
import zlib

BG = (0x1E, 0x2B, 0x38)
FG = (0xF5, 0xB0, 0x41)
OUT = os.path.join(os.path.dirname(__file__), '..', 'web')


def png(path, size, pixels):
    raw = b''.join(b'\x00' + bytes(row) for row in pixels)

    def chunk(tag, data):
        c = struct.pack('>I', len(data)) + tag + data
        return c + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)))
        f.write(chunk(b'IDAT', zlib.compress(raw, 9)))
        f.write(chunk(b'IEND', b''))


def shape(u, v, scale):
    """(u,v) は 0..1 の正規化座標。アイコンの絵柄に含まれるなら True。
    scale: 絵柄の大きさ（maskable は安全領域のため小さめ）"""
    # 中心基準の座標に変換（-0.5..0.5）、scale で縮める
    x = (u - 0.5) / scale
    y = (v - 0.5) / scale
    t = 0.045                      # 線の太さ
    top = -0.22                    # 給電点（先端）の高さ
    # マスト
    if abs(x) < t / 2 and top <= y <= 0.36:
        return True
    # 土台（三脚風の横棒）
    if abs(y - 0.36) < t / 2 and abs(x) < 0.16:
        return True
    # 先端の丸
    if math.hypot(x, y - top) < 0.07:
        return True
    # 電波（左右に広がる弧）
    d = math.hypot(x, y - top)
    for r in (0.19, 0.31, 0.43):
        if abs(d - r) < t / 2 and abs(y - top) <= abs(x) * math.tan(math.radians(52)):
            return True
    return False


def render(size, rounded, scale, ss=3):
    px = []
    radius = size * 0.22 if rounded else 0
    for j in range(size):
        row = []
        for i in range(size):
            fg = 0
            bg = 0
            for a in range(ss):
                for b in range(ss):
                    u = (i + (a + 0.5) / ss) / size
                    v = (j + (b + 0.5) / ss) / size
                    # 角丸の外側は透明
                    if radius:
                        cx = min(max(u * size, radius), size - radius)
                        cy = min(max(v * size, radius), size - radius)
                        if math.hypot(u * size - cx, v * size - cy) > radius:
                            continue
                    bg += 1
                    if shape(u, v, scale):
                        fg += 1
            n = ss * ss
            alpha = bg / n
            k = fg / bg if bg else 0
            rgb = [round(BG[c] * (1 - k) + FG[c] * k) for c in range(3)]
            row += rgb + [round(255 * alpha)]
        px.append(row)
    return px


def main():
    icons = os.path.join(OUT, 'icons')
    os.makedirs(icons, exist_ok=True)
    jobs = [
        (os.path.join(icons, 'Icon-192.png'), 192, True, 0.82),
        (os.path.join(icons, 'Icon-512.png'), 512, True, 0.82),
        (os.path.join(icons, 'Icon-maskable-192.png'), 192, False, 0.68),
        (os.path.join(icons, 'Icon-maskable-512.png'), 512, False, 0.68),
        (os.path.join(icons, 'apple-touch-icon.png'), 180, False, 0.78),
        (os.path.join(OUT, 'favicon.png'), 64, True, 0.85),
    ]
    for path, size, rounded, scale in jobs:
        png(path, size, render(size, rounded, scale))
        print('wrote', os.path.relpath(path), size)


if __name__ == '__main__':
    main()
