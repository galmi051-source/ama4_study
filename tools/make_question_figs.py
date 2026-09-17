"""図を使った問題（assets/questions/zukai.json）の図を作る。

    python tools/make_question_figs.py

tools/lecture/make_figs.py の描画部品を使って SVG を描き、Edge で PNG（assets/images/*.png）にする。
図を直したいときはここを編集して実行し直す。
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "lecture"))
import make_figs as mf  # noqa: E402

OUT = ROOT / "assets" / "images"
W, H = 1000, 600   # 出力 PNG の大きさ（viewBox 520x312 を約2倍）

EDGE = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]
INK, MUTED, RED, AMBER, GREEN, BLUE = mf.INK, mf.MUTED, mf.RED, mf.AMBER, mf.GREEN, mf.BLUE


class QFig(mf.Fig):
    """問題用：横長（520x312）。答えが図に書いてあってはいけないので、記号やア・イで示す"""

    def __init__(self):
        super().__init__(520, 312)

    def label(self, x, y, s, color=RED):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="16" fill="{color}"/>')
        self.text(x, y + 7, s, 18, "#fff", bold=True)

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" {mf.FONT}>'
                f'<rect x="0" y="0" width="{self.w}" height="{self.h}" fill="#fff"/>'
                + "".join(self.parts) + "</svg>")


FIGS = {}


def fig(name):
    def deco(fn):
        FIGS[name] = fn
        return fn
    return deco


@fig("z_parallel")
def _():
    f = QFig()
    f.line(60, 156, 140, 156); f.line(140, 90, 140, 222)
    f.line(140, 90, 200, 90); f.resistor(200, 90, 100, "20Ω"); f.line(300, 90, 360, 90)
    f.line(140, 222, 200, 222); f.resistor(200, 222, 100); f.text(250, 250, "20Ω", 18, MUTED); f.line(300, 222, 360, 222)
    f.line(360, 90, 360, 222); f.line(360, 156, 440, 156)
    f.circle(52, 156, 6); f.circle(448, 156, 6)
    f.text(250, 295, "端子間の合成抵抗は？", 18, MUTED)
    return f


@fig("z_ohm")
def _():
    f = QFig()
    f.line(80, 100, 80, 220); f.line(66, 150, 94, 150, w=3); f.line(72, 170, 88, 170, w=6)
    f.text(40, 165, "E", 22, INK, bold=True)
    f.line(80, 100, 200, 100); f.circle(240, 100, 32, label="A", size=24); f.line(272, 100, 420, 100)
    f.text(240, 50, "2A", 22, RED, bold=True)
    f.line(420, 100, 420, 130); f.parts.append(f'<rect x="408" y="130" width="24" height="60" fill="#fff" stroke="{INK}" stroke-width="2.5"/>')
    f.text(460, 165, "10Ω", 22, INK, bold=True)
    f.line(420, 190, 420, 220); f.line(80, 220, 420, 220)
    f.text(250, 285, "電源 E の電圧は？", 18, MUTED)
    return f


@fig("z_symbol_diode")
def _():
    f = QFig()
    f.line(120, 156, 230, 156); f.diode(260, 156, 26); f.line(286, 156, 400, 156)
    f.text(260, 260, "この記号の部品は？", 18, MUTED)
    return f


@fig("z_transistor")
def _():
    f = QFig()
    f.circle(260, 150, 80)
    f.line(215, 115, 215, 185, w=6); f.line(140, 150, 215, 150)
    f.line(215, 132, 275, 90); f.line(275, 90, 275, 50)
    f.line(215, 168, 275, 210); f.line(275, 210, 275, 250)
    f.arrow(240, 186, 272, 208, INK, 3)
    f.label(110, 150, "ア"); f.label(310, 50, "イ"); f.label(310, 250, "ウ")
    f.text(420, 160, "接合形トランジスタ", 16, MUTED)
    return f


@fig("z_yagi")
def _():
    f = QFig()
    f.line(80, 170, 440, 170, w=4)
    f.line(140, 80, 140, 260, INK, 8); f.line(240, 95, 240, 245, INK, 8); f.line(330, 105, 330, 235, INK, 8); f.line(400, 110, 400, 230, INK, 8)
    f.line(240, 170, 240, 175); f.text(240, 290, "給電", 16, MUTED)
    f.label(100, 60, "ア"); f.label(420, 60, "イ")
    f.arrow(78, 60, 30, 60, MUTED, 3); f.arrow(442, 60, 490, 60, MUTED, 3)
    f.text(260, 40, "八木アンテナ（上から見た図）", 16, MUTED)
    return f


@fig("z_meters")
def _():
    f = QFig()
    f.line(80, 90, 80, 230); f.line(66, 150, 94, 150, w=3); f.line(72, 170, 88, 170, w=6); f.text(45, 165, "電源", 14, MUTED)
    f.line(80, 90, 170, 90); f.circle(200, 90, 28); f.line(228, 90, 400, 90)
    f.line(400, 90, 400, 120); f.parts.append(f'<rect x="388" y="120" width="24" height="70" fill="#fff" stroke="{INK}" stroke-width="2.5"/>')
    f.text(440, 160, "負荷", 18); f.line(400, 190, 400, 230); f.line(80, 230, 400, 230)
    f.line(300, 90, 300, 125); f.circle(300, 155, 28); f.line(300, 183, 300, 230)
    f.label(200, 90, "ア"); f.label(300, 155, "イ")
    f.text(250, 290, "ア・イは計器。負荷の電流を測るのはどちら？", 16, MUTED)
    return f


@fig("z_am_wave")
def _():
    f = QFig()
    import math
    f.wave(50, 160, 300, 70, 16, INK, env=lambda t: 2 / 3 + 1 / 3 * math.sin(2 * math.pi * 1.5 * t))
    f.line(50, 160, 350, 160, mf.LINE, 1)
    f.line(370, 160, 370, 90, RED, 2); f.line(365, 90, 375, 90, RED, 2); f.line(365, 160, 375, 160, RED, 2)
    f.text(385, 128, "90V", 18, RED, anchor="start", bold=True)
    f.line(430, 160, 430, 113, BLUE, 2); f.line(425, 113, 435, 113, BLUE, 2); f.line(425, 160, 435, 160, BLUE, 2)
    f.text(445, 140, "60V", 18, BLUE, anchor="start", bold=True)
    f.line(50, 90, 350, 90, RED, 1.5, dash="5,5"); f.line(50, 113, 350, 113, BLUE, 1.5, dash="5,5")
    f.text(200, 270, "変調波の最大振幅 90V、搬送波の振幅 60V", 16, MUTED)
    return f


@fig("z_power_supply")
def _():
    f = QFig()
    f.box(20, 110, 100, 70, "交流\n100V", size=16); f.arrow(120, 145, 150, 145)
    f.box(150, 110, 100, 70, "変圧器", size=17); f.arrow(250, 145, 280, 145)
    f.box(280, 110, 100, 70, "", fill="#FFF6E5", stroke=RED); f.label(330, 145, "ア")
    f.arrow(380, 145, 410, 145); f.box(410, 110, 100, 70, "平滑回路", size=17)
    f.text(460, 215, "→ 直流", 16, MUTED)
    f.text(260, 270, "直流電源装置の構成。アに入る回路は？", 16, MUTED)
    return f


@fig("z_superhet")
def _():
    f = QFig()
    f.line(30, 70, 30, 40, w=3); f.line(15, 40, 45, 40, w=3); f.line(30, 70, 30, 120)
    boxes = [("高周波\n増幅器", 30), ("", 130), ("中間周波\n増幅器", 230), ("検波器", 330), ("低周波\n増幅器", 420)]
    for i, (lab, x) in enumerate(boxes):
        w = 80 if i < 4 else 85
        f.box(x, 90, w, 60, lab, size=13, fill="#FFF6E5" if i == 1 else "#fff", stroke=RED if i == 1 else INK)
        if i < 4:
            f.arrow(x + w, 120, boxes[i + 1][1], 120)
    f.label(170, 120, "ア")
    f.box(130, 200, 80, 50, "局部\n発振器", size=13); f.arrow(170, 200, 170, 150)
    f.text(260, 290, "スーパヘテロダイン受信機。アに入るのは？", 16, MUTED)
    return f


@fig("z_ionosphere")
def _():
    f = QFig()
    f.parts.append(f'<rect x="0" y="260" width="520" height="52" fill="#E8EDF2"/>'); f.text(260, 292, "地表", 16, MUTED)
    for y, lab, km in [(60, "ア", "約200〜400km"), (140, "イ", "約100km"), (200, "ウ", "約80km")]:
        f.line(20, y, 500, y, INK, 4, dash="14,8"); f.label(45, y, lab); f.text(480, y - 10, km, 14, MUTED, anchor="end")
    f.text(260, 30, "電離層の模式図", 16, MUTED)
    return f


def find_edge():
    for c in EDGE:
        if Path(c).exists():
            return c
    sys.exit("Edge が見つかりません")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    edge = find_edge()
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("CHROME_") and k.upper() != "__COMPAT_LAYER"}
    profile = Path(tempfile.gettempdir()) / "ama4_lecture_edge_profile"
    with tempfile.TemporaryDirectory() as td:
        for name, fn in FIGS.items():
            svg = fn().svg()
            hp = Path(td) / f"{name}.html"
            hp.write_text(f"<html><head><meta charset='utf-8'><style>html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;background:#fff}}"
                          f"svg{{width:{W}px;height:{H}px}}</style></head><body>{svg}</body></html>", encoding="utf-8")
            png = OUT / f"{name}.png"
            subprocess.run([edge, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                            f"--user-data-dir={profile}", f"--window-size={W},{H}", f"--screenshot={png}", hp.as_uri()],
                           capture_output=True, timeout=120, env=env)
            if not png.exists():
                sys.exit(f"画像化に失敗: {name}")
            print("wrote", png.relative_to(ROOT))


if __name__ == "__main__":
    main()
