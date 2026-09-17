"""講義スライド用の図（SVG）を生成する。  python tools/lecture/make_figs.py
図を直したいときはここを編集して実行し直す（fig/ 以下が上書きされる）。
電源の図（fig_series 等）は初期に別途作ったもので、ここには含まない。
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent / "fig"
INK, MUTED, RED, AMBER, GREEN, BLUE, LINE = "#1A1F24", "#66727F", "#C8463D", "#F5B041", "#2E9E62", "#2F6DB5", "#D9DEE3"
FONT = 'font-family="Yu Gothic UI, Meiryo, sans-serif"'


class Fig:
    def __init__(self, w=520, h=400):
        self.w, self.h = w, h
        self.parts = []

    def text(self, x, y, s, size=20, color=INK, anchor="middle", bold=False):
        b = ' font-weight="700"' if bold else ""
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}"{b}>{s}</text>')

    def line(self, x1, y1, x2, y2, color=INK, w=3, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}"{d}/>')

    def arrow(self, x1, y1, x2, y2, color=INK, w=3):
        self.line(x1, y1, x2, y2, color, w)
        a = math.atan2(y2 - y1, x2 - x1)
        p = [(x2, y2), (x2 - 14 * math.cos(a - 0.4), y2 - 14 * math.sin(a - 0.4)),
             (x2 - 14 * math.cos(a + 0.4), y2 - 14 * math.sin(a + 0.4))]
        self.parts.append('<polygon points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in p) + f'" fill="{color}"/>')

    def box(self, x, y, w, h, label="", fill="#fff", stroke=INK, size=20, color=INK, r=8, bold=False):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>')
        if label:
            lines = label.split("\n")
            y0 = y + h / 2 - (len(lines) - 1) * size * 0.6 + size * 0.35
            for i, s in enumerate(lines):
                self.text(x + w / 2, y0 + i * size * 1.2, s, size, color, bold=bold)

    def circle(self, x, y, r, fill="#fff", stroke=INK, label="", size=20):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>')
        if label:
            self.text(x, y + size * 0.35, label, size)

    def wave(self, x0, y0, w, amp, n=3, color=INK, env=None, rect=False, fm=None):
        pts = []
        for i in range(0, w + 1, 2):
            t = i / w
            a = amp * (env(t) if env else 1)
            ph = 2 * math.pi * (n * t + (fm(t) if fm else 0))
            v = math.sin(ph)
            if rect:
                v = max(v, 0)
            pts.append(f"{x0 + i},{y0 - v * a:.1f}")
        self.parts.append('<polyline points="' + " ".join(pts) + f'" fill="none" stroke="{color}" stroke-width="2.5"/>')

    def resistor(self, x, y, w=60, label=""):
        self.parts.append(f'<rect x="{x}" y="{y-10}" width="{w}" height="20" fill="#fff" stroke="{INK}" stroke-width="2.5"/>')
        if label:
            self.text(x + w / 2, y - 18, label, 18, MUTED)

    def coil(self, x, y, n=4, r=9):
        d = f"M{x} {y}" + "".join(f" a{r} {r} 0 0 1 {2*r} 0" for _ in range(n))
        self.parts.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="2.5"/>')

    def cap(self, x, y, vert=True):
        if vert:
            self.line(x - 14, y - 4, x + 14, y - 4, w=4)
            self.line(x - 14, y + 4, x + 14, y + 4, w=4)
        else:
            self.line(x - 4, y - 14, x - 4, y + 14, w=4)
            self.line(x + 4, y - 14, x + 4, y + 14, w=4)

    def diode(self, x, y, size=16, vert=False):
        if vert:  # 上から下へ流れる
            self.parts.append(f'<polygon points="{x-size},{y-size} {x+size},{y-size} {x},{y+size}" fill="{INK}"/>')
            self.line(x - size, y + size, x + size, y + size, w=4)
        else:
            self.parts.append(f'<polygon points="{x-size},{y-size} {x-size},{y+size} {x+size},{y}" fill="{INK}"/>')
            self.line(x + size, y - size, x + size, y + size, w=4)

    def save(self, name):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" {FONT}>'
               + "".join(self.parts) + "</svg>")
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")


# ================= 電子回路 =================
def fig_diode():
    f = Fig()
    f.line(40, 120, 200, 120); f.diode(230, 120, 22); f.line(252, 120, 480, 120)
    f.text(150, 90, "アノード（＋）", 20, RED); f.text(360, 90, "カソード（−）", 20, BLUE)
    f.arrow(120, 180, 400, 180, GREEN, 4); f.text(260, 215, "電流はこの向きにだけ流れる", 20, GREEN, bold=True)
    f.arrow(400, 260, 120, 260, RED, 4); f.text(260, 295, "逆向きには流れない", 20, RED)
    f.parts.append(f'<line x1="240" y1="240" x2="280" y2="280" stroke="{RED}" stroke-width="4"/>')
    f.text(260, 360, "三角の向き ＝ 電流の向き", 22, INK, bold=True)
    f.save("fig_diode")


def fig_zener():
    f = Fig()
    # axes
    f.line(60, 340, 480, 340); f.line(260, 40, 260, 370)
    f.text(470, 365, "電圧", 18, MUTED); f.text(290, 55, "電流", 18, MUTED)
    f.text(400, 365, "順方向 →", 18, MUTED); f.text(120, 365, "← 逆方向", 18, MUTED)
    # forward curve
    pts = " ".join(f"{260+i},{340-max(0,(i-60))**1.8/220:.1f}" for i in range(0, 200, 4))
    f.parts.append(f'<polyline points="{pts}" fill="none" stroke="{INK}" stroke-width="3"/>')
    # reverse: flat then breakdown
    f.line(260, 340, 120, 340, INK, 3)
    f.line(120, 340, 116, 392, RED, 5)
    f.parts.append(f'<circle cx="120" cy="340" r="7" fill="{RED}"/>')
    f.text(120, 320, "降伏電圧", 18, RED, bold=True)
    f.text(60, 385, "急に大電流", 17, RED, bold=True)
    f.text(150, 130, "定電圧（ツェナー）", 20, RED, bold=True)
    f.text(150, 155, "ダイオードはここを使う", 18, RED)
    f.text(390, 250, "ふつうの動作", 18, MUTED)
    f.save("fig_zener")


def fig_transistor():
    f = Fig()
    # NPN symbol
    f.circle(150, 180, 70)
    f.line(110, 150, 110, 210, w=5); f.line(60, 180, 110, 180)
    f.line(110, 165, 160, 130); f.line(160, 130, 160, 100)
    f.line(110, 195, 160, 230); f.line(160, 230, 160, 260)
    f.arrow(130, 209, 158, 228, INK, 3)
    f.text(50, 172, "B", 22, RED, bold=True); f.text(175, 100, "C", 22, RED, bold=True); f.text(175, 268, "E", 22, RED, bold=True)
    f.text(150, 300, "接合形トランジスタ", 20, INK, bold=True)
    f.text(150, 330, "エミッタ・ベース・コレクタ", 18, RED)
    # FET
    f.circle(380, 180, 70)
    f.line(340, 150, 340, 210, w=3); f.line(290, 180, 340, 180)
    f.line(352, 145, 352, 215, w=5)
    f.line(352, 150, 395, 150, w=3); f.line(395, 150, 395, 100)
    f.line(352, 210, 395, 210, w=3); f.line(395, 210, 395, 260)
    f.text(280, 172, "G", 22, BLUE, bold=True); f.text(410, 100, "D", 22, BLUE, bold=True); f.text(410, 268, "S", 22, BLUE, bold=True)
    f.text(380, 300, "FET", 20, INK, bold=True)
    f.text(380, 330, "ゲート・ドレイン・ソース", 18, BLUE)
    f.save("fig_transistor")


def fig_circuits():
    f = Fig()
    f.text(90, 45, "送信側", 20, MUTED); f.text(430, 45, "受信側", 20, MUTED)
    f.box(30, 70, 120, 60, "音声", size=20); f.arrow(150, 100, 190, 100)
    f.box(190, 70, 120, 60, "変調回路", fill="#FFF6E5", stroke=AMBER, bold=True)
    f.arrow(310, 100, 350, 100); f.text(330, 90, "", 12)
    f.box(350, 70, 140, 60, "電波（変調波）", size=18)
    f.text(250, 160, "搬送波に信号を乗せる", 18, MUTED)
    f.box(350, 220, 140, 60, "電波（変調波）", size=18); f.arrow(350, 250, 310, 250)
    f.box(190, 220, 120, 60, "検波回路", fill="#FFF6E5", stroke=AMBER, bold=True)
    f.arrow(190, 250, 150, 250); f.box(30, 220, 120, 60, "音声", size=20)
    f.text(250, 310, "変調波から信号を取り出す（復調）", 18, MUTED)
    f.text(260, 370, "乗せるのが変調、取り出すのが検波", 22, RED, bold=True)
    f.save("fig_circuits")


# ================= 電波障害 =================
def fig_harmonics():
    f = Fig()
    f.line(40, 300, 500, 300)
    for x, h, lab, col in [(120, 200, "基本波 28MHz", INK), (230, 80, "第2高調波 56MHz", MUTED), (340, 110, "第3高調波 84MHz", RED), (450, 50, "第4 112MHz", MUTED)]:
        f.parts.append(f'<rect x="{x-14}" y="{300-h}" width="28" height="{h}" fill="{col}"/>')
        f.text(x, 330, lab.split(" ")[0], 16, col); f.text(x, 352, lab.split(" ")[1], 16, col, bold=(col == RED))
    f.parts.append(f'<rect x="300" y="60" width="90" height="40" rx="6" fill="#FFF6E5" stroke="{RED}" stroke-width="2"/>')
    f.text(345, 87, "FM放送帯", 17, RED, bold=True); f.text(345, 45, "76〜95MHz", 15, RED)
    f.text(260, 385, "高調波 ＝ 基本波の整数倍（必ず高い）", 20, INK, bold=True)
    f.save("fig_harmonics")


def fig_lpf():
    f = Fig()
    f.box(30, 60, 130, 70, "送信機", size=22)
    f.arrow(160, 95, 200, 95)
    f.box(200, 60, 130, 70, "低域フィルタ\n（LPF）", fill="#FFF6E5", stroke=AMBER, size=19, bold=True)
    f.arrow(330, 95, 380, 95)
    f.line(400, 95, 400, 40, w=3); f.line(380, 40, 420, 40, w=3); f.line(385, 55, 415, 55, w=3); f.line(390, 70, 410, 70, w=3)
    f.text(455, 100, "アンテナ", 18)
    f.text(180, 160, "基本波 ＋ 高調波", 17, MUTED); f.text(400, 160, "基本波だけ", 17, GREEN, bold=True)
    # response curve
    f.line(60, 340, 480, 340); f.line(60, 220, 60, 350)
    f.text(470, 365, "周波数 →", 16, MUTED); f.text(60, 210, "通す量", 16, MUTED, anchor="start")
    f.parts.append(f'<path d="M60 240 L230 240 C 270 240 280 330 330 335 L480 338" fill="none" stroke="{BLUE}" stroke-width="4"/>')
    f.text(140, 270, "低い周波数は通す", 16, BLUE); f.text(400, 310, "高い周波数（高調波）はカット", 16, RED)
    f.save("fig_lpf")


def fig_bef():
    f = Fig()
    f.line(90, 95, 90, 40, w=3); f.line(70, 40, 110, 40, w=3); f.text(90, 125, "地デジアンテナ", 16)
    f.arrow(90, 95, 90, 140) if False else None
    f.line(110, 60, 160, 60); f.arrow(160, 60, 200, 60)
    f.box(200, 30, 130, 60, "トラップフィルタ\n（BEF）", fill="#FFF6E5", stroke=AMBER, size=17, bold=True)
    f.arrow(330, 60, 370, 60); f.box(370, 30, 120, 60, "ブースタ", size=20)
    f.text(455, 115, "→ テレビへ", 16, MUTED)
    f.text(120, 165, "435MHz（アマチュア）", 16, RED); f.text(430, 165, "470〜710MHz は通す", 16, GREEN)
    f.line(60, 340, 480, 340); f.line(60, 220, 60, 350)
    f.text(470, 365, "周波数 →", 16, MUTED)
    f.parts.append(f'<path d="M60 240 L150 240 C 175 240 175 330 195 332 C 215 330 215 240 240 240 L480 240" fill="none" stroke="{BLUE}" stroke-width="4"/>')
    f.text(195, 300, "435MHz", 15, RED, bold=True); f.text(195, 318, "だけ落とす", 15, RED)
    f.text(360, 225, "テレビの周波数は通す", 16, GREEN)
    f.save("fig_bef")


def fig_cross_mod():
    f = Fig()
    f.wave(30, 90, 150, 30, 12, INK, env=lambda t: 0.6 + 0.4 * math.sin(2 * math.pi * 2 * t))
    f.text(105, 150, "希望波（聞きたい放送）", 16)
    f.wave(30, 240, 150, 45, 12, RED, env=lambda t: 0.6 + 0.4 * math.sin(2 * math.pi * 5 * t))
    f.text(105, 300, "強い妨害波（別の周波数）", 16, RED)
    f.arrow(190, 90, 250, 150, INK); f.arrow(190, 240, 250, 180, RED)
    f.box(250, 130, 90, 70, "受信機", size=20)
    f.arrow(340, 165, 380, 165)
    f.wave(380, 165, 120, 40, 10, INK, env=lambda t: 0.6 + 0.4 * math.sin(2 * math.pi * 2 * t) * (0.5 + 0.5 * math.sin(2 * math.pi * 5 * t)))
    f.text(440, 230, "妨害波の変調が", 16, RED); f.text(440, 252, "乗り移る", 16, RED, bold=True)
    f.text(260, 360, "混変調 → 関係ない音が混ざる（BCI）", 21, INK, bold=True)
    f.save("fig_cross_mod")


# ================= 電波伝搬 =================
def fig_ionosphere():
    f = Fig()
    f.parts.append(f'<rect x="0" y="330" width="520" height="70" fill="#E8EDF2"/>')
    f.text(260, 370, "地球", 18, MUTED)
    for y, name, km, col in [(80, "F層", "200〜400km", RED), (170, "E層", "約100km", INK), (230, "D層", "約80km", BLUE)]:
        f.line(20, y, 500, y, col, 6 if col == RED else 4, dash="14,8")
        f.text(40, y - 12, name, 20, col, anchor="start", bold=True); f.text(480, y - 12, km, 15, MUTED, anchor="end")
    f.text(300, 60, "短波を反射 → 遠距離へ", 17, RED)
    f.text(300, 262, "昼間、低い周波数を吸収", 17, BLUE)
    # HF path bouncing off F
    f.parts.append(f'<path d="M60 330 Q 160 80 260 330 Q 360 80 460 330" fill="none" stroke="{RED}" stroke-width="3"/>')
    f.text(160, 310, "短波（HF）", 16, RED)
    f.save("fig_ionosphere")


def fig_propagation():
    f = Fig()
    f.parts.append(f'<path d="M0 330 Q 260 250 520 330 L520 400 L0 400 Z" fill="#E8EDF2"/>')
    f.line(20, 60, 500, 60, RED, 5, dash="14,8"); f.text(40, 48, "電離層", 18, RED, anchor="start")
    # HF bounce
    f.parts.append(f'<path d="M60 300 L 200 62 L 340 300" fill="none" stroke="{RED}" stroke-width="3"/>')
    f.text(120, 200, "短波 HF", 17, RED, bold=True); f.text(120, 222, "反射して遠くへ", 15, RED)
    # VHF through
    f.arrow(300, 300, 380, 30, BLUE, 3); f.text(430, 120, "VHF・UHF", 17, BLUE, bold=True); f.text(430, 142, "突き抜ける", 15, BLUE)
    # direct wave
    f.line(60, 300, 60, 260, w=3); f.line(45, 260, 75, 260, w=3)
    f.line(300, 300, 300, 260, w=3); f.line(285, 260, 315, 260, w=3)
    f.arrow(70, 268, 290, 268, GREEN, 3); f.text(180, 258, "直接波（見通し内）", 16, GREEN, bold=True)
    f.text(260, 385, "VHF/UHF は直接波で見える範囲、HF は電離層で遠くへ", 17, INK)
    f.save("fig_propagation")


def fig_sporadic_e():
    f = Fig()
    f.parts.append(f'<rect x="0" y="330" width="520" height="70" fill="#E8EDF2"/>')
    f.line(20, 70, 500, 70, MUTED, 3, dash="14,8"); f.text(40, 58, "F層", 16, MUTED, anchor="start")
    f.line(20, 160, 500, 160, MUTED, 3, dash="14,8"); f.text(40, 148, "E層", 16, MUTED, anchor="start")
    f.parts.append(f'<ellipse cx="260" cy="160" rx="120" ry="14" fill="{AMBER}" opacity="0.9"/>')
    f.text(260, 128, "スポラディックE層（Eスポ）", 18, RED, bold=True)
    f.parts.append(f'<path d="M60 330 L 260 165 L 460 330" fill="none" stroke="{RED}" stroke-width="3"/>')
    f.text(120, 250, "50MHz帯", 16, RED); f.text(120, 272, "（普段は突き抜ける）", 14, MUTED)
    f.text(400, 250, "数百km先に届く", 16, RED); f.text(400, 272, "＝ 遠距離交信／混信", 14, RED)
    f.parts.append(f'<circle cx="470" cy="40" r="18" fill="{AMBER}"/>'); f.text(470, 80, "夏の昼間", 16, RED, bold=True)
    f.save("fig_sporadic_e")


# ================= 測定 =================
def fig_meters():
    f = Fig()
    # circuit: battery left, ammeter in series top, load right, voltmeter parallel
    f.line(80, 120, 80, 280); f.line(80, 120, 170, 120)
    f.line(66, 180, 94, 180, w=3); f.line(72, 200, 88, 200, w=6); f.text(40, 195, "電源", 16, MUTED)
    f.circle(200, 120, 30, label="A", size=24); f.line(230, 120, 400, 120)
    f.line(400, 120, 400, 160); f.resistor(390, 200, 20, "")  # placeholder
    f.parts.pop()  # remove placeholder resistor
    f.parts.append(f'<rect x="388" y="160" width="24" height="80" fill="#fff" stroke="{INK}" stroke-width="2.5"/>')
    f.text(440, 205, "負荷", 18)
    f.line(400, 240, 400, 280); f.line(80, 280, 400, 280)
    f.line(300, 120, 300, 160); f.circle(300, 200, 30, label="V", size=24); f.line(300, 230, 300, 280)
    f.text(200, 70, "電流計：直列", 20, RED, bold=True); f.text(200, 92, "（通り道に割り込む）", 15, RED)
    f.text(300, 330, "電圧計：並列", 20, BLUE, bold=True); f.text(300, 352, "（負荷をまたぐ）", 15, BLUE)
    f.save("fig_meters")


def fig_shunt():
    f = Fig()
    f.line(40, 150, 140, 150); f.circle(200, 150, 40, label="A", size=26); f.line(240, 150, 340, 150)
    f.text(200, 90, "内部抵抗 r", 17, MUTED)
    f.line(140, 150, 140, 240); f.line(240, 150, 240, 240); f.line(140, 240, 165, 240); f.resistor(165, 240, 50); f.line(215, 240, 240, 240)
    f.text(190, 285, "分流器 r/4", 18, RED, bold=True)
    f.arrow(40, 130, 130, 130, INK, 3); f.text(85, 118, "5", 20, INK, bold=True)
    f.arrow(150, 108, 250, 108, BLUE, 3); f.text(200, 66, "", 10); f.text(270, 112, "1", 20, BLUE, bold=True, anchor="start")
    f.arrow(150, 262, 250, 262, RED, 3); f.text(270, 266, "4", 20, RED, bold=True, anchor="start")
    f.text(400, 150, "電流計に 1", 18, BLUE, anchor="start"); f.text(400, 178, "分流器に 4", 18, RED, anchor="start")
    f.text(400, 206, "合計 5", 18, INK, anchor="start", bold=True)
    f.text(260, 345, "倍率 ＝ 1 ＋ r ÷（分流器の抵抗）", 20, INK, bold=True)
    f.text(260, 375, "＝ 1 ＋ 4 ＝ 5倍", 20, RED, bold=True)
    f.save("fig_shunt")


def fig_swr():
    f = Fig()
    f.box(30, 60, 110, 60, "送信機", size=20); f.line(140, 90, 380, 90, w=4)
    f.line(400, 90, 400, 40, w=3); f.line(380, 40, 420, 40, w=3); f.text(400, 130, "アンテナ", 16)
    f.arrow(160, 70, 340, 70, GREEN, 3); f.text(250, 60, "進行波", 15, GREEN)
    f.arrow(340, 112, 160, 112, RED, 3); f.text(250, 128, "反射波（整合がずれると戻る）", 15, RED)
    f.box(40, 190, 200, 80, "整合している\n反射なし", fill="#EAF6EE", stroke=GREEN, size=18)
    f.text(140, 300, "SWR ＝ 1（最良）", 22, GREEN, bold=True)
    f.box(280, 190, 200, 80, "整合がずれている\n反射あり", fill="#FDECEA", stroke=RED, size=18)
    f.text(380, 300, "SWR ＞ 1（大きいほど悪い）", 18, RED, bold=True)
    f.text(260, 365, "SWRメータで測るのは「定在波比」", 19, INK)
    f.save("fig_swr")


def fig_dummy():
    f = Fig()
    f.text(130, 40, "ディップメータ", 20, INK, bold=True)
    f.box(40, 60, 110, 70, "メータ", size=18); f.coil(160, 95, 4, 8); f.text(200, 75, "コイル", 14, MUTED)
    f.coil(250, 95, 4, 8); f.cap(300, 95, vert=False); f.line(250, 95, 250, 140); f.line(322, 95, 322, 140); f.line(250, 140, 322, 140)
    f.line(300, 81, 300, 95); f.line(300, 95, 300, 109)
    f.text(290, 170, "調べたい同調回路", 15, MUTED)
    f.text(130, 190, "近づけて周波数を変える →", 15, MUTED)
    f.text(130, 212, "共振周波数で針がディップ（下がる）", 15, RED, bold=True)
    f.text(390, 40, "擬似負荷（ダミーロード）", 20, INK, bold=True)
    f.box(340, 230, 110, 60, "送信機", size=18); f.line(450, 260, 470, 260); f.resistor(470, 260, 40, ""); f.text(490, 240, "抵抗", 14, MUTED)
    f.line(455, 250, 455, 250)
    f.text(430, 320, "アンテナの代わりにつなぐ", 16, MUTED)
    f.text(430, 345, "→ 電波を出さずに調整できる", 16, RED, bold=True)
    f.parts.append(f'<line x1="380" y1="150" x2="440" y2="210" stroke="{RED}" stroke-width="4"/><line x1="440" y1="150" x2="380" y2="210" stroke="{RED}" stroke-width="4"/>')
    f.line(410, 200, 410, 160, w=3); f.line(395, 160, 425, 160, w=3)
    f.save("fig_dummy")


# ================= 空中線 =================
def fig_wavelength():
    f = Fig()
    f.text(260, 60, "波長（m）＝ 300 ÷ 周波数（MHz）", 26, RED, bold=True)
    for i, (fq, lam, band) in enumerate([("7MHz", "約43m", "40mバンド"), ("21MHz", "約14.3m", "15mバンド"), ("144MHz", "約2m", "2mバンド"), ("430MHz", "約0.7m", "70cmバンド")]):
        y = 110 + i * 62
        f.text(80, y + 8, fq, 22, INK, bold=True)
        w = [400, 190, 60, 30][i]
        f.wave(130, y, w, 16, 1, BLUE)
        f.text(130 + w + 20, y + 8, lam, 20, BLUE, anchor="start", bold=True)
        f.text(130 + w + 130, y + 8, band, 15, MUTED, anchor="start")
    f.text(260, 375, "周波数が高いほど波長は短い", 20, INK)
    f.save("fig_wavelength")


def fig_dipole():
    f = Fig()
    f.text(130, 40, "半波長ダイポール", 20, INK, bold=True)
    f.line(30, 90, 120, 90, w=5); f.line(140, 90, 230, 90, w=5)
    f.line(120, 90, 120, 130); f.line(140, 90, 140, 130); f.text(130, 155, "給電点", 15, MUTED)
    f.arrow(30, 60, 230, 60, MUTED, 2); f.text(130, 52, "λ/2", 16, MUTED)
    f.text(130, 200, "約73Ω（75Ω）", 22, RED, bold=True)
    f.text(390, 40, "1/4波長 垂直接地", 20, INK, bold=True)
    f.parts.append(f'<rect x="300" y="200" width="180" height="12" fill="#B8C2CC"/>'); f.text(390, 232, "大地（またはラジアル）", 14, MUTED)
    f.line(390, 200, 390, 80, w=5); f.arrow(420, 200, 420, 80, MUTED, 2); f.text(445, 145, "λ/4", 16, MUTED)
    f.line(380, 200, 380, 215); f.text(390, 270, "約36Ω（73の半分）", 22, RED, bold=True)
    f.text(390, 300, "21MHz：14.3m ÷ 4 ≒ 3.6m", 17, BLUE)
    f.text(260, 370, "ダイポール 73、その半分の垂直接地 36", 20, INK)
    f.save("fig_dipole")


def fig_yagi():
    f = Fig()
    f.line(60, 200, 460, 200, w=4)  # boom
    f.line(120, 100, 120, 300, RED, 8); f.text(120, 330, "反射器", 18, RED, bold=True); f.text(120, 352, "長い", 16, RED)
    f.line(240, 120, 240, 280, INK, 8); f.text(240, 330, "放射器", 18, INK, bold=True); f.text(240, 352, "（給電）", 14, MUTED)
    f.line(340, 135, 340, 265, BLUE, 8); f.text(340, 330, "導波器", 18, BLUE, bold=True); f.text(340, 352, "短い", 16, BLUE)
    f.line(420, 140, 420, 260, BLUE, 8); f.text(420, 330, "導波器", 16, BLUE)
    f.arrow(300, 60, 490, 60, GREEN, 5); f.text(395, 45, "電波はこっちに強く出る", 17, GREEN, bold=True)
    f.text(260, 390, "「長く反射、短く導く」", 22, RED, bold=True)
    f.save("fig_yagi")


def fig_coax():
    f = Fig()
    f.text(260, 60, "5 D - 2 V", 44, INK, bold=True)
    f.parts.append(f'<rect x="228" y="22" width="40" height="52" rx="6" fill="none" stroke="{RED}" stroke-width="3"/>')
    f.arrow(248, 100, 248, 130, RED, 3)
    f.text(248, 160, "2文字目でインピーダンスが決まる", 18, RED, bold=True)
    f.box(60, 200, 180, 80, "D ＝ 50Ω\nアマチュア無線用", fill="#FFF6E5", stroke=AMBER, size=20, bold=True)
    f.box(280, 200, 180, 80, "C ＝ 75Ω\nテレビ用", size=20)
    f.text(180, 330, "最初の数字（5・3）は太さの目安", 17, MUTED, anchor="start")
    f.text(180, 355, "大きいほど太くて損失が少ない", 17, MUTED, anchor="start")
    f.circle(110, 340, 26, "#fff", INK); f.circle(110, 340, 14, "#fff", INK); f.circle(110, 340, 4, INK, INK)
    f.save("fig_coax")


# ================= 基礎 =================
def fig_ohm():
    f = Fig()
    f.parts.append(f'<polygon points="260,40 100,260 420,260" fill="#FFF6E5" stroke="{AMBER}" stroke-width="3"/>')
    f.line(150, 190, 370, 190, AMBER, 3); f.line(260, 190, 260, 260, AMBER, 3)
    f.text(260, 160, "V", 48, RED, bold=True); f.text(205, 245, "I", 40, INK, bold=True); f.text(315, 245, "R", 40, INK, bold=True)
    f.text(260, 305, "V ＝ I × R　　I ＝ V ÷ R　　R ＝ V ÷ I", 20, INK, bold=True)
    f.text(260, 345, "求めたいものを指で隠す", 17, MUTED)
    f.text(260, 380, "例：10Ω に 2A → 2×10 ＝ 20V", 20, RED, bold=True)
    f.save("fig_ohm")


def fig_power():
    f = Fig()
    f.text(260, 50, "P ＝ V × I", 30, INK, bold=True)
    f.text(260, 95, "V ＝ I×R を代入 →　P ＝ I² × R", 20, MUTED)
    f.text(260, 125, "I ＝ V÷R を代入 →　P ＝ V² ÷ R", 20, MUTED)
    f.box(60, 160, 400, 60, "電圧を求める：V² ＝ P × R → 平方根", fill="#FFF6E5", stroke=AMBER, size=20, bold=True)
    f.text(80, 265, "25Ω・100W", 20, INK, anchor="start"); f.text(230, 265, "→ 100×25 ＝ 2500 → √2500 ＝ 50V", 20, RED, anchor="start", bold=True)
    f.text(80, 310, "4Ω・100W", 20, INK, anchor="start"); f.text(230, 310, "→ 100×4 ＝ 400 → √400 ＝ 20V", 20, RED, anchor="start", bold=True)
    f.text(260, 370, "よく出る平方根：√100=10 √400=20 √2500=50", 17, MUTED)
    f.save("fig_power")


def fig_resistors():
    f = Fig()
    f.text(130, 40, "直列", 22, INK, bold=True)
    f.line(30, 90, 60, 90); f.resistor(60, 90, 60, "20Ω"); f.line(120, 90, 150, 90); f.resistor(150, 90, 60, "20Ω"); f.line(210, 90, 240, 90)
    f.text(130, 140, "足し算 ＝ 40Ω", 22, INK, bold=True)
    f.text(390, 40, "並列", 22, RED, bold=True)
    f.line(300, 90, 340, 90); f.line(340, 60, 340, 120); f.line(340, 60, 360, 60); f.resistor(360, 60, 60, "20Ω"); f.line(420, 60, 440, 60)
    f.line(340, 120, 360, 120); f.resistor(360, 120, 60, ""); f.text(390, 145, "20Ω", 18, MUTED); f.line(420, 120, 440, 120)
    f.line(440, 60, 440, 120); f.line(440, 90, 480, 90)
    f.text(390, 190, "同じ値2本 → 半分 ＝ 10Ω", 22, RED, bold=True)
    f.text(260, 260, "並列の一般式", 18, MUTED)
    f.text(260, 300, "1/R ＝ 1/R₁ ＋ 1/R₂　　（2本なら 積÷和）", 21, INK)
    f.text(260, 350, "並列にすると必ず元の値より小さくなる", 18, MUTED)
    f.save("fig_resistors")


def fig_lc():
    f = Fig()
    f.line(60, 320, 480, 320); f.line(60, 60, 60, 330)
    f.text(470, 350, "周波数 →", 16, MUTED); f.text(60, 45, "電流の通しやすさ", 16, MUTED, anchor="start")
    f.parts.append(f'<path d="M70 300 C 150 120 300 80 470 70" fill="none" stroke="{BLUE}" stroke-width="4"/>')
    f.text(330, 120, "コンデンサ", 20, BLUE, bold=True); f.text(330, 145, "高い周波数ほど通す", 16, BLUE)
    f.parts.append(f'<path d="M70 80 C 150 260 300 300 470 310" fill="none" stroke="{RED}" stroke-width="4"/>')
    f.text(330, 260, "コイル", 20, RED, bold=True); f.text(330, 285, "高い周波数ほど通さない", 16, RED)
    f.cap(110, 70); f.text(150, 76, "直流は通さない", 15, BLUE, anchor="start")
    f.coil(90, 215, 4, 8)
    f.text(260, 385, "コンデンサは高い周波数に強い、コイルは弱い", 18, INK, bold=True)
    f.save("fig_lc")


def fig_bands():
    f = Fig()
    bands = [("MF", "300kHz〜3MHz", "中波放送", MUTED), ("HF", "3〜30MHz", "7・21MHz（短波）", INK), ("VHF", "30〜300MHz", "50・144MHz", RED), ("UHF", "300MHz〜3GHz", "430MHz", BLUE)]
    for i, (n, r, ex, c) in enumerate(bands):
        y = 50 + i * 62
        f.box(40, y, 90, 48, n, fill="#fff" if c != RED else "#FFF6E5", stroke=c, size=22, color=c, bold=True)
        f.text(150, y + 30, r, 20, INK, anchor="start"); f.text(340, y + 30, ex, 17, c, anchor="start")
    f.text(260, 330, "区切りは 3・30・300・3000", 20, INK, bold=True)
    f.text(260, 365, "144MHz は 30〜300 の間 → VHF", 20, RED, bold=True)
    f.save("fig_bands")


# ================= 受信機 =================
def fig_superhet():
    f = Fig()
    f.line(40, 60, 40, 30, w=3); f.line(25, 30, 55, 30, w=3); f.line(40, 60, 40, 90)
    stages = [("高周波\n増幅", 30, 80), ("周波数\n変換", 130, 80), ("中間周波\n増幅", 230, 80), ("検波", 330, 80), ("低周波\n増幅", 410, 80)]
    for i, (lab, x, _) in enumerate(stages):
        w = 90 if i < 4 else 80
        f.box(x, 90, w, 70, lab, size=16, fill="#FFF6E5" if i in (1, 2) else "#fff", stroke=AMBER if i in (1, 2) else INK)
        if i < 4:
            f.arrow(x + w, 125, stages[i + 1][1], 125)
    f.line(490, 125, 505, 125); f.parts.append(f'<polygon points="505,110 505,140 515,150 515,100" fill="{INK}"/>')
    f.box(130, 210, 90, 60, "局部発振器", size=15); f.arrow(175, 210, 175, 160)
    f.text(175, 300, "受信 145MHz、局発 155.7MHz", 15, MUTED)
    f.text(175, 322, "→ 差の 10.7MHz ＝ 中間周波数（IF）", 16, RED, bold=True)
    f.text(275, 195, "選択度を決める", 14, RED); f.text(75, 195, "S/N を良くする", 14, RED)
    f.text(260, 375, "いつも同じ IF に変換してから増幅する", 18, INK)
    f.save("fig_superhet")


def fig_image():
    f = Fig()
    f.line(40, 250, 480, 250); f.text(470, 275, "周波数 →", 15, MUTED)
    for x, lab, val, c in [(120, "受信したい", "145.0", RED), (260, "局部発振", "155.7", INK), (400, "影像周波数", "166.4", BLUE)]:
        f.parts.append(f'<rect x="{x-12}" y="120" width="24" height="130" fill="{c}"/>')
        f.text(x, 100, lab, 17, c, bold=True); f.text(x, 280, val, 20, c, bold=True); f.text(x, 302, "MHz", 13, MUTED)
    f.arrow(135, 60, 245, 60, MUTED, 2); f.arrow(245, 60, 135, 60, MUTED, 2); f.text(190, 50, "IF 10.7", 15, MUTED)
    f.arrow(275, 60, 385, 60, MUTED, 2); f.arrow(385, 60, 275, 60, MUTED, 2); f.text(330, 50, "IF 10.7", 15, MUTED)
    f.text(260, 345, "局発の反対側、同じ IF 差の周波数も受信されてしまう", 16, INK)
    f.text(260, 380, "影像 ＝ 受信 ＋ IF×2 ＝ 145 ＋ 21.4 ＝ 166.4MHz", 19, RED, bold=True)
    f.save("fig_image")


def fig_rx_circuits():
    f = Fig()
    rows = [("AGC", "電波の強弱に関係なく出力を一定に", RED), ("スケルチ", "無信号時の「ザー」を消す", BLUE), ("リミッタ", "FM の振幅をそろえて雑音を除く", INK),
            ("周波数弁別器", "周波数の変化 → 振幅の変化（FM の検波）", RED), ("クラリファイヤ", "SSB の周波数を微調整して明りょう度↑", BLUE)]
    for i, (n, d, c) in enumerate(rows):
        y = 40 + i * 68
        f.box(30, y, 150, 50, n, fill="#FFF6E5", stroke=c, size=18, color=c, bold=True)
        f.text(195, y + 31, d, 16, INK, anchor="start")
    f.text(260, 385, "問題文のキーワードで回路名を選ぶ", 17, MUTED)
    f.save("fig_rx_circuits")


# ================= 送信機 =================
def fig_am_fm():
    f = Fig()
    f.text(80, 45, "音声", 16, MUTED); f.wave(30, 45, 100, 12, 1.5, MUTED)
    f.text(60, 120, "AM", 22, RED, bold=True); f.wave(100, 120, 380, 40, 20, RED, env=lambda t: 0.5 + 0.5 * math.sin(2 * math.pi * 1.5 * t))
    f.parts.append(f'<path d="M100 {120-20} ' + " ".join(f"L{100+i} {120-40*(0.5+0.5*math.sin(2*math.pi*1.5*i/380)):.1f}" for i in range(0, 381, 4)) + f'" fill="none" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="4,4"/>')
    f.text(260, 185, "振幅（高さ）が音声の形に変わる", 16, RED)
    f.text(60, 260, "FM", 22, BLUE, bold=True); f.wave(100, 260, 380, 40, 14, BLUE, fm=lambda t: 3 * (1 - math.cos(2 * math.pi * 1.5 * t)))
    f.text(260, 325, "周波数（間隔）が変わる。振幅は一定", 16, BLUE)
    f.text(260, 375, "AM：振幅 ／ FM：周波数", 22, INK, bold=True)
    f.save("fig_am_fm")


def fig_ssb():
    f = Fig()
    f.line(40, 170, 480, 170); f.text(470, 195, "周波数 →", 14, MUTED)
    f.text(120, 40, "AM（A3E）", 20, INK, bold=True)
    f.parts.append(f'<rect x="118" y="60" width="6" height="110" fill="{INK}"/>'); f.text(121, 190, "搬送波", 13, MUTED)
    f.parts.append(f'<polygon points="70,170 116,170 116,120" fill="{MUTED}"/>'); f.text(90, 190, "下側波帯", 12, MUTED)
    f.parts.append(f'<polygon points="126,170 172,170 126,120" fill="{MUTED}"/>'); f.text(150, 190, "上側波帯", 12, MUTED)
    f.arrow(70, 90, 172, 90, MUTED, 2); f.arrow(172, 90, 70, 90, MUTED, 2); f.text(121, 80, "帯域幅", 13, MUTED)
    f.text(380, 40, "SSB（J3E）", 20, RED, bold=True)
    f.line(378, 60, 378, 170, MUTED, 2, dash="5,5"); f.text(378, 190, "搬送波なし", 13, MUTED)
    f.parts.append(f'<polygon points="384,170 430,170 384,120" fill="{RED}"/>'); f.text(407, 190, "上側波帯だけ", 12, RED)
    f.arrow(384, 90, 430, 90, RED, 2); f.arrow(430, 90, 384, 90, RED, 2); f.text(407, 80, "約半分", 13, RED, bold=True)
    f.box(40, 240, 130, 60, "平衡変調器", size=17); f.arrow(170, 270, 210, 270)
    f.box(210, 240, 130, 60, "帯域フィルタ", size=17); f.arrow(340, 270, 380, 270); f.text(430, 276, "SSB波", 17, RED, bold=True)
    f.text(105, 325, "搬送波 ± 信号波を出す", 14, MUTED); f.text(275, 325, "片側だけ通す", 14, MUTED)
    f.text(260, 375, "1506.5 ＋ 1.5 ＝ 1508.0kHz（上側波帯）", 19, RED, bold=True)
    f.save("fig_ssb")


def fig_modulation():
    f = Fig()
    f.wave(40, 150, 300, 60, 18, INK, env=lambda t: 2 / 3 + 1 / 3 * math.sin(2 * math.pi * 1.5 * t))
    f.line(40, 150, 340, 150, LINE, 1)
    f.line(350, 150, 350, 90, RED, 2); f.line(345, 90, 355, 90, RED, 2); f.line(345, 150, 355, 150, RED, 2); f.text(365, 125, "最大 90V", 16, RED, anchor="start", bold=True)
    f.line(400, 150, 400, 110, BLUE, 2); f.line(395, 110, 405, 110, BLUE, 2); f.text(415, 135, "搬送波 60V", 16, BLUE, anchor="start", bold=True)
    f.line(40, 90, 340, 90, RED, 1.5, dash="5,5"); f.line(40, 110, 340, 110, BLUE, 1.5, dash="5,5")
    f.text(260, 250, "変調度 ＝（最大振幅 − 搬送波）÷ 搬送波", 20, INK, bold=True)
    f.text(260, 285, "＝（90 − 60）÷ 60 ＝ 0.5 → 50%", 22, RED, bold=True)
    f.text(260, 340, "100% を超えると過変調", 18, INK)
    f.text(260, 368, "→ ひずみ・占有周波数帯幅が広がって混信", 17, RED)
    f.save("fig_modulation")


def fig_tx_block():
    f = Fig()
    f.text(260, 35, "直接FM送信機の構成", 20, INK, bold=True)
    blocks = [("音声", 20, "#fff", INK), ("IDC", 100, "#FFF6E5", RED), ("電圧制御\n発振器", 180, "#fff", INK), ("緩衝\n増幅器", 270, "#fff", INK), ("電力\n増幅器", 350, "#FFF6E5", RED), ("LPF", 430, "#fff", INK)]
    for i, (lab, x, fill, c) in enumerate(blocks):
        w = 70 if i in (0, 1, 5) else 80
        f.box(x, 60, w, 60, lab, fill=fill, stroke=c, size=14, color=c, bold=(c == RED))
        if i < 5:
            f.arrow(x + w, 90, blocks[i + 1][1], 90)
    f.text(135, 145, "周波数偏移を制限", 13, RED); f.text(390, 145, "出力を大きく", 13, RED)
    rows = [("ALC", "SSB：電力増幅器の入力を制限 → ひずまない", RED), ("IDC", "FM：周波数偏移を一定値以下に", BLUE), ("VOX", "声の有無で送信⇔受信を自動切替", INK)]
    for i, (n, d, c) in enumerate(rows):
        y = 190 + i * 60
        f.box(40, y, 90, 44, n, fill="#FFF6E5", stroke=c, size=18, color=c, bold=True)
        f.text(145, y + 28, d, 16, INK, anchor="start")
    f.text(260, 385, "AGC・スケルチは受信機の回路", 16, MUTED)
    f.save("fig_tx_block")


# ================= 法規 =================
def fig_law_purpose():
    f = Fig()
    f.text(260, 40, "電波法 第1条（目的）", 22, INK, bold=True)
    f.box(40, 70, 440, 120, "", fill="#FFF6E5", stroke=AMBER)
    f.text(260, 105, "電波の", 20, INK); f.text(260, 135, "公平かつ能率的な利用", 26, RED, bold=True); f.text(260, 170, "を確保することによって", 18, INK)
    f.box(40, 210, 440, 70, "", fill="#FFF6E5", stroke=AMBER)
    f.text(260, 240, "公共の福祉を増進", 26, RED, bold=True); f.text(260, 268, "することを目的とする", 16, INK)
    f.text(260, 320, "✕ 有効な利用　✕ 電気通信事業の発展", 17, MUTED)
    f.text(260, 348, "✕ 通信の秘密　✕ 無線技術の向上", 17, MUTED)
    f.text(260, 385, "キーワード 2 つがそろった選択肢を選ぶ", 17, RED)
    f.save("fig_law_purpose")


def fig_station_def():
    f = Fig()
    f.box(40, 40, 440, 100, "", fill="#FFF6E5", stroke=RED)
    f.text(260, 70, "無線局 ＝ 無線設備 ＋ 操作する者（総体）", 20, RED, bold=True)
    f.text(260, 100, "ただし 受信のみを目的とするものは含まない", 17, INK)
    f.text(260, 125, "（設備だけでなく人も含む）", 14, MUTED)
    f.box(40, 160, 440, 80, "", fill="#fff", stroke=INK)
    f.text(260, 190, "無線設備 ＝ 電波を送り、又は受けるための電気的設備", 17, INK, bold=True)
    f.text(260, 218, "（人は含まない）", 14, MUTED)
    f.box(40, 260, 440, 80, "", fill="#fff", stroke=INK)
    f.text(260, 290, "送信設備 ＝ 送信装置 ＋ 送信空中線系", 17, INK, bold=True)
    f.text(260, 318, "（電波を送る設備）", 14, MUTED)
    f.text(260, 380, "「設備＋人」なら無線局、「設備だけ」なら無線設備", 16, RED)
    f.save("fig_station_def")


def fig_amateur_def():
    f = Fig()
    f.text(260, 40, "アマチュア業務の定義", 22, INK, bold=True)
    f.text(260, 85, "金銭上の利益のためでなく", 22, RED, bold=True)
    f.text(260, 120, "もっぱら 個人的な無線技術の興味 によって行う", 19, INK)
    for i, (t, x) in enumerate([("自己訓練", 100), ("通　信", 260), ("技術的研究", 420)]):
        f.box(x - 65, 160, 130, 60, t, fill="#FFF6E5", stroke=AMBER, size=20, color=RED, bold=True)
        if i < 2:
            f.text(x + 82, 197, "＋", 22, INK)
    f.text(260, 260, "の業務", 20, INK)
    f.text(260, 310, "3 点セット。穴埋めは「技術的研究」", 18, RED)
    f.text(260, 350, "✕ 公共の福祉（→ 電波法の目的）　✕ 災害の救援　✕ 放送", 15, MUTED)
    f.save("fig_amateur_def")


def fig_license_timeline():
    f = Fig()
    f.line(40, 200, 480, 200, INK, 4)
    f.parts.append(f'<circle cx="60" cy="200" r="9" fill="{INK}"/>'); f.text(60, 240, "免許の日", 16, INK)
    f.parts.append(f'<circle cx="460" cy="200" r="9" fill="{RED}"/>'); f.text(460, 240, "満了", 16, RED, bold=True)
    f.arrow(70, 150, 450, 150, MUTED, 2); f.arrow(450, 150, 70, 150, MUTED, 2)
    f.text(260, 138, "有効期間 5 年", 24, RED, bold=True)
    f.parts.append(f'<rect x="300" y="190" width="147" height="20" fill="{AMBER}" opacity="0.8"/>')
    f.text(373, 310, "再免許の申請期間", 18, RED, bold=True)
    f.text(373, 336, "満了前 1 か月以上 1 年以内", 18, INK)
    f.text(373, 358, "（改正前の問題では 6 か月以内）", 14, MUTED)
    f.line(447, 205, 447, 260, MUTED, 1.5, dash="4,4"); f.text(447, 275, "1 か月前", 12, MUTED)
    f.line(300, 205, 300, 260, MUTED, 1.5, dash="4,4"); f.text(300, 275, "1 年前", 12, MUTED)
    f.text(260, 388, "無線従事者の免許証には有効期間がない", 14, MUTED)
    f.save("fig_license_timeline")


def fig_permission():
    f = Fig()
    f.text(140, 40, "前もって 許可 が必要", 20, RED, bold=True)
    f.box(30, 60, 220, 70, "無線設備の\n設置場所を変える", fill="#FFF6E5", stroke=RED, size=17, color=INK, bold=True)
    f.box(30, 145, 220, 70, "無線設備の\n変更の工事", fill="#FFF6E5", stroke=RED, size=17, color=INK, bold=True)
    f.text(140, 245, "＝ 設備をいじる・動かす", 15, RED)
    f.text(380, 40, "許可ではない", 20, MUTED, bold=True)
    for i, t in enumerate(["免許人の氏名の変更（届出）", "無線局の運用の休止", "無線局の廃止（届出）", "免許状の訂正"]):
        f.text(380, 85 + i * 40, t, 16, MUTED)
    f.line(270, 60, 270, 240, LINE, 2)
    f.text(260, 330, "「許可が必要なのはどれか」→ 上の 2 つのどちらか", 16, INK)
    f.save("fig_permission")


def fig_emission():
    f = Fig()
    for i, (ch, col) in enumerate([("J", RED), ("3", BLUE), ("E", GREEN)]):
        x = 110 + i * 150
        f.box(x - 45, 30, 90, 80, ch, fill="#fff", stroke=col, size=48, color=col, bold=True)
    f.text(110, 140, "変調の方式", 17, RED, bold=True); f.text(260, 140, "信号の性質", 17, BLUE, bold=True); f.text(410, 140, "情報の種類", 17, GREEN, bold=True)
    for i, t in enumerate(["A ＝ AM（両側波帯）", "J ＝ SSB（抑圧搬送波・単側波帯）", "F ＝ FM（周波数変調）", "H 全搬送波 / R 低減搬送波"]):
        f.text(20, 175 + i * 26, t, 14, RED if i < 3 else MUTED, anchor="start")
    for i, t in enumerate(["3 ＝ アナログ", "　　単一チャネル", "1 ＝ デジタル（モールス）", "2 ＝ デジタル・副搬送波"]):
        f.text(215, 175 + i * 26, t, 14, BLUE if i < 2 else MUTED, anchor="start")
    for i, t in enumerate(["E ＝ 電話（音声）", "A ＝ 電信（モールス）", "D ＝ データ"]):
        f.text(375, 175 + i * 26, t, 14, GREEN if i == 0 else MUTED, anchor="start")
    f.line(30, 295, 490, 295, LINE, 1.5)
    f.text(260, 325, "A3E ＝ AM 電話　　J3E ＝ SSB 電話", 18, INK, bold=True)
    f.text(260, 355, "F3E ＝ FM 電話　　A1A ＝ モールス電信", 18, INK, bold=True)
    f.save("fig_emission")


def fig_bandwidth():
    f = Fig()
    f.line(40, 250, 480, 250, INK, 3)
    f.parts.append(f'<rect x="120" y="100" width="280" height="150" fill="#EAF6EE" stroke="{GREEN}" stroke-width="2"/>')
    f.text(260, 90, "動作することを許された周波数帯（バンド）", 15, GREEN, bold=True)
    f.parts.append(f'<polygon points="200,250 240,150 280,250" fill="{BLUE}" opacity="0.8"/>')
    f.arrow(200, 275, 280, 275, BLUE, 2); f.arrow(280, 275, 200, 275, BLUE, 2); f.text(240, 300, "占有周波数帯幅", 14, BLUE, bold=True)
    f.text(240, 135, "OK", 16, BLUE, bold=True)
    f.parts.append(f'<polygon points="370,250 400,150 430,250" fill="{RED}" opacity="0.8"/>')
    f.text(430, 135, "はみ出し ✕", 16, RED, bold=True)
    f.text(260, 350, "幅の分まで含めてバンドの中に収める", 18, INK, bold=True)
    f.text(260, 380, "穴埋め：「占有する［周波数帯幅］」", 16, RED)
    f.save("fig_bandwidth")


def fig_4ama_range():
    f = Fig()
    f.line(40, 200, 480, 200, INK, 3)
    segs = [(40, 150, "8MHz 以下", "10W", GREEN, "1.9・3.5・7"), (150, 260, "8〜21MHz", "✕", MUTED, "10・14・18"),
            (260, 340, "21〜30MHz", "10W", GREEN, "21・24・28"), (340, 480, "30MHz 超", "20W", RED, "50・144・430")]
    for x1, x2, lab, pw, col, ex in segs:
        f.parts.append(f'<rect x="{x1}" y="150" width="{x2-x1}" height="50" fill="{col}" opacity="{0.25 if col == MUTED else 0.85}"/>')
        f.text((x1 + x2) / 2, 183, pw, 22 if pw != "✕" else 26, "#fff" if col != MUTED else RED, bold=True)
        f.text((x1 + x2) / 2, 230, lab, 15, INK, bold=True); f.text((x1 + x2) / 2, 252, ex + " MHz帯", 12, MUTED)
    for x, v in [(150, "8"), (260, "21"), (340, "30")]:
        f.line(x, 140, x, 205, INK, 2); f.text(x, 130, v + "MHz", 14, INK, bold=True)
    f.text(260, 60, "4アマの操作範囲", 22, INK, bold=True)
    f.text(260, 92, "20W は 30MHz 超だけ。10・14・18MHz 帯は操作できない", 15, RED)
    f.text(260, 320, "モールス符号による通信操作は含まれない", 16, MUTED)
    f.save("fig_4ama_range")


def fig_return_days():
    f = Fig()
    f.text(140, 45, "無線従事者 免許証（人）", 18, RED, bold=True)
    f.box(40, 65, 200, 90, "10 日以内\nに返納", fill="#FFF6E5", stroke=RED, size=22, color=RED, bold=True)
    for i, t in enumerate(["・免許の取消しを受けた", "・再交付後に見つかった", "・死亡／失そうの宣告"]):
        f.text(40, 185 + i * 24, t, 14, INK, anchor="start")
    f.text(140, 275, "有効期間は無い", 14, MUTED)
    f.text(380, 45, "無線局 免許状（局）", 18, BLUE, bold=True)
    f.box(280, 65, 200, 90, "1 か月以内\nに返納", fill="#EEF3FA", stroke=BLUE, size=22, color=BLUE, bold=True)
    f.text(280, 185, "・免許が効力を失った", 14, INK, anchor="start")
    f.text(280, 209, "・有効期間は 5 年", 14, INK, anchor="start")
    f.text(280, 245, "免許記録の写しは", 14, MUTED, anchor="start"); f.text(280, 265, "返納でなく「廃棄」", 14, MUTED, anchor="start")
    f.text(260, 340, "免許証 10 日 ／ 免許状 1 か月", 22, INK, bold=True)
    f.text(260, 372, "運用停止・従事停止は 3 か月以内", 15, MUTED)
    f.save("fig_return_days")


def fig_call_reply():
    f = Fig()

    def row(y, title, items, col):
        f.text(20, y - 30, title, 18, col, bold=True, anchor="start")
        x = 20
        for lab, n, hi in items:
            w = 150
            f.box(x, y - 15, w, 56, "", fill="#FFF6E5" if hi else "#fff", stroke=col if hi else INK)
            f.text(x + w / 2, y + 8, lab, 14, INK); f.text(x + w / 2, y + 32, n, 18, RED if hi else INK, bold=True)
            x += w + 12
            if x < 470:
                f.arrow(x - 12, y + 13, x, y + 13, MUTED, 2)
    row(80, "呼出し（呼ぶ側）", [("相手局の呼出符号", "3 回以下", False), ("こちらは", "1 回", False), ("自局の呼出符号", "3 回以下", True)], INK)
    row(220, "応答（呼ばれた側）", [("相手局の呼出符号", "3 回以下", False), ("こちらは", "1 回", False), ("自局の呼出符号", "1 回", True)], BLUE)
    f.text(260, 330, "違いは最後の自局：呼出し 3 回以下 ／ 応答 1 回", 18, RED, bold=True)
    f.text(260, 365, "順番はどちらも「相手が先、自分が後」", 15, MUTED)
    f.save("fig_call_reply")


def fig_test_wave():
    f = Fig()
    steps = [("① 聴守", "その周波数で受信して\n混信を与えないことを確認", GREEN), ("② 擬似空中線回路", "できればダミーロードで\n電波を出さずに調整", INK), ("③ 試験電波", "「本日は晴天なり」＋呼出符号\n10 秒 を超えない", RED)]
    for i, (t, d, c) in enumerate(steps):
        y = 40 + i * 110
        f.box(30, y, 150, 80, t, fill="#FFF6E5" if c == RED else "#fff", stroke=c, size=17, color=c, bold=True)
        lines = d.split("\n")
        f.text(200, y + 32, lines[0], 16, INK, anchor="start"); f.text(200, y + 58, lines[1], 16, RED if c == RED else INK, anchor="start", bold=(c == RED))
        if i < 2:
            f.arrow(105, y + 80, 105, y + 110, MUTED, 2)
    f.text(260, 385, "確かめるのは「混信を与えないこと」（他局が通信していないこと、ではない）", 13, MUTED)
    f.save("fig_test_wave")


def fig_ops_numbers():
    f = Fig()
    rows = [("3 分", "応答がないとき、呼出しを再開するまであける間隔", RED), ("10 分", "長時間の送信中、「こちらは」＋自局の呼出符号を送る間隔", RED),
            ("直ちに", "通信上の誤りを知ったときの訂正", BLUE), ("反復", "反復を求めるとき：「反復」の次に箇所を示す", BLUE), ("さようなら", "通信が終了したとき", BLUE)]
    for i, (n, d, c) in enumerate(rows):
        y = 40 + i * 66
        f.box(30, y, 120, 50, n, fill="#FFF6E5", stroke=c, size=19, color=c, bold=True)
        f.text(165, y + 31, d, 14, INK, anchor="start")
    f.save("fig_ops_numbers")


def fig_emergency():
    f = Fig()
    f.text(260, 40, "非常通信", 22, INK, bold=True)
    f.text(260, 72, "有線通信が使えない／著しく困難なときの通信", 15, MUTED)
    f.text(120, 120, "呼出し", 18, INK, bold=True)
    f.box(30, 140, 90, 50, "非常", fill="#FFF6E5", stroke=RED, size=18, color=RED, bold=True); f.text(75, 210, "3 回", 18, RED, bold=True)
    f.arrow(120, 165, 140, 165, MUTED, 2); f.box(140, 140, 120, 50, "呼出事項", size=16)
    f.text(75, 235, "前に", 14, MUTED)
    f.text(390, 120, "応答", 18, BLUE, bold=True)
    f.box(280, 140, 120, 50, "応答事項", size=16); f.arrow(400, 165, 420, 165, MUTED, 2)
    f.box(420, 140, 80, 50, "非常", fill="#EEF3FA", stroke=BLUE, size=18, color=BLUE, bold=True); f.text(460, 210, "1 回", 18, BLUE, bold=True)
    f.text(460, 235, "次に", 14, MUTED)
    f.text(260, 290, "前に 3 回 ／ 後ろに 1 回", 20, INK, bold=True)
    f.text(260, 330, "混信防止の規定の例外（遭難・緊急・安全・非常）", 15, MUTED)
    f.text(260, 360, "行ったら 総務大臣に報告", 16, RED, bold=True)
    f.save("fig_emergency")


def fig_prohibited():
    f = Fig()
    rows = [("秘密の保護", "特定の相手方への通信を傍受して 漏らす・窃用 ✕（聞くこと自体は ✕ではない）"),
            ("暗語", "使ってはならない（略語・Q符号・通話表は OK）"),
            ("他人の依頼", "頼まれた通報は送信できない（非常時の救助・救援用は例外）"),
            ("放送に支障", "テレビ・ラジオに支障 → 速やかにその周波数での発射を中止")]
    for i, (t, d) in enumerate(rows):
        y = 40 + i * 80
        f.box(30, y, 130, 56, t, fill="#FFF6E5", stroke=RED, size=16, color=RED, bold=True)
        f.text(175, y + 34, d, 13, INK, anchor="start")
    f.save("fig_prohibited")


def fig_sanction():
    f = Fig()
    f.text(260, 40, "電波法に違反したとき", 20, INK, bold=True)
    f.box(40, 70, 200, 110, "運用の停止\n3 か月以内", fill="#FFF6E5", stroke=RED, size=20, color=RED, bold=True)
    f.box(280, 70, 200, 110, "運用時間・周波数\n空中線電力の制限", fill="#fff", stroke=INK, size=16)
    f.text(260, 215, "無線従事者の業務従事停止も 3 か月以内", 15, MUTED)
    f.box(40, 250, 440, 60, "不正な手段で免許を受けた → 免許の取消し", fill="#FDECEA", stroke=RED, size=17, color=RED, bold=True)
    f.text(260, 350, "✕ 従事者の解任命令　✕ 相手方の制限　✕ 電波の型式の制限", 14, MUTED)
    f.save("fig_sanction")


def fig_report():
    f = Fig()
    f.box(30, 60, 190, 70, "非常通信を\n行った", size=17)
    f.box(30, 170, 190, 70, "違反して運用する\n無線局を見つけた", size=17)
    f.arrow(220, 95, 300, 145, RED, 3); f.arrow(220, 205, 300, 160, RED, 3)
    f.box(300, 110, 190, 90, "総務大臣に\n報告", fill="#FFF6E5", stroke=RED, size=22, color=RED, bold=True)
    f.text(260, 290, "報告先はいつも総務大臣", 20, INK, bold=True)
    f.text(260, 325, "✕ 警察署　✕ 市町村長　✕ 都道府県知事　✕ 中央防災会議会長", 13, MUTED)
    f.text(260, 360, "宇宙無線通信・国際通信・試験の通信は報告不要", 13, MUTED)
    f.save("fig_report")


def fig_license_place():
    f = Fig()
    f.parts.append(f'<polygon points="80,150 180,70 280,150" fill="{INK}"/><rect x="100" y="150" width="160" height="120" fill="#fff" stroke="{INK}" stroke-width="3"/>')
    f.box(140, 190, 80, 50, "免許状", fill="#FFF6E5", stroke=RED, size=15, color=RED, bold=True)
    f.text(180, 300, "無線設備の常置場所", 18, RED, bold=True); f.text(180, 322, "（ふだん無線機を置いてある所）", 13, MUTED)
    f.parts.append(f'<rect x="340" y="170" width="140" height="60" rx="10" fill="{MUTED}"/><rect x="365" y="140" width="80" height="40" rx="8" fill="{MUTED}"/>')
    f.parts.append(f'<circle cx="370" cy="235" r="14" fill="{INK}"/><circle cx="450" cy="235" r="14" fill="{INK}"/>')
    f.line(410, 140, 410, 100, INK, 3)
    f.text(410, 300, "移動運用", 16, INK); f.text(410, 322, "免許状を持ち歩く必要はない", 13, MUTED)
    f.text(260, 375, "移動するアマチュア局の免許状 → 常置場所に備え付け", 15, INK, bold=True)
    f.save("fig_license_place")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    n = 0
    for name, fn in list(globals().items()):
        if name.startswith("fig_") and callable(fn):
            fn()
            n += 1
    print(f"{n} figures -> {OUT}")
