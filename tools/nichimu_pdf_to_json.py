#!/usr/bin/env python3
"""
日本無線協会が公開している CBT 例題 PDF（4アマ）を、このアプリの問題 JSON に変換する補助スクリプト。
自分の学習用に、自分でダウンロードした PDF を変換するためのもの。

入手先:
  https://www.nichimu.or.jp/kshiken/siken/vcmsFolder_856/vcms_856.html
  （第四級アマチュア無線技士 → 法規 No.1〜3 / 工学 No.1〜3）

使い方:
  pip install pdfplumber
  python nichimu_pdf_to_json.py 4ama_E_01.pdf --subject 法規 --tag E01
  python nichimu_pdf_to_json.py 4ama_A_01.pdf --subject 無線工学 --tag A01
  → 同じ場所に nichimu_E01.json などができるので assets/questions/ にコピーしてビルド

仕組みと限界:
  - 2段組みのページを左右に分けて読み、〔番号〕で問題を、「１．」〜「４．」で選択肢を切り出します。
  - 正解は PDF 上の「網掛け」で示されているため、選択肢番号の位置に重なる塗りつぶし矩形から推定します。
    推定できなかった問題は answer=0 で出力され、アプリ側では読み込み時に除外されます（ホームに警告表示）。
    PDF を見ながら answer を 1〜4 に書き換えてください。
  - 図のある問題は needsImage=true になります。図のスクリーンショットを assets/images/ に置き、
    "image": "assets/images/xxx.png" を設定してください（pubspec.yaml の assets/images/ 行も有効に）。
  - 図中の文字が問題文に混ざることがあります。出力は必ず目で確認してください。
  - 解説は空なので、必要なら自分で書き足してください（空でも「正解」の読み上げはされます）。
"""
import argparse
import json
import re
import sys
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    sys.exit("pdfplumber が必要です:  pip install pdfplumber")

Q_MARK = re.compile(r"^\s*〔\s*(\d+)\s*〕\s*")
CHOICE_MARK = re.compile(r"^\s*([1-4１-４])\s*[．.]\s*")
SKIP_LINE = re.compile(r"(試験問題例題|^\s*\d+\s*/\s*\d+\s*$)")
Z2H = str.maketrans("１２３４", "1234")


def is_shading(rect):
    """白以外で塗られた小さめの矩形を網掛けとみなす。"""
    if not rect.get("fill"):
        return False
    w = rect["x1"] - rect["x0"]
    h = rect["bottom"] - rect["top"]
    if w > 60 or h > 30 or w < 3 or h < 3:
        return False
    color = rect.get("non_stroking_color")
    if color is None:
        return False
    vals = color if isinstance(color, (list, tuple)) else [color]
    try:
        vals = [float(v) for v in vals]
    except (TypeError, ValueError):
        return False
    if len(vals) == 4:  # CMYK
        return any(v > 0.03 for v in vals)
    return any(v < 0.97 for v in vals)  # Gray / RGB


def overlaps(a, b, pad=1.5):
    return not (
        a["x1"] < b["x0"] - pad
        or a["x0"] > b["x1"] + pad
        or a["bottom"] < b["top"] - pad
        or a["top"] > b["bottom"] + pad
    )


def lines_of(area):
    """領域内の単語を行ごとにまとめる。各行は (テキスト, 先頭単語のbbox)。"""
    words = area.extract_words(keep_blank_chars=True, x_tolerance=1.5, y_tolerance=3)
    rows = {}
    for w in words:
        rows.setdefault(round(w["top"] / 3), []).append(w)
    out = []
    for key in sorted(rows):
        ws = sorted(rows[key], key=lambda w: w["x0"])
        out.append(("".join(w["text"] for w in ws), ws[0]))
    return out


def parse(pdf_path):
    questions = []
    cur = None
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            shades = [r for r in page.rects if is_shading(r)]
            mid = page.width / 2
            for area in (page.crop((0, 0, mid, page.height)),
                         page.crop((mid, 0, page.width, page.height))):
                for text, first in lines_of(area):
                    if SKIP_LINE.search(text):
                        continue
                    m = Q_MARK.match(text)
                    if m:
                        cur = {"no": int(m.group(1)), "q": text[m.end():],
                               "choices": [], "answer": 0}
                        questions.append(cur)
                        continue
                    if cur is None:
                        continue
                    c = CHOICE_MARK.match(text)
                    if c:
                        n = int(c.group(1).translate(Z2H))
                        cur["choices"].append(text[c.end():])
                        marker = {"x0": first["x0"], "x1": first["x0"] + 14,
                                  "top": first["top"], "bottom": first["bottom"]}
                        if any(overlaps(marker, r) for r in shades):
                            cur["answer"] = n
                    elif cur["choices"]:
                        cur["choices"][-1] += text
                    else:
                        cur["q"] += text
    questions.sort(key=lambda x: x["no"])
    return questions


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--subject", required=True, choices=["法規", "無線工学"])
    ap.add_argument("--tag", required=True, help="IDの接頭辞（例 E01, A02）")
    ap.add_argument("-o", "--out", help="出力先（省略時は nichimu_<tag>.json）")
    args = ap.parse_args()

    raw = parse(args.pdf)
    items, missing = [], []
    for r in raw:
        qid = f"N{args.tag}-{r['no']:02d}"
        item = {
            "id": qid,
            "subject": args.subject,
            "category": "公式例題",
            "question": r["q"].strip(),
            "choices": [c.strip() for c in r["choices"]],
            "answer": r["answer"],
            "explanation": "",
            "image": None,
            "source": f"日本無線協会 CBT例題 {Path(args.pdf).name}",
        }
        if "図" in item["question"]:
            item["needsImage"] = True
        if r["answer"] == 0 or len(item["choices"]) != 4:
            missing.append(qid)
        items.append(item)

    out = Path(args.out or f"nichimu_{args.tag}.json")
    out.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(items)}問を書き出しました → {out}", file=sys.stderr)
    if missing:
        print("正解か選択肢を手で確認してください: " + ", ".join(missing), file=sys.stderr)
    figs = [i["id"] for i in items if i.get("needsImage")]
    if figs:
        print("図の画像が必要な問題: " + ", ".join(figs), file=sys.stderr)


if __name__ == "__main__":
    main()
