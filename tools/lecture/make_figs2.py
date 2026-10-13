"""「過去問攻略」講義用の図（SVG）を生成する。  python tools/lecture/make_figs2.py
描画部品は make_figs.py の Fig を使う。図を直したいときはここを編集して実行し直す。
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_figs import Fig, INK, MUTED, RED, AMBER, GREEN, BLUE, LINE  # noqa: E402

PALE = "#FFF6E5"
PALE_B = "#EEF3FA"
PALE_G = "#EAF6EE"
PALE_R = "#FDECEA"


# ---------- 共通の部品 ----------
def rows(f, items, x=24, y=30, h=56, gap=12, lw=150, size=16, dsize=14):
    """[(ラベル, 説明, 色)] を縦に並べた表"""
    for i, (lab, desc, col) in enumerate(items):
        yy = y + i * (h + gap)
        f.box(x, yy, lw, h, lab, fill=PALE, stroke=col, size=size, color=col, bold=True)
        for j, line in enumerate(desc.split("\n")):
            n = len(desc.split("\n"))
            f.text(x + lw + 14, yy + h / 2 + 5 - (n - 1) * 9 + j * 19, line, dsize, INK, anchor="start")


def check(f, x, y, ok=True):
    col = GREEN if ok else RED
    f.parts.append(f'<circle cx="{x}" cy="{y}" r="13" fill="{col}"/>')
    if ok:
        f.parts.append(f'<polyline points="{x-6},{y} {x-1},{y+5} {x+7},{y-5}" fill="none" stroke="#fff" stroke-width="3"/>')
    else:
        f.line(x - 6, y - 6, x + 6, y + 6, "#fff", 3); f.line(x + 6, y - 6, x - 6, y + 6, "#fff", 3)


def antenna(f, x, y, h=40):
    f.line(x, y, x, y - h, INK, 3); f.line(x - 14, y - h, x + 14, y - h, INK, 3)
    f.line(x - 9, y - h + 10, x + 9, y - h + 10, INK, 3)


def flow(f, labels, y=90, x0=14, w=88, gap=12, h=56, hi=(), size=13):
    """横一列のブロック図。hi に入れた番号を強調"""
    xs = []
    for i, lab in enumerate(labels):
        x = x0 + i * (w + gap)
        xs.append(x)
        f.box(x, y, w, h, lab, fill=PALE if i in hi else "#fff", stroke=RED if i in hi else INK,
              size=size, color=RED if i in hi else INK, bold=i in hi)
        if i < len(labels) - 1:
            f.arrow(x + w, y + h / 2, x + w + gap, y + h / 2, INK, 2)
    return xs


# ================= 基礎 =================
def fig2_materials():
    f = Fig()
    cols = [("導体", "電気をよく通す", "銅・アルミニウム・鉛", BLUE), ("半導体", "中くらい", "シリコン・ゲルマニウム", AMBER), ("絶縁体", "通さない", "磁器・ガラス・ゴム", RED)]
    for i, (n, d, ex, c) in enumerate(cols):
        x = 20 + i * 168
        f.box(x, 40, 150, 150, "", fill="#fff", stroke=c)
        f.text(x + 75, 78, n, 24, c, bold=True); f.text(x + 75, 112, d, 15, INK); f.text(x + 75, 150, ex, 13, MUTED)
    # がいし
    for k in range(4):
        f.parts.append(f'<ellipse cx="430" cy="{230 + k * 22}" rx="34" ry="9" fill="#fff" stroke="{RED}" stroke-width="3"/>')
    f.line(430, 215, 430, 310, RED, 3)
    f.text(300, 255, "高圧の絶縁 ＝ 磁器（がいし）", 17, RED, bold=True, anchor="end")
    f.box(20, 330, 480, 54, "", fill=PALE_B, stroke=BLUE)
    f.text(260, 352, "半導体：温度 ↑ → 抵抗 ↓ → 電流 ↑", 18, BLUE, bold=True)
    f.text(260, 374, "（金属とは逆）", 13, MUTED)
    f.save("fig2_materials")


def fig2_rms():
    f = Fig()
    f.line(40, 170, 480, 170, LINE, 2)
    f.wave(40, 170, 440, 100, 1.5, BLUE)
    f.line(40, 70, 480, 70, RED, 1.5, dash="6,5"); f.text(470, 60, "最大値 140V", 15, RED, anchor="end", bold=True)
    y_rms = 170 - 100 / math.sqrt(2)
    f.line(40, y_rms, 480, y_rms, GREEN, 2.5, dash="10,5"); f.text(470, y_rms - 8, "実効値 ≒ 100V", 15, GREEN, anchor="end", bold=True)
    f.box(40, 300, 440, 70, "", fill=PALE, stroke=AMBER)
    f.text(260, 330, "実効値 ＝ 最大値 ÷ √2（≒1.41）", 20, INK, bold=True)
    f.text(260, 358, "140 ÷ 1.41 ≒ 100V", 18, RED, bold=True)
    f.save("fig2_rms")


def fig2_electromagnet():
    f = Fig()
    f.parts.append(f'<rect x="120" y="110" width="260" height="60" rx="6" fill="#C9CFD6" stroke="{INK}" stroke-width="2"/>')
    f.text(250, 146, "鉄心（磁性体）", 15, INK, bold=True)
    for k in range(9):
        x = 135 + k * 28
        f.parts.append(f'<path d="M{x} 100 C {x+20} 100 {x+20} 180 {x} 180" fill="none" stroke="{AMBER}" stroke-width="4"/>')
    f.text(100, 146, "N", 26, RED, bold=True); f.text(400, 146, "S", 26, BLUE, bold=True)
    f.text(250, 70, "磁界を強くする", 18, INK, bold=True)
    for i, (t, ok) in enumerate([("巻数を多く", True), ("電流を大きく", True), ("鉄心を入れる", True), ("断面積を大きく", False)]):
        y = 225 + i * 40
        check(f, 150, y, ok); f.text(175, y + 6, t, 18, GREEN if ok else RED, anchor="start", bold=True)
    f.text(390, 270, "鉄心を入れると", 15, MUTED); f.text(390, 295, "インダクタンス", 15, MUTED); f.text(390, 322, "大きくなる", 18, RED, bold=True)
    f.save("fig2_electromagnet")


def fig2_cap_combo():
    f = Fig()
    f.text(130, 34, "抵抗", 22, INK, bold=True); f.text(390, 34, "コンデンサ", 22, BLUE, bold=True)
    f.line(260, 20, 260, 300, LINE, 2)
    for i, (k, r, c) in enumerate([("直列", "足し算", "半分（積÷和）"), ("並列", "半分（積÷和）", "足し算")]):
        y = 80 + i * 110
        f.text(260, y - 14, k, 16, MUTED, bold=True)
        f.box(30, y, 200, 70, r, fill=PALE if r == "足し算" else "#fff", stroke=AMBER if r == "足し算" else INK, size=19, bold=r == "足し算")
        f.box(290, y, 200, 70, c, fill=PALE_B if c == "足し算" else "#fff", stroke=BLUE if c == "足し算" else INK, size=19, color=BLUE if c == "足し算" else INK, bold=c == "足し算")
    f.text(260, 330, "10μF と 15μF の並列 → 25μF", 17, BLUE, bold=True)
    f.text(260, 362, "30μF 2個の直列 → 15μF", 17, BLUE, bold=True)
    f.save("fig2_cap_combo")


def fig2_ratio():
    f = Fig()
    f.box(30, 40, 460, 90, "", fill=PALE_B, stroke=BLUE)
    f.text(260, 72, "I ＝ V ÷ R", 24, BLUE, bold=True)
    f.text(260, 108, "抵抗 2倍 → 電流 1/2倍　　抵抗 1/2倍 → 電流 2倍", 16, INK)
    f.box(30, 150, 460, 100, "", fill=PALE, stroke=RED)
    f.text(260, 184, "P ＝ V² ÷ R", 24, RED, bold=True)
    f.text(260, 222, "電圧 4倍 → 電力 4 × 4 ＝ 16倍", 19, RED, bold=True)
    f.box(30, 270, 460, 90, "", fill="#fff", stroke=INK)
    f.text(260, 302, "100V で 500W の負荷の抵抗は？", 16, INK)
    f.text(260, 336, "R ＝ V² ÷ P ＝ 10000 ÷ 500 ＝ 20Ω", 19, INK, bold=True)
    f.save("fig2_ratio")


def fig2_fet_map():
    f = Fig()
    f.text(140, 40, "FET", 24, BLUE, bold=True); f.text(380, 40, "トランジスタ", 24, RED, bold=True)
    for i, (a, b) in enumerate([("ゲート", "ベース"), ("ドレイン", "コレクタ"), ("ソース", "エミッタ")]):
        y = 80 + i * 90
        f.box(60, y, 160, 60, a, fill=PALE_B, stroke=BLUE, size=20, color=BLUE, bold=True)
        f.box(300, y, 160, 60, b, fill=PALE, stroke=RED, size=20, color=RED, bold=True)
        f.arrow(225, y + 30, 295, y + 30, INK, 3); f.arrow(295, y + 30, 225, y + 30, INK, 3)
    f.text(260, 370, "入口の制御 ＝ ゲート/ベース、出口側 ＝ ドレイン/コレクタ", 14, MUTED)
    f.save("fig2_fet_map")


# ================= 電子回路 =================
def fig2_amp_class():
    f = Fig()
    f.line(60, 300, 480, 300, INK, 2); f.line(60, 300, 60, 40, INK, 2)
    f.text(470, 325, "V_BE", 14, MUTED); f.text(80, 40, "I_C", 14, MUTED, anchor="start")
    pts = " ".join(f"{60+i},{300 - max(0,(i-140))**1.6/9:.1f}" for i in range(0, 421, 4))
    f.parts.append(f'<polyline points="{pts}" fill="none" stroke="{INK}" stroke-width="3"/>')
    for x, lab, col in [(330, "A級", GREEN), (200, "B級", BLUE), (130, "C級", RED)]:
        yy = 300 - max(0, (x - 60 - 140)) ** 1.6 / 9
        f.parts.append(f'<circle cx="{x}" cy="{yy:.1f}" r="8" fill="{col}"/>')
        if x > 200:
            f.text(x + 14, yy + 6, lab, 17, col, bold=True, anchor="start")
        else:
            f.text(x, 285, lab, 17, col, bold=True)
    f.box(75, 50, 210, 120, "", fill=PALE, stroke=AMBER)
    f.text(180, 78, "効率：C ＞ B ＞ A", 16, INK, bold=True)
    f.text(180, 106, "ひずみ：C ＞ B ＞ A", 16, INK, bold=True)
    f.text(180, 140, "A級は入力なしでも", 13, MUTED); f.text(180, 158, "常に電流が流れる", 13, GREEN, bold=True)
    f.text(260, 370, "動作点（●）の位置で A・B・C が決まる", 15, MUTED)
    f.save("fig2_amp_class")


def fig2_osc_stable():
    f = Fig()
    flow(f, ["水晶\n発振器", "緩衝\n増幅器", "逓倍器\nなど"], y=60, x0=40, w=120, gap=40, h=70, hi=(1,), size=16)
    f.text(220, 155, "結合は「疎」", 15, RED, bold=True)
    f.text(260, 200, "周波数が変動する原因", 17, INK, bold=True)
    for i, t in enumerate(["負荷の変動", "電源電圧の変動", "周囲温度の変化"]):
        f.box(30 + i * 158, 220, 145, 46, t, fill=PALE_R, stroke=RED, size=15, color=RED)
    f.box(30, 290, 460, 44, "最も関係が少ない ＝ 内部雑音の変動", fill="#fff", stroke=MUTED, size=15, color=MUTED)
    f.text(260, 370, "✕「次段との結合を密にする」", 16, RED, bold=True)
    f.save("fig2_osc_stable")


def fig2_hfe():
    f = Fig()
    f.circle(150, 170, 60)
    f.line(115, 140, 115, 200, w=5); f.line(60, 170, 115, 170)
    f.line(115, 155, 160, 125); f.line(160, 125, 160, 80); f.line(115, 185, 160, 215); f.line(160, 215, 160, 260)
    f.arrow(132, 197, 158, 213, INK, 3)
    f.text(40, 150, "I_B", 16, BLUE, bold=True); f.text(180, 80, "I_C", 16, RED, bold=True, anchor="start")
    f.box(260, 50, 240, 60, "I_B：3mA → 4mA\n変化 1mA", fill=PALE_B, stroke=BLUE, size=15, color=BLUE)
    f.box(260, 125, 240, 60, "I_C：180mA → 240mA\n変化 60mA", fill=PALE_R, stroke=RED, size=15, color=RED)
    f.box(30, 290, 460, 80, "", fill=PALE, stroke=AMBER)
    f.text(260, 320, "電流増幅率 ＝ I_C の変化 ÷ I_B の変化", 17, INK, bold=True)
    f.text(260, 352, "60 ÷ 1 ＝ 60", 22, RED, bold=True)
    f.save("fig2_hfe")


def fig2_spectrum():
    f = Fig()

    def axis(y):
        f.line(30, y, 490, y, INK, 2)
    for i, (name, kind, col) in enumerate([("DSB（A3E）", "dsb", INK), ("SSB（J3E）", "ssb", RED), ("FM（F3E）", "fm", BLUE)]):
        y = 110 + i * 115
        axis(y); f.text(30, y - 72, name, 16, col, bold=True, anchor="start")
        if kind == "dsb":
            f.parts.append(f'<rect x="258" y="{y-70}" width="5" height="70" fill="{INK}"/>')
            f.parts.append(f'<polygon points="210,{y} 255,{y} 255,{y-40}" fill="{MUTED}"/><polygon points="266,{y} 311,{y} 266,{y-40}" fill="{MUTED}"/>')
            f.text(400, y - 20, "搬送波＋上下の側波帯", 13, MUTED)
        elif kind == "ssb":
            f.line(260, y - 70, 260, y, MUTED, 2, dash="4,4")
            f.parts.append(f'<polygon points="266,{y} 311,{y} 266,{y-40}" fill="{RED}"/>')
            f.text(400, y - 20, "片方の側波帯だけ（最も狭い）", 13, RED, bold=True)
        else:
            f.parts.append(f'<rect x="150" y="{y-45}" width="220" height="45" fill="{BLUE}" opacity="0.35"/>')
            f.text(260, y - 18, "2 ×（Δf ＋ fm）", 14, BLUE, bold=True)
            f.text(440, y - 20, "最も広い", 13, BLUE, bold=True)
    f.text(260, 392, "例：Δf 5kHz・fm 3kHz → 2 × 8 ＝ 16kHz", 15, INK, bold=True)
    f.save("fig2_spectrum")


def fig2_mixer():
    f = Fig()
    f.circle(250, 140, 50, fill=PALE, stroke=AMBER); f.text(250, 148, "混合器", 17, INK, bold=True)
    f.arrow(60, 140, 200, 140, BLUE, 3); f.text(120, 128, "信号 f", 16, BLUE, bold=True)
    f.box(195, 250, 110, 50, "局部発振器\nfo", size=14); f.arrow(250, 250, 250, 190, INK, 2)
    f.arrow(300, 140, 420, 110, RED, 3); f.text(440, 108, "f ＋ fo", 16, RED, bold=True, anchor="start")
    f.arrow(300, 140, 420, 170, GREEN, 3); f.text(440, 178, "f − fo", 16, GREEN, bold=True, anchor="start")
    f.text(440, 202, "← 中間周波数", 13, GREEN, anchor="start")
    f.box(30, 330, 460, 50, "直線検波：入力が「大きい」とき直線的（小さい入力は ✕）", fill="#fff", stroke=INK, size=14)
    f.save("fig2_mixer")


def fig2_mod_calc():
    f = Fig()
    f.wave(30, 150, 280, 90, 14, INK, env=lambda t: 1 / 1.6 + 0.6 / 1.6 * math.sin(2 * math.pi * 1.5 * t))
    f.line(30, 150, 310, 150, LINE, 1)
    f.line(330, 150, 330, 60, RED, 2); f.text(340, 104, "最大 240V", 14, RED, anchor="start", bold=True)
    f.line(400, 150, 400, 94, BLUE, 2); f.text(408, 130, "搬送波", 13, BLUE, anchor="start"); f.text(408, 148, "150V", 13, BLUE, anchor="start", bold=True)
    items = [("150V・信号90V", "90 ÷ 150 ＝ 60%"), ("150V・変調度40%", "信号 ＝ 150 × 0.4 ＝ 60V"), ("150V・変調度60%", "最大 ＝ 150 ＋ 90 ＝ 240V")]
    for i, (a, b) in enumerate(items):
        y = 255 + i * 46
        f.box(20, y, 190, 38, a, fill=PALE_B, stroke=BLUE, size=14, color=BLUE)
        f.text(225, y + 25, b, 16, RED, anchor="start", bold=True)
    f.save("fig2_mod_calc")


# ================= 送信機 =================
def fig2_tx_chain():
    f = Fig()
    xs = flow(f, ["発振器", "緩衝\n増幅器", "周波数\n逓倍器", "励振\n増幅器", "電力\n増幅器"], y=60, x0=8, w=88, gap=14, h=60, hi=(1, 2), size=14)
    antenna(f, 505, 90, 40); f.line(482, 90, 505, 90, INK, 2)
    f.text(xs[1] + 44, 145, "後段の影響を防ぐ", 13, RED, bold=True)
    f.text(xs[2] + 44, 165, "整数倍にする", 13, RED, bold=True)
    f.box(30, 210, 460, 70, "", fill=PALE, stroke=AMBER)
    f.text(260, 238, "×2 と ×3 の逓倍器を通る → 全体で ×6", 16, INK, bold=True)
    f.text(260, 266, "送信周波数 fc ＝ 6 × fo（fo ＝ fc の 1/6）", 16, RED, bold=True)
    f.text(260, 320, "送信機の条件：周波数が安定・帯域が狭い・スプリアスが小さい", 14, MUTED)
    f.save("fig2_tx_chain")


def fig2_ptt():
    f = Fig()
    f.parts.append(f'<rect x="60" y="60" width="90" height="170" rx="40" fill="#fff" stroke="{INK}" stroke-width="3"/>')
    f.parts.append(f'<rect x="150" y="110" width="18" height="50" rx="4" fill="{RED}"/>')
    f.text(185, 140, "PTT", 16, RED, bold=True, anchor="start")
    f.text(105, 260, "マイク", 15, MUTED)
    f.box(270, 60, 220, 60, "押す → 送信状態", fill=PALE_R, stroke=RED, size=18, color=RED, bold=True)
    f.text(380, 140, "アンテナが送信機に接続", 14, INK)
    f.box(270, 170, 220, 50, "離す → 受信状態", fill="#fff", stroke=INK, size=16)
    f.box(30, 300, 460, 70, "", fill=PALE, stroke=AMBER)
    f.text(260, 328, "擬似負荷（ダミーロード）の目的", 15, INK)
    f.text(260, 356, "調整中に電波を外部に出さないため", 18, RED, bold=True)
    f.save("fig2_ptt")


def fig2_ssb_tx():
    f = Fig()
    flow(f, ["音声", "平衡\n変調器", "帯域\nフィルタ", "周波数\n混合器", "電力増幅\n（ALC）"], y=50, x0=8, w=90, gap=12, h=60, hi=(1, 2), size=13)
    f.text(155, 135, "搬送波を除く", 13, RED, bold=True); f.text(257, 135, "片側を取り出す", 13, RED, bold=True)
    f.box(30, 175, 460, 50, "✕ 周波数逓倍器で所要の周波数を得る（SSB は逓倍しない）", fill=PALE_R, stroke=RED, size=14, color=RED)
    f.box(30, 235, 460, 50, "✕ DSB より回路構成が簡単（実際は複雑）", fill=PALE_R, stroke=RED, size=14, color=RED)
    f.text(260, 315, "正しい特長", 15, GREEN, bold=True)
    f.text(260, 343, "帯域が狭い ・ 声があるときだけ電波が出る ・ 雑音が少ない", 14, GREEN)
    f.save("fig2_ssb_tx")


def fig2_indirect_fm():
    f = Fig()
    f.box(10, 160, 90, 56, "水晶\n発振器", size=13)
    f.box(10, 50, 90, 56, "音声", size=14)
    f.box(125, 50, 90, 56, "IDC回路", fill=PALE, stroke=RED, size=14, color=RED, bold=True)
    f.arrow(100, 78, 125, 78, INK, 2)
    f.box(240, 105, 90, 56, "位相\n変調器", fill=PALE, stroke=RED, size=14, color=RED, bold=True)
    f.arrow(215, 78, 285, 105, INK, 2); f.arrow(100, 188, 240, 140, INK, 2)
    f.box(355, 105, 90, 56, "周波数\n逓倍器", fill=PALE, stroke=RED, size=14, color=RED, bold=True)
    f.arrow(330, 133, 355, 133, INK, 2); f.arrow(445, 133, 470, 133, INK, 2); antenna(f, 490, 133, 40); f.line(470, 133, 490, 133, INK, 2)
    f.text(400, 190, "逓倍数を大きく → 偏移も大きく", 13, RED, bold=True)
    f.box(20, 240, 480, 48, "間接FM に使わないもの ＝ 平衡変調器（SSB用）", fill="#fff", stroke=INK, size=15)
    f.box(20, 300, 480, 60, "FM は自動車の点火雑音に強い\n（雑音は振幅に乗り、FM は振幅を使わない）", fill=PALE_B, stroke=BLUE, size=14, color=BLUE)
    f.save("fig2_indirect_fm")


# ================= 受信機 =================
def fig2_selectivity():
    f = Fig()
    antenna(f, 22, 95, 40); f.line(22, 95, 22, 120, INK, 2)
    xs = flow(f, ["高周波\n増幅", "周波数\n変換", "中間周波\n増幅", "検波", "低周波\n増幅"], y=90, x0=10, w=88, gap=13, h=60, hi=(0, 2), size=13)
    f.box(xs[1], 200, 88, 46, "局部\n発振器", size=12); f.arrow(xs[1] + 44, 200, xs[1] + 44, 150, INK, 2)
    f.box(10, 280, 240, 90, "", fill=PALE_R, stroke=RED)
    f.text(130, 306, "影像周波数（遠い）", 15, RED, bold=True); f.text(130, 334, "→ 高周波増幅器", 17, RED, bold=True)
    f.text(130, 358, "（周波数変換の前で落とす）", 12, MUTED)
    f.box(270, 280, 240, 90, "", fill=PALE_B, stroke=BLUE)
    f.text(390, 306, "近接周波数（すぐ隣）", 15, BLUE, bold=True); f.text(390, 334, "→ 中間周波増幅器", 17, BLUE, bold=True)
    f.text(390, 358, "（帯域フィルタで分ける）", 12, MUTED)
    f.save("fig2_selectivity")


def fig2_image_fix():
    f = Fig()
    f.text(260, 34, "影像混信を減らす方法", 18, INK, bold=True)
    for i, (t, ok) in enumerate([("中間周波数を高くする", True), ("高周波増幅部の選択度を高くする", True), ("アンテナにウェーブトラップを入れる", True), ("中間周波増幅部の利得を下げる", False)]):
        y = 70 + i * 42
        check(f, 50, y, ok); f.text(75, y + 6, t, 16, GREEN if ok else RED, anchor="start", bold=not ok)
    f.text(260, 260, "高周波増幅部があると", 16, INK, bold=True)
    f.text(260, 290, "感度↑・影像混信↓・S/N↑", 16, GREEN, bold=True)
    f.box(30, 310, 460, 60, "✕「局部発振器の出力が空中線から放射されやすい」\n（実際は放射されにくくなる）", fill=PALE_R, stroke=RED, size=14, color=RED)
    f.save("fig2_image_fix")


def fig2_noise_check():
    f = Fig()
    f.box(170, 60, 180, 120, "受信機", size=20)
    f.circle(195, 200, 10); f.text(195, 232, "ANT", 13, MUTED)
    f.circle(325, 200, 10); f.text(325, 232, "E", 13, MUTED)
    f.parts.append(f'<path d="M195 210 C 195 270 325 270 325 210" fill="none" stroke="{RED}" stroke-width="4"/>')
    f.text(260, 288, "導線でつなぐ（短絡）", 16, RED, bold=True)
    f.text(90, 120, "雑音が消える", 14, GREEN, bold=True); f.text(90, 140, "→ 外来雑音", 14, GREEN)
    f.text(430, 120, "雑音が残る", 14, BLUE, bold=True); f.text(430, 140, "→ 受信機内部", 14, BLUE)
    f.box(30, 320, 460, 50, "S メータが指示するもの ＝ 検波電流", fill=PALE, stroke=AMBER, size=16, bold=True)
    f.save("fig2_noise_check")


def fig2_ssb_rx():
    f = Fig()
    flow(f, ["中間周波\n増幅", "検波器", "低周波\n増幅"], y=60, x0=30, w=120, gap=40, h=60, size=15)
    f.box(190, 170, 120, 60, "復調用\n局部発振器", fill=PALE, stroke=RED, size=14, color=RED, bold=True)
    f.arrow(250, 170, 250, 120, RED, 2)
    f.text(250, 255, "搬送波の代わりを補う", 13, RED)
    f.box(340, 170, 160, 60, "クラリファイヤ\n（RIT）", fill=PALE_B, stroke=BLUE, size=14, color=BLUE, bold=True)
    f.arrow(340, 200, 310, 200, BLUE, 2)
    f.text(420, 252, "局発の周波数を変えて", 12, BLUE); f.text(420, 270, "明りょう度を良く", 12, BLUE, bold=True)
    f.box(30, 310, 460, 54, "SSB 受信機に不要 ＝ スピーチクリッパ（送信側の回路）", fill="#fff", stroke=INK, size=15)
    f.save("fig2_ssb_rx")


def fig2_fm_rx():
    f = Fig()
    flow(f, ["中間周波\n増幅", "振幅\n制限器", "周波数\n弁別器", "低周波\n増幅"], y=60, x0=14, w=104, gap=24, h=60, hi=(1, 2), size=14)
    f.box(270, 170, 110, 50, "スケルチ", fill=PALE, stroke=RED, size=16, color=RED, bold=True)
    f.arrow(325, 120, 325, 170, INK, 2); f.arrow(380, 195, 430, 120, INK, 2)
    rows(f, [("振幅制限器", "振幅を一定に → 振幅変調成分（雑音）を除く", BLUE),
             ("周波数弁別器", "周波数の変化 → 振幅の変化（FM の復調）", RED),
             ("スケルチ", "電波がないときの雑音を消す", GREEN)], y=245, h=40, gap=8, lw=120, size=14, dsize=13)
    f.save("fig2_fm_rx")


# ================= 電波障害 =================
def fig2_interference_names():
    f = Fig()
    antenna(f, 60, 200, 80); f.text(60, 230, "アマチュア局", 14, MUTED)
    for i, (n, t, c) in enumerate([("TVI", "テレビ", RED), ("BCI", "ラジオ", BLUE), ("アンプI", "アンプ", AMBER), ("テレホンI", "電話機", GREEN)]):
        y = 50 + i * 70
        f.arrow(90, 140, 230, y + 25, MUTED, 2)
        f.box(240, y, 120, 50, t, size=16)
        f.text(380, y + 32, n, 20, c, bold=True, anchor="start")
    f.box(30, 330, 460, 50, "強い電波で受信機の中で変調される ＝ 混変調", fill=PALE, stroke=AMBER, size=16, bold=True)
    f.save("fig2_interference_names")


def fig2_harmonic_calc():
    f = Fig()
    for i, (a, b, ans) in enumerate([("28MHz", "84MHz（FM放送）", "84 ÷ 28 ＝ 3"), ("50MHz", "150MHz", "150 ÷ 50 ＝ 3")]):
        y = 40 + i * 110
        f.box(20, y, 120, 56, a, fill="#fff", stroke=INK, size=18, bold=True)
        f.arrow(140, y + 28, 230, y + 28, RED, 3)
        f.box(230, y, 170, 56, b, fill=PALE_R, stroke=RED, size=15, color=RED)
        f.text(260, y + 85, ans + " → 第3高調波", 17, RED, bold=True)
    f.box(20, 275, 480, 95, "", fill=PALE_B, stroke=BLUE)
    f.text(260, 305, "夏の昼間・50MHz・数百km先の「同じ周波数帯」に混信", 14, BLUE)
    f.text(260, 340, "→ スポラジックE層（高調波ではない）", 18, BLUE, bold=True)
    f.save("fig2_harmonic_calc")


def fig2_tx_rx_filters():
    f = Fig()
    f.text(130, 34, "送信側", 20, RED, bold=True); f.text(390, 34, "受信側", 20, BLUE, bold=True)
    f.line(260, 20, 260, 380, LINE, 2)
    f.box(20, 60, 90, 50, "送信機", size=15); f.arrow(110, 85, 130, 85, INK, 2)
    f.box(130, 60, 80, 50, "LPF", fill=PALE_R, stroke=RED, size=20, color=RED, bold=True)
    f.line(210, 85, 235, 85, INK, 2); antenna(f, 240, 85, 36)
    f.text(130, 140, "高調波を出さない", 14, RED, bold=True)
    for i, t in enumerate(["遮へいを厳重に", "接地を完全に", "正しく調整", "TVアンテナから離す"]):
        f.text(30, 180 + i * 28, "・" + t, 14, INK, anchor="start")
    antenna(f, 290, 85, 36); f.line(290, 85, 310, 85, INK, 2)
    f.box(310, 60, 80, 50, "HPF", fill=PALE_B, stroke=BLUE, size=20, color=BLUE, bold=True)
    f.arrow(390, 85, 410, 85, INK, 2); f.box(410, 60, 90, 50, "テレビ", size=15)
    f.text(390, 140, "短波の基本波を落とす", 14, BLUE, bold=True)
    f.text(390, 170, "TV電波（高い周波数）は通す", 13, MUTED)
    f.box(20, 320, 480, 50, "✕ 送信側に「TV電波を通しやすいフィルタ」", fill="#fff", stroke=RED, size=15, color=RED)
    f.save("fig2_tx_rx_filters")


def fig2_noise_sources():
    f = Fig()
    f.text(140, 34, "雑音を出す", 18, RED, bold=True); f.text(390, 34, "出さない", 18, GREEN, bold=True)
    for i, t in enumerate(["電気溶接機", "高周波ミシン", "自動車の点火栓"]):
        f.box(40, 55 + i * 58, 200, 46, t, fill=PALE_R, stroke=RED, size=16, color=RED)
    f.box(290, 55, 200, 46, "電波時計", fill=PALE_G, stroke=GREEN, size=18, color=GREEN, bold=True)
    f.text(390, 125, "電波を受けるだけ", 13, MUTED)
    f.text(260, 260, "BCI の原因：過変調・寄生振動・送電線に接近", 15, INK, bold=True)
    f.text(260, 290, "✕ アンテナ結合回路の結合度が疎", 15, RED)
    f.box(30, 315, 460, 50, "障害を与えるおそれが最も低い ＝ 送信電力が低下したとき", fill=PALE, stroke=AMBER, size=14)
    f.save("fig2_noise_sources")


# ================= 電源 =================
def fig2_batteries():
    f = Fig()
    for i, (n, v, note, col) in enumerate([("ニッケルカドミウム", "1.2V", "充放電できる・大電流", RED), ("マンガン乾電池", "1.5V", "充電できない", MUTED), ("鉛蓄電池", "2V", "車のバッテリー", MUTED), ("リチウムイオン", "約3.7V", "継ぎ足し充電できる", BLUE)]):
        y = 30 + i * 62
        f.box(20, y, 200, 50, n, fill=PALE if i == 0 else "#fff", stroke=col, size=15, color=col, bold=i == 0)
        f.text(240, y + 32, v, 20, col, bold=True, anchor="start"); f.text(330, y + 32, note, 13, MUTED, anchor="start")
    f.text(260, 300, "ニカド：放電終止電圧 1.0V・内部抵抗が小さい", 14, RED)
    f.box(30, 320, 460, 50, "同じ乾電池を並列 → 使用時間を長くする（電圧はそのまま）", fill=PALE_B, stroke=BLUE, size=14, color=BLUE)
    f.save("fig2_batteries")


def fig2_battery_series():
    f = Fig()
    for i in range(3):
        x = 70 + i * 130
        f.box(x, 60, 100, 70, "6V\n60Ah", fill="#fff", stroke=INK, size=16, bold=True)
        if i < 2:
            f.line(x + 100, 95, x + 130, 95, INK, 3)
    f.text(260, 40, "3個を直列", 16, MUTED)
    f.box(60, 160, 400, 70, "", fill=PALE, stroke=AMBER)
    f.text(260, 190, "電圧 ＝ 6 × 3 ＝ 18V", 19, RED, bold=True)
    f.text(260, 218, "容量 ＝ 60Ah のまま", 17, INK, bold=True)
    f.box(60, 260, 400, 80, "", fill=PALE_B, stroke=BLUE)
    f.text(260, 290, "容量 Ah ＝ 電流 × 時間", 16, BLUE)
    f.text(260, 322, "30Ah を 3A で → 30 ÷ 3 ＝ 10時間", 18, BLUE, bold=True)
    f.text(260, 372, "並列なら：電圧そのまま・容量が足し算", 14, MUTED)
    f.save("fig2_battery_series")


def fig2_rectifier():
    f = Fig()
    f.text(130, 34, "半波整流", 18, INK, bold=True); f.text(390, 34, "全波整流", 18, RED, bold=True)
    f.line(20, 140, 240, 140, LINE, 1); f.wave(20, 140, 220, 60, 2, INK, rect=True)
    pts = " ".join(f"{280+i},{140 - abs(math.sin(i/220*2*math.pi*2))*60:.1f}" for i in range(0, 221, 2))
    f.line(280, 140, 500, 140, LINE, 1); f.parts.append(f'<polyline points="{pts}" fill="none" stroke="{RED}" stroke-width="2.5"/>')
    f.text(130, 180, "山が1周期に1回", 14, MUTED); f.text(390, 180, "山が1周期に2回", 14, RED)
    f.box(20, 210, 220, 60, "50Hz → 50Hz", fill="#fff", stroke=INK, size=18)
    f.box(280, 210, 220, 60, "50Hz → 100Hz", fill=PALE_R, stroke=RED, size=20, color=RED, bold=True)
    f.box(20, 300, 480, 70, "ダイオードの三角の向き ＝ 電流の向き\n電流が負荷に流れ込む側が ＋（正）", fill=PALE, stroke=AMBER, size=15)
    f.save("fig2_rectifier")


def fig2_transformer():
    f = Fig()
    f.parts.append(f'<rect x="200" y="50" width="120" height="160" fill="none" stroke="{MUTED}" stroke-width="10"/>')
    for k in range(5):
        f.parts.append(f'<path d="M195 {70+k*26} C 170 {70+k*26} 170 {92+k*26} 195 {92+k*26}" fill="none" stroke="{BLUE}" stroke-width="4"/>')
    for k in range(5):
        f.parts.append(f'<path d="M325 {70+k*26} C 350 {70+k*26} 350 {92+k*26} 325 {92+k*26}" fill="none" stroke="{RED}" stroke-width="4"/>')
    f.text(110, 130, "一次", 18, BLUE, bold=True); f.text(410, 130, "二次", 18, RED, bold=True)
    f.box(30, 240, 460, 44, "電圧の比 ＝ 巻数の比", fill=PALE, stroke=AMBER, size=18, bold=True)
    f.text(260, 318, "1 : 3 に 100V → 二次 300V", 17, INK, bold=True)
    f.text(260, 352, "100V → 5V（20:1）、二次10回 → 一次 200回", 16, RED, bold=True)
    f.save("fig2_transformer")


# ================= 空中線 =================
def fig2_patterns():
    f = Fig()
    cx = [90, 260, 430]
    f.circle(cx[0], 140, 70, fill=PALE_B, stroke=BLUE); f.parts.append(f'<circle cx="{cx[0]}" cy="140" r="5" fill="{INK}"/>')
    f.parts.append(f'<ellipse cx="{cx[1]}" cy="95" rx="38" ry="48" fill="{PALE_R}" stroke="{RED}" stroke-width="2.5"/><ellipse cx="{cx[1]}" cy="185" rx="38" ry="48" fill="{PALE_R}" stroke="{RED}" stroke-width="2.5"/>')
    f.line(cx[1] - 30, 140, cx[1] + 30, 140, INK, 4)
    f.parts.append(f'<path d="M{cx[2]} 230 C {cx[2]-45} 170 {cx[2]-30} 50 {cx[2]} 40 C {cx[2]+30} 50 {cx[2]+45} 170 {cx[2]} 230 Z" fill="{PALE}" stroke="{AMBER}" stroke-width="2.5"/>')
    f.parts.append(f'<circle cx="{cx[2]}" cy="230" r="5" fill="{INK}"/>')
    f.text(cx[0], 245, "全方向（円）", 15, BLUE, bold=True); f.text(cx[0], 268, "垂直ダイポール", 12, MUTED); f.text(cx[0], 286, "GP・ホイップ", 12, MUTED)
    f.text(cx[1], 268, "8の字", 15, RED, bold=True); f.text(cx[1], 290, "水平ダイポール", 12, MUTED)
    f.text(cx[2], 268, "一方向", 15, AMBER, bold=True); f.text(cx[2], 290, "八木（最も鋭い）", 12, MUTED)
    f.box(30, 320, 460, 50, "陸上移動局 ＝ 水平面内で全方向性（無指向性）", fill=PALE_B, stroke=BLUE, size=15, color=BLUE, bold=True)
    f.save("fig2_patterns")


def fig2_quarter_wave():
    f = Fig()
    f.parts.append(f'<rect x="40" y="300" width="200" height="12" fill="#B8C2CC"/>')
    f.line(140, 300, 140, 80, INK, 5)
    pts = " ".join(f"{140 + math.cos((300-y)/220*math.pi/2)*60:.1f},{y}" for y in range(80, 301, 5))
    f.parts.append(f'<polyline points="{pts}" fill="none" stroke="{RED}" stroke-width="3" stroke-dasharray="5,4"/>')
    f.text(215, 92, "先端で 0", 13, RED, anchor="start", bold=True); f.text(210, 290, "底部で最大", 13, RED, anchor="start", bold=True)
    f.arrow(80, 300, 80, 80, MUTED, 2); f.text(60, 190, "λ/4", 16, MUTED)
    rows(f, [("高さ 10m", "固有波長 ＝ 10 × 4 ＝ 40m", BLUE), ("接地抵抗", "小さいほど効率が良い（大は ✕）", RED), ("同調", "固有周波数の奇数倍にも同調", INK)], x=270, y=60, h=60, gap=16, lw=100, size=13, dsize=12)
    f.save("fig2_quarter_wave")


def fig2_feedline():
    f = Fig()
    f.box(20, 60, 100, 60, "送信機", size=16)
    f.line(120, 90, 400, 90, INK, 6); antenna(f, 420, 90, 50); f.line(400, 90, 420, 90, INK, 3)
    f.text(260, 75, "給電線", 15, MUTED)
    for i, (t, ok) in enumerate([("損失が少ない", True), ("外部の影響を受けない", True), ("特性インピーダンスが一定", True), ("給電線から電波が放射される", False)]):
        y = 160 + i * 38
        check(f, 60, y, ok); f.text(85, y + 6, t, 16, GREEN if ok else RED, anchor="start", bold=not ok)
    f.box(30, 320, 460, 50, "放射に役立つ ＝ 放射抵抗（接地・導体・漏れ抵抗は損失）", fill=PALE, stroke=AMBER, size=14, bold=True)
    f.save("fig2_feedline")


def fig2_antenna_calc():
    f = Fig()
    f.box(30, 20, 460, 50, "波長（m）＝ 300 ÷ 周波数（MHz）", fill=PALE, stroke=AMBER, size=19, bold=True)
    rows(f, [("10m", "300 ÷ 10 ＝ 30MHz", INK), ("7MHz 半波長", "43m の半分 ≒ 21m", INK), ("28MHz 放射器", "10.7m の半分 ≒ 5m", INK)], y=85, h=44, gap=10, lw=140, size=14, dsize=15)
    f.box(30, 260, 460, 110, "", fill=PALE_B, stroke=BLUE)
    f.text(260, 290, "放射電力 ＝ 電流² × 73Ω（半波長ダイポール）", 15, BLUE, bold=True)
    f.text(260, 322, "10W にするには I ＝ √(10÷73) ≒ 0.37A", 15, INK)
    f.text(260, 352, "0.2A なら P ＝ 0.04 × 73 ≒ 3W", 15, INK)
    f.save("fig2_antenna_calc")


# ================= 電波伝搬 =================
def fig2_polarization():
    f = Fig()
    f.line(40, 200, 480, 200, LINE, 2)
    pts = " ".join(f"{40+i},{200 - math.sin(i/440*2*math.pi*2.5)*80:.1f}" for i in range(0, 441, 4))
    f.parts.append(f'<polyline points="{pts}" fill="none" stroke="{RED}" stroke-width="3"/>')
    pts2 = " ".join(f"{40+i+math.sin(i/440*2*math.pi*2.5)*40:.1f},{200 + math.sin(i/440*2*math.pi*2.5)*28:.1f}" for i in range(0, 441, 4))
    f.parts.append(f'<polyline points="{pts2}" fill="none" stroke="{BLUE}" stroke-width="2.5" stroke-dasharray="6,4"/>')
    f.text(60, 100, "電界", 16, RED, bold=True); f.text(60, 270, "磁界", 16, BLUE, bold=True)
    f.text(400, 100, "互いに直角", 16, INK, bold=True)
    f.box(30, 300, 220, 70, "電界が大地と平行\n→ 水平偏波", fill=PALE_R, stroke=RED, size=15, color=RED, bold=True)
    f.box(270, 300, 220, 70, "電界が大地と垂直\n→ 垂直偏波", fill=PALE_B, stroke=BLUE, size=15, color=BLUE, bold=True)
    f.save("fig2_polarization")


def fig2_day_night():
    f = Fig()
    for i, (title, dens, col, sun) in enumerate([("昼", "電子密度 大", AMBER, True), ("夜", "電子密度 小", BLUE, False)]):
        x = 20 + i * 250
        f.box(x, 20, 230, 230, "", fill="#fff" if sun else "#1E2B38", stroke=col)
        f.text(x + 115, 50, title, 22, col if sun else "#fff", bold=True)
        if sun:
            f.parts.append(f'<circle cx="{x+190}" cy="48" r="16" fill="{AMBER}"/>')
        f.line(x + 10, 100, x + 220, 100, col, 6 if sun else 3, dash="12,6")
        f.text(x + 115, 90, dens, 14, col if sun else "#fff")
        if sun:
            f.parts.append(f'<path d="M{x+30} 240 L {x+115} 104 L {x+200} 240" fill="none" stroke="{RED}" stroke-width="3"/>')
            f.text(x + 115, 200, "21MHz 反射", 14, RED, bold=True)
        else:
            f.arrow(x + 60, 240, x + 110, 40, "#fff", 2); f.text(x + 160, 170, "21MHz", 13, "#fff"); f.text(x + 160, 188, "突き抜け", 13, "#fff")
            f.parts.append(f'<path d="M{x+30} 240 L {x+115} 106 L {x+200} 240" fill="none" stroke="{AMBER}" stroke-width="3"/>')
            f.text(x + 115, 230, "7MHz なら反射", 13, AMBER, bold=True)
    f.box(20, 270, 480, 100, "", fill=PALE, stroke=AMBER)
    f.text(260, 298, "突き抜けの減衰：高い周波数ほど 小", 15, INK, bold=True)
    f.text(260, 326, "反射の減衰：高い周波数ほど 大", 15, INK, bold=True)
    f.text(260, 354, "夜は低い周波数へ（21MHz → 7MHz）", 16, RED, bold=True)
    f.save("fig2_day_night")


def fig2_skip():
    f = Fig()
    f.parts.append(f'<rect x="0" y="260" width="520" height="40" fill="#E8EDF2"/>')
    f.line(10, 60, 510, 60, RED, 5, dash="14,8"); f.text(20, 50, "電離層", 15, RED, anchor="start", bold=True)
    antenna(f, 40, 260, 30)
    f.parts.append(f'<path d="M40 255 Q 110 250 170 258" fill="none" stroke="{GREEN}" stroke-width="4"/>')
    f.text(105, 240, "地表波", 14, GREEN, bold=True)
    f.parts.append(f'<path d="M45 240 L 240 64 L 430 258" fill="none" stroke="{BLUE}" stroke-width="3"/>')
    f.text(330, 150, "電離層反射波", 14, BLUE, bold=True)
    f.parts.append(f'<rect x="170" y="262" width="260" height="14" fill="{RED}" opacity="0.6"/>')
    f.text(300, 300, "不感地帯", 17, RED, bold=True)
    f.arrow(40, 325, 430, 325, INK, 2); f.arrow(430, 325, 40, 325, INK, 2)
    f.text(235, 318, "跳躍距離", 15, INK, bold=True)
    f.text(260, 370, "反射の条件：電子密度・入射角・周波数（送信電力は関係ない）", 13, MUTED)
    f.save("fig2_skip")


def fig2_vhf():
    f = Fig()
    f.parts.append(f'<rect x="0" y="250" width="520" height="40" fill="#E8EDF2"/>')
    antenna(f, 60, 250, 90); antenna(f, 460, 250, 90)
    f.arrow(70, 165, 450, 165, RED, 3); f.text(260, 155, "A：直接波", 16, RED, bold=True)
    f.parts.append(f'<path d="M70 175 L 260 248 L 450 175" fill="none" stroke="{BLUE}" stroke-width="3"/>')
    f.text(260, 230, "B：大地反射波", 15, BLUE, bold=True)
    f.text(260, 40, "VHF は見通し距離内（電離層は突き抜け）", 15, MUTED)
    f.box(20, 300, 230, 70, "アンテナを高く\n→ 見通し距離が延びる", fill=PALE_G, stroke=GREEN, size=14, color=GREEN, bold=True)
    f.box(270, 300, 230, 70, "✕ 放射角を高角度にする\n（空へ逃げる）", fill=PALE_R, stroke=RED, size=14, color=RED, bold=True)
    f.save("fig2_vhf")


def fig2_diffraction():
    f = Fig()
    f.parts.append(f'<rect x="0" y="230" width="520" height="40" fill="#E8EDF2"/>')
    f.parts.append(f'<polygon points="170,230 260,80 350,230" fill="#9AA5B1"/>')
    antenna(f, 50, 230, 50); antenna(f, 470, 230, 50)
    f.parts.append(f'<path d="M60 182 L 258 84 L 460 182" fill="none" stroke="{RED}" stroke-width="3" stroke-dasharray="7,5"/>')
    f.text(260, 66, "山頂で回り込む ＝ 回折", 16, RED, bold=True)
    rows(f, [("地表波", "大地の表面に沿って伝わる", GREEN), ("地上波", "直接波・大地反射波・地表波（電離層反射は ✕）", BLUE),
             ("フェージング", "✕「周波数が時間的に変動するため」", RED)], y=282, h=30, gap=6, lw=110, size=13, dsize=12)
    f.save("fig2_diffraction")


# ================= 測定 =================
def fig2_tester():
    f = Fig()
    f.parts.append(f'<rect x="30" y="30" width="190" height="230" rx="14" fill="#fff" stroke="{INK}" stroke-width="3"/>')
    f.parts.append(f'<path d="M60 120 A 70 70 0 0 1 190 120" fill="none" stroke="{MUTED}" stroke-width="2"/>')
    f.line(125, 150, 185, 112, RED, 3); f.text(185, 100, "0Ω", 14, RED, bold=True)
    f.circle(125, 210, 22, label="0Ω", size=12)
    f.line(90, 260, 110, 330, RED, 4); f.line(160, 260, 140, 330, BLUE, 4)
    f.parts.append(f'<circle cx="125" cy="334" r="9" fill="{AMBER}"/>'); f.text(125, 365, "先端を接触（短絡）", 14, AMBER, bold=True)
    for i, t in enumerate(["① 測定レンジを選ぶ", "② テスト棒を短絡する", "③ 0Ω 調整をする"]):
        f.box(260, 70 + i * 80, 240, 56, t, fill=PALE if i == 1 else "#fff", stroke=AMBER if i == 1 else INK, size=16, bold=True)
        if i < 2:
            f.arrow(380, 126 + i * 80, 380, 150 + i * 80, INK, 2)
    f.save("fig2_tester")


def fig2_dip():
    f = Fig()
    f.box(30, 40, 120, 70, "ディップ\nメータ", size=15); f.coil(150, 75, 4, 8)
    f.coil(240, 75, 4, 8); f.text(270, 120, "測る回路", 13, MUTED)
    f.text(210, 50, "疎", 18, RED, bold=True)
    f.line(360, 60, 360, 120, MUTED, 2); f.parts.append(f'<path d="M370 60 L 400 60 Q 420 60 430 90 Q 440 120 460 120 L 490 120" fill="none" stroke="{INK}" stroke-width="2"/>')
    f.text(440, 140, "一致で最小（吸収）", 12, RED, bold=True)
    f.text(140, 180, "使える", 17, GREEN, bold=True); f.text(390, 180, "使えない", 17, RED, bold=True)
    for i, t in enumerate(["共振周波数の測定", "送信周波数の測定", "寄生発射の有無"]):
        f.text(140, 215 + i * 34, t, 15, GREEN)
    for i, t in enumerate(["空中線電力の測定", "整合状態（→ SWR）"]):
        f.text(390, 215 + i * 34, t, 15, RED)
    f.box(30, 325, 460, 45, "穴埋め：疎 ・ 吸収 ・ 最小", fill=PALE, stroke=AMBER, size=17, bold=True)
    f.save("fig2_dip")


def fig2_swr_position():
    f = Fig()
    f.box(20, 80, 100, 60, "送信機", size=16)
    f.line(120, 110, 420, 110, INK, 6); antenna(f, 440, 110, 60); f.line(420, 110, 440, 110, INK, 3)
    f.box(350, 140, 80, 46, "SWR", fill=PALE_G, stroke=GREEN, size=16, color=GREEN, bold=True); f.line(390, 110, 390, 140, GREEN, 2)
    check(f, 455, 165, True)
    f.box(140, 140, 80, 46, "SWR", fill="#fff", stroke=MUTED, size=16, color=MUTED); f.line(180, 110, 180, 140, MUTED, 2)
    check(f, 235, 165, False)
    f.text(390, 215, "給電点の近く", 15, GREEN, bold=True)
    f.text(180, 215, "送信機の近く", 15, MUTED)
    f.box(30, 255, 460, 110, "", fill=PALE, stroke=AMBER)
    f.text(260, 285, "送信機側で測ると、給電線の損失で", 15, INK)
    f.text(260, 310, "反射が実際より小さく見える", 15, INK)
    f.text(260, 345, "SWR メータで測れるのは 定在波比 だけ", 15, RED, bold=True)
    f.save("fig2_swr_position")


def fig2_multiplier():
    f = Fig()
    f.text(130, 30, "分流器", 18, BLUE, bold=True); f.text(390, 30, "倍率器（直列抵抗器）", 17, RED, bold=True)
    f.line(260, 15, 260, 260, LINE, 2)
    f.line(30, 100, 70, 100); f.circle(130, 100, 30, label="A", size=20); f.line(160, 100, 230, 100)
    f.line(70, 100, 70, 160); f.line(190, 100, 190, 160); f.line(70, 160, 100, 160); f.resistor(100, 160, 60); f.line(160, 160, 190, 160)
    f.text(130, 200, "電流計に 並列", 15, BLUE, bold=True); f.text(130, 228, "倍率 ＝ 1 ＋ r ÷ R", 15, INK, bold=True)
    f.line(280, 100, 310, 100); f.resistor(310, 100, 60); f.line(370, 100, 390, 100); f.circle(420, 100, 30, label="V", size=20); f.line(450, 100, 490, 100)
    f.text(390, 200, "電圧計に 直列", 15, RED, bold=True); f.text(390, 228, "倍率 ＝ 1 ＋ R ÷ r", 15, INK, bold=True)
    f.box(20, 270, 480, 100, "", fill=PALE, stroke=AMBER)
    f.text(260, 298, "分流器 r/5 → 6倍　　倍率器 4r → 5倍", 16, INK, bold=True)
    f.text(260, 330, "50kΩ の電圧計を 20倍に", 15, INK)
    f.text(260, 356, "R ＝ 50k × (20 − 1) ＝ 950kΩ", 17, RED, bold=True)
    f.save("fig2_multiplier")


def fig2_power_meter():
    f = Fig()
    f.box(20, 60, 100, 60, "送信機", size=16)
    f.box(200, 60, 120, 60, "通過型\n電力計", fill=PALE, stroke=AMBER, size=14, bold=True)
    f.line(120, 90, 200, 90, INK, 4); f.line(320, 90, 420, 90, INK, 4); antenna(f, 440, 90, 50); f.line(420, 90, 440, 90, INK, 3)
    f.arrow(330, 70, 410, 70, GREEN, 3); f.text(370, 58, "進行 95W", 14, GREEN, bold=True)
    f.arrow(410, 112, 330, 112, RED, 3); f.text(370, 135, "反射 5W", 14, RED, bold=True)
    f.box(30, 170, 460, 70, "", fill=PALE_G, stroke=GREEN)
    f.text(260, 198, "アンテナへの供給電力 ＝ 進行 − 反射", 17, INK, bold=True)
    f.text(260, 228, "95 − 5 ＝ 90W", 20, GREEN, bold=True)
    f.box(30, 265, 460, 100, "", fill="#fff", stroke=INK)
    f.text(260, 293, "2V の蓄電池 3個直列 ＝ 6V", 15, INK)
    f.text(260, 321, "→ 最大目盛 10V の電圧計（5V は振り切れる）", 15, INK, bold=True)
    f.text(260, 349, "＋端子を電池の＋側、−端子を−側へ", 15, RED, bold=True)
    f.save("fig2_power_meter")


# ================= 法規 =================
def fig2_defs():
    f = Fig()
    rows(f, [("無線電話", "電波で「音声その他の音響」を\n送り、又は受けるための通信設備", RED),
             ("無線電信", "電波で「符号」を送り、又は受ける\nための通信設備", BLUE),
             ("無線設備", "無線電信・無線電話その他電波を送り、\n又は受けるための「電気的設備」", INK),
             ("混信", "他の無線局の正常な業務の運行を\n「妨害」する電波の発射、輻射又は誘導", AMBER)], y=26, h=76, gap=12, lw=120, size=16, dsize=13)
    f.save("fig2_defs")


def fig2_tx_equipment():
    f = Fig()
    f.box(30, 60, 180, 80, "送信装置", fill=PALE, stroke=RED, size=20, color=RED, bold=True)
    f.text(240, 108, "＋", 26, INK, bold=True)
    f.box(270, 60, 220, 80, "送信空中線系", fill=PALE_B, stroke=BLUE, size=20, color=BLUE, bold=True)
    f.parts.append(f'<path d="M30 160 L 30 175 L 490 175 L 490 160" fill="none" stroke="{INK}" stroke-width="2"/>')
    f.text(260, 205, "＝ 送信設備（電波を送る設備）", 18, INK, bold=True)
    f.box(30, 240, 460, 120, "", fill="#fff", stroke=BLUE)
    f.text(260, 272, "送信空中線系とは", 15, BLUE, bold=True)
    f.text(260, 302, "送信装置の発生する「高周波エネルギー」を", 15, INK)
    f.text(260, 330, "空間へふく射する装置", 15, INK)
    f.save("fig2_tx_equipment")


def fig2_procedures():
    f = Fig()
    rows(f, [("あらかじめ許可", "設備の変更の工事・設置場所の変更", RED),
             ("申請", "指定事項の変更\n（呼出符号・電波の型式・周波数・空中線電力）", BLUE),
             ("届出", "無線局の廃止", GREEN),
             ("訂正", "免許状の記載事項に変更を生じたとき", AMBER)], y=26, h=62, gap=12, lw=150, size=16, dsize=13)
    f.text(260, 330, "開設するとき ＝ 免許の申請書を提出", 15, INK, bold=True)
    f.text(260, 362, "いじる・動かす → 許可／もらい直す → 申請／やめる → 届出", 13, MUTED)
    f.save("fig2_procedures")


def fig2_designated():
    f = Fig()
    f.text(260, 34, "免許のときに指定される事項", 18, INK, bold=True)
    for i, t in enumerate(["電波の型式\n及び周波数", "呼出符号", "空中線電力", "運用許容時間"]):
        x = 20 + (i % 2) * 245; y = 55 + (i // 2) * 90
        f.box(x, y, 235, 75, t, fill=PALE, stroke=RED, size=18, color=RED, bold=True)
    f.text(260, 270, "指定事項でないもの", 15, MUTED, bold=True)
    f.text(260, 300, "✕ 無線設備の設置場所　✕ 空中線の型式及び構成", 14, MUTED)
    f.text(260, 328, "✕ 通信事項・通信の相手方　✕ 発振及び変調の方式", 14, MUTED)
    f.save("fig2_designated")


def fig2_license_items():
    f = Fig()
    f.parts.append(f'<rect x="30" y="20" width="250" height="350" rx="8" fill="#fff" stroke="{INK}" stroke-width="3"/>')
    f.text(155, 52, "無線局免許状", 18, INK, bold=True)
    for i, t in enumerate(["免許人の氏名・住所", "無線局の種別・目的", "通信の相手方・通信事項", "無線設備の設置場所", "免許の有効期間", "呼出符号", "電波の型式・周波数", "空中線電力・運用許容時間"]):
        f.text(50, 90 + i * 34, "・" + t, 14, INK, anchor="start")
    f.text(400, 60, "書かれない", 18, RED, bold=True)
    f.box(300, 90, 200, 60, "空中線の型式", fill=PALE_R, stroke=RED, size=17, color=RED, bold=True)
    f.box(300, 170, 200, 60, "無線従事者の資格", fill=PALE_R, stroke=RED, size=17, color=RED, bold=True)
    f.text(400, 260, "人の資格は", 13, MUTED); f.text(400, 280, "免許証のほう", 13, MUTED)
    f.save("fig2_license_items")


def fig2_antenna_removal():
    f = Fig()
    antenna(f, 100, 220, 120); f.line(30, 226, 170, 226, INK, 3)
    f.line(60, 90, 140, 170, RED, 5); f.line(140, 90, 60, 170, RED, 5)
    f.text(100, 260, "空中線を撤去", 16, RED, bold=True)
    f.box(200, 40, 300, 70, "免許が効力を失った\n→ 遅滞なく 空中線を撤去", fill=PALE_R, stroke=RED, size=16, color=RED, bold=True)
    f.box(200, 125, 300, 50, "免許状は 1か月以内に返納", fill=PALE, stroke=AMBER, size=16, bold=True)
    f.text(350, 210, "撤去しない場面", 15, MUTED, bold=True)
    for i, t in enumerate(["運用の休止", "運用の停止の命令", "臨時の電波発射停止"]):
        f.text(350, 240 + i * 26, "✕ " + t, 14, MUTED)
    f.text(100, 330, "（無線設備全部ではなく空中線だけ）", 13, MUTED)
    f.save("fig2_antenna_removal")


def fig2_wave_quality():
    f = Fig()
    f.box(30, 30, 460, 120, "", fill=PALE, stroke=AMBER)
    f.text(260, 62, "電波の質", 20, INK, bold=True)
    f.text(260, 98, "周波数の偏差及び幅", 20, RED, bold=True)
    f.text(260, 130, "高調波の強度　等", 20, RED, bold=True)
    f.text(260, 185, "電波の質ではないもの", 15, MUTED, bold=True)
    for i, t in enumerate(["変調度", "信号対雑音比", "空中線電力の偏差", "電波の型式"]):
        f.box(30 + i * 118, 205, 108, 44, t, fill="#fff", stroke=MUTED, size=12, color=MUTED)
    f.box(30, 285, 460, 80, "適合しないと → 臨時に電波の発射の停止\n→ 臨時検査", fill=PALE_R, stroke=RED, size=16, color=RED, bold=True)
    f.save("fig2_wave_quality")


def fig2_freq_stability():
    f = Fig()
    rows(f, [("発振回路の方式", "外囲の「温度若しくは湿度」の変化に\n影響を受けない", RED),
             ("送信装置", "「電源電圧又は負荷」の変化で\n「発振周波数」に影響を与えない", BLUE),
             ("移動する局", "実際上起こり得る「振動又は衝撃」\nによっても周波数を維持", GREEN)], y=30, h=84, gap=16, lw=150, size=16, dsize=14)
    f.box(30, 335, 460, 45, "回路 ＝ 温度湿度／装置 ＝ 電源と負荷／移動 ＝ 揺れ", fill=PALE, stroke=AMBER, size=14, bold=True)
    f.save("fig2_freq_stability")


def fig2_license_card():
    f = Fig()
    f.parts.append(f'<rect x="30" y="30" width="200" height="130" rx="10" fill="#fff" stroke="{INK}" stroke-width="3"/>')
    f.text(130, 60, "無線従事者免許証", 14, INK, bold=True)
    f.parts.append(f'<rect x="50" y="78" width="50" height="62" fill="#D9DEE3"/>')
    f.text(160, 100, "氏名", 14, RED, bold=True); f.text(160, 125, "資格", 13, MUTED)
    rows(f, [("訂正", "氏名が変わったとき", BLUE), ("再交付", "汚した・破った・失った\n→ 免許証と写真1枚", AMBER), ("返納 10日", "取消し・再交付後に発見・\n死亡／失そう", RED)], x=250, y=20, h=62, gap=12, lw=100, size=14, dsize=12)
    f.box(30, 250, 460, 50, "業務中は 携帯（掲示・保管ではない）", fill=PALE_B, stroke=BLUE, size=16, color=BLUE, bold=True)
    f.box(30, 315, 460, 55, "有効期間はない → 5年たっても何もしない", fill="#fff", stroke=MUTED, size=15, color=MUTED)
    f.save("fig2_license_card")


def fig2_supervision():
    f = Fig()
    flow(f, ["電波の質が\n不適合", "臨時に\n電波の発射の停止", "臨時検査"], y=30, x0=10, w=150, gap=20, h=70, hi=(1,), size=14)
    f.text(260, 130, "電波を発射させる検査 ＝ 電波の質又は空中線電力", 14, INK, bold=True)
    f.text(260, 170, "違反したとき（3か月以内の運用の停止）または制限", 15, INK, bold=True)
    for i, t in enumerate(["運用許容時間", "周波数", "空中線電力"]):
        f.box(30 + i * 158, 190, 145, 46, t, fill=PALE, stroke=RED, size=15, color=RED, bold=True)
    f.text(260, 270, "✕ 電波の型式・通信の相手方・通信事項の制限", 13, MUTED)
    f.box(30, 290, 225, 75, "不正な手段\n→ 免許の取消し", fill=PALE_R, stroke=RED, size=15, color=RED, bold=True)
    f.box(265, 290, 225, 75, "従事者の違反\n→ 3か月以内の従事停止", fill=PALE_B, stroke=BLUE, size=14, color=BLUE, bold=True)
    f.save("fig2_supervision")


def fig2_license_doc():
    f = Fig()
    f.parts.append(f'<rect x="30" y="30" width="150" height="190" rx="6" fill="#fff" stroke="{INK}" stroke-width="3"/>')
    f.text(105, 60, "免許状", 18, INK, bold=True)
    for k in range(5):
        f.line(50, 85 + k * 24, 160, 85 + k * 24, LINE, 2)
    rows(f, [("記載事項の変更", "免許状を提出して「訂正」", BLUE), ("汚した・破った", "理由を記載した申請書で「再交付」", AMBER), ("旧免許状", "遅滞なく返す（廃棄・保管 ✕）", RED)], x=200, y=30, h=56, gap=12, lw=120, size=13, dsize=12)
    f.box(30, 250, 460, 50, "移動する局の備え付け ＝ 無線設備の常置場所", fill=PALE_B, stroke=BLUE, size=15, color=BLUE, bold=True)
    f.box(30, 315, 460, 50, "効力を失ったら 1か月以内に返納", fill=PALE, stroke=AMBER, size=16, bold=True)
    f.save("fig2_license_doc")


def fig2_return_cases():
    f = Fig()
    f.text(130, 34, "1か月以内に返納", 18, RED, bold=True); f.text(390, 34, "返納しない", 18, MUTED, bold=True)
    f.line(260, 20, 260, 330, LINE, 2)
    for i, t in enumerate(["免許の取消し", "無線局の廃止", "有効期間の満了"]):
        f.box(30, 60 + i * 70, 200, 52, t, fill=PALE_R, stroke=RED, size=17, color=RED, bold=True)
    for i, t in enumerate(["臨時の電波発射停止", "運用の停止", "運用の休止", "住所の変更"]):
        f.box(290, 60 + i * 60, 200, 44, t, fill="#fff", stroke=MUTED, size=15, color=MUTED)
    f.text(130, 300, "＝ 免許が効力を失った", 14, RED, bold=True)
    f.text(390, 320, "（免許はまだ生きている）", 13, MUTED)
    f.save("fig2_return_cases")


def fig2_license_rule():
    f = Fig()
    f.parts.append(f'<rect x="30" y="30" width="180" height="220" rx="6" fill="#fff" stroke="{INK}" stroke-width="3"/>')
    f.text(120, 64, "免許状", 20, INK, bold=True)
    for i, t in enumerate(["呼出符号", "電波の型式", "周波数", "設置場所"]):
        f.text(120, 105 + i * 34, t, 15, BLUE, bold=True)
    f.text(330, 70, "運用はすべて", 15, INK); f.text(330, 98, "免許状のとおり", 19, BLUE, bold=True)
    f.box(240, 125, 260, 75, "空中線電力は\n範囲内で 必要最小", fill=PALE, stroke=AMBER, size=16, bold=True)
    f.text(370, 222, "（「適当なもの」は ✕）", 13, RED)
    f.box(30, 280, 460, 80, "範囲を超えて運用できる ＝ 非常通信\n（遭難・緊急・安全通信も）", fill=PALE_R, stroke=RED, size=16, color=RED, bold=True)
    f.save("fig2_license_rule")


def fig2_phrases():
    f = Fig()
    rows(f, [("了解 / OK", "通報を確実に受信した", GREEN), ("どうぞ", "応答してすぐ受信できる", BLUE), ("終わり", "通報の送信を終わる", INK),
             ("さようなら", "通信が終了した", RED), ("お待ちください", "10分以上待たせる（時間・理由も）", AMBER)], y=20, h=56, gap=11, lw=150, size=15, dsize=14)
    f.save("fig2_phrases")


def fig2_uncertain_call():
    f = Fig()
    f.box(20, 30, 230, 110, "", fill=PALE_B, stroke=BLUE)
    f.text(135, 60, "呼出符号が不確実", 16, BLUE, bold=True)
    f.text(135, 92, "「誰かこちらを", 16, INK); f.text(135, 118, "呼びましたか」で応答", 16, INK)
    f.box(270, 30, 230, 110, "", fill=PALE_R, stroke=RED)
    f.text(385, 60, "自局宛てか不確実", 16, RED, bold=True)
    f.text(385, 92, "確実に分かるまで", 16, INK); f.text(385, 118, "応答しない", 18, RED, bold=True)
    rows(f, [("混信の通知", "直ちに呼出しを中止", RED), ("周波数変更の要求", "「了解」又は「OK」→ 直ちに変更", BLUE), ("一括呼出し", "各局 3回・こちらは 1回・自局 3回以下", INK)], y=165, h=56, gap=10, lw=150, size=14, dsize=13)
    f.save("fig2_uncertain_call")


def fig2_correction():
    f = Fig()
    f.text(260, 34, "誤って送った", 16, MUTED)
    words = ["こちらは", "JA1ABC", "本日の", "天気は", "あめ"]
    for i, w in enumerate(words):
        f.box(20 + i * 98, 50, 90, 46, w, fill=PALE_R if i == 4 else "#fff", stroke=RED if i == 4 else INK, size=14, color=RED if i == 4 else INK)
    f.arrow(260, 110, 260, 140, INK, 2)
    f.box(20, 150, 110, 46, "訂正", fill=PALE, stroke=AMBER, size=17, color=RED, bold=True)
    for i, w in enumerate(["天気は", "晴れ"]):
        f.box(150 + i * 110, 150, 100, 46, w, fill=PALE_G, stroke=GREEN, size=15, color=GREEN, bold=True)
    f.text(260, 225, "正しく送った適当な語字から送り直す", 15, GREEN, bold=True)
    f.box(20, 250, 480, 50, "反復を求める ＝「反復」の 次に 箇所を示す", fill=PALE_B, stroke=BLUE, size=16, color=BLUE, bold=True)
    f.box(20, 315, 480, 50, "反復して送る ＝ 各通ごと又は1連続ごとに「反復」を前置", fill="#fff", stroke=INK, size=14)
    f.save("fig2_correction")


def fig2_simple_call():
    f = Fig()
    f.text(260, 30, "10W・確実に連絡できるとき", 16, INK, bold=True)
    f.box(20, 45, 230, 75, "呼出し\n相手局の呼出符号 3回以下", fill=PALE_B, stroke=BLUE, size=14, color=BLUE, bold=True)
    f.box(270, 45, 230, 75, "応答\nこちらは＋自局 1回", fill=PALE_G, stroke=GREEN, size=14, color=GREEN, bold=True)
    f.box(20, 140, 480, 70, "試験の前：ただいま試験中 3回・こちらは 1回・自局 3回\n試験中：他の無線局から停止の要求がないか聴守", fill=PALE, stroke=AMBER, size=14)
    f.box(20, 230, 480, 60, "「非常」の呼出しを受信\n→ 混信を与えるおそれのある電波を止めて傍受", fill=PALE_R, stroke=RED, size=14, color=RED, bold=True)
    f.box(20, 305, 480, 55, "有線が復旧 → 速やかに非常通信の取扱いを停止", fill="#fff", stroke=INK, size=15, bold=True)
    f.save("fig2_simple_call")


if __name__ == "__main__":
    n = 0
    for name, fn in list(globals().items()):
        if name.startswith("fig2_") and callable(fn):
            fn()
            n += 1
    print(f"{n} figures")
