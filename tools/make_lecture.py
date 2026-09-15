#!/usr/bin/env python3
"""
分野ごとの「講義動画」（スライド＋読み上げ）を作る。

    python tools/make_lecture.py 電源            # 1分野。ボイスの一覧が出るので番号を入力
    python tools/make_lecture.py all             # 全部まとめて。ボイスは 1 回選べば全分野に使われる
    python tools/make_lecture.py all --each      # 分野ごとに別のボイスを選ぶ（最初に全部聞かれ、あとは放置）
    python tools/make_lecture.py 電源 --speaker 8 --speed 0.8   # 一覧を出さずにすぐ作る
    python tools/make_lecture.py --speakers      # ボイスの番号一覧だけ表示
    python tools/make_lecture.py 電源 --engine sapi   # VOICEVOX 無しで Windows の音声で試作

ボイスと速さ:
  - 実行すると一覧が出る。番号を入力、Enter で voices.json の設定、「t 8」で試聴
  - 選んだ番号は tools/lecture/voices.json にその分野の値として保存される（次回の既定）
  - 話す速さは --speed（1.0 が標準。0.8 でゆっくり）。voices.json の "speed" が既定

必要なもの:
  - VOICEVOX を起動しておく（--engine sapi のときは不要）
  - ffmpeg（PATH に通っていること）
  - Microsoft Edge（スライドを画像にするのに使う）

入力:
  tools/lecture/<分野>.json   台本（スライドの見出し・箇条書き・図・ナレーション）
  tools/lecture/fig/*.svg     図
  tools/lecture/voices.json   分野ごとの話者番号 {"default": 3, "電源": 8, ...}
                              （番号は python tools/make_voice.py --speakers で一覧）
出力:
  lectures/<分野>.mp4         動画（1280x720）
  lectures/<分野>.m4a         音声だけ（ミュージック／ファイルアプリ用）
  lectures/<分野>.txt         台本の全文（読み返し用）

音声は tools/lecture/cache/ に文章＋話者ごとに残るので、台本の変わった所だけ作り直される。
読み方の変換（単位・略語・yomi.tsv）は make_voice.py と同じものを使う。

台本の書き方（JSON）:
  {"category": "電源", "speaker": 3,          speaker は省略可（voices.json を使う）
   "slides": [
     {"cover": true, "title": "電源", "subtitle": "…"},        表紙
     {"title": "見出し",
      "lines": ["箇条書き", "!赤字で強調する行", "途中の**強調**もできる"],
      "figure": "fig_xxx.svg",                                  省略可
      "say": ["ナレーション。", "配列なら連結される。"]}
   ]}
"""
import argparse
import hashlib
import html
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import make_voice as mv  # noqa: E402  読み方の変換と VOICEVOX 呼び出しを再利用

LECTURE_DIR = ROOT / "tools" / "lecture"
FIG_DIR = LECTURE_DIR / "fig"
CACHE_DIR = LECTURE_DIR / "cache"
OUT_DIR = ROOT / "lectures"
VOICES = LECTURE_DIR / "voices.json"

W, H = 1280, 720
SPEED = 0.9               # 話す速さの既定（1.0 が VOICEVOX 標準）。voices.json の "speed" か --speed で変更
PREVIEW_TEXT = "無線工学、電源の講義です。1.5ボルトの乾電池を4本直列にすると6ボルトになります。"
PAUSE_AFTER_SLIDE = 0.8   # スライドの最後に入れる無音（秒）
FPS = 10

EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
]

SLIDE_CSS = """
* { box-sizing: border-box; }
html, body { margin: 0; width: 1280px; height: 720px; overflow: hidden;
  background: #F2F4F6; font-family: "Yu Gothic UI", "Meiryo", "Noto Sans JP", sans-serif; color: #1A1F24; }
.top { background: #1E2B38; color: #fff; height: 84px; padding: 0 40px; display: flex; align-items: center; gap: 18px; }
.top .cat { background: #F5B041; color: #142029; font-weight: 700; padding: 4px 12px; border-radius: 6px; font-size: 22px; }
.top .title { font-size: 34px; font-weight: 700; }
.body { display: flex; height: 592px; padding: 28px 40px; gap: 32px; }
.text { flex: 1 1 0; font-size: 30px; line-height: 1.55; }
.text.wide { flex: 1 1 100%; }
.text ul { margin: 0; padding-left: 1.1em; }
.text li { margin-bottom: 14px; }
.text li.k { color: #C8463D; font-weight: 700; }
.text b { color: #C8463D; }
.fig { flex: 0 0 560px; display: flex; align-items: center; justify-content: center; background: #fff;
  border-radius: 14px; border: 1px solid #D9DEE3; padding: 16px; }
.fig svg { max-width: 100%; max-height: 100%; }
.foot { position: absolute; left: 0; right: 0; bottom: 0; height: 44px; padding: 0 40px; display: flex; align-items: center;
  justify-content: space-between; color: #66727F; font-size: 18px; }
.cover { height: 636px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 24px; text-align: center; }
.cover h1 { font-size: 64px; margin: 0; }
.cover p { font-size: 30px; color: #66727F; margin: 0; }
"""


def find_edge():
    for c in EDGE_CANDIDATES:
        if Path(c).exists():
            return c
    sys.exit("Edge（または Chrome）が見つかりません。スライドを画像にするのに必要です。")


def need(cmd):
    if shutil.which(cmd) is None:
        sys.exit(f"{cmd} が見つかりません。インストールして PATH を通してください。")


# ---------- 台本 ----------
def load_script(name):
    p = LECTURE_DIR / f"{name}.json"
    if not p.exists():
        sys.exit(f"台本がありません: {p}")
    s = json.loads(p.read_text(encoding="utf-8"))
    s.setdefault("category", name)
    s.setdefault("subject", "無線工学")
    s.setdefault("title", s["category"])
    return s


def narration(slide):
    say = slide.get("say", "")
    if isinstance(say, list):
        say = "".join(say)
    return say.strip()


# ---------- スライド → PNG ----------
def emphasize(text):
    """**強調** を赤太字にする"""
    parts = html.escape(text).split("**")
    return "".join(f"<b>{p}</b>" if j % 2 else p for j, p in enumerate(parts))


def slide_html(script, i, slide, total):
    cat = html.escape(script["category"])
    if slide.get("cover"):
        body = (f'<div class="cover"><h1>{html.escape(slide.get("title", script["title"]))}</h1>'
                f'<p>{html.escape(slide.get("subtitle", script["subject"] + "｜" + script["category"]))}</p></div>')
    else:
        items = []
        for line in slide.get("lines", []):
            key = line.startswith("!")
            txt = emphasize(line[1:] if key else line)
            cls = ' class="k"' if key else ""
            items.append(f"<li{cls}>{txt}</li>")
        fig = ""
        if slide.get("figure"):
            fp = FIG_DIR / slide["figure"]
            if not fp.exists():
                sys.exit(f"図がありません: {fp}")
            fig = f'<div class="fig">{fp.read_text(encoding="utf-8")}</div>'
        wide = "" if fig else " wide"
        body = (f'<div class="top"><span class="cat">{cat}</span>'
                f'<span class="title">{html.escape(slide.get("title", ""))}</span></div>'
                f'<div class="body"><div class="text{wide}"><ul>{"".join(items)}</ul></div>{fig}</div>')
    foot = (f'<div class="foot"><span>{html.escape(script["subject"])}｜{cat}</span>'
            f'<span>{i + 1} / {total}</span></div>')
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{SLIDE_CSS}</style></head>"
            f"<body>{body}{foot}</body></html>")


def render_png(edge, html_path, png_path):
    subprocess.run([edge, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                    f"--window-size={W},{H}", f"--screenshot={png_path}", html_path.as_uri()],
                   check=True, capture_output=True, timeout=120)


# ---------- 音声 ----------
def sapi_wav(text, out, speed=1.0):
    """Windows 標準の音声合成（試作用）。speed 1.0 → Rate 0、0.8 → Rate -2"""
    rate = max(-10, min(10, round((speed - 1.0) * 10)))
    txt = Path(f"{out}.txt")
    txt.write_text(text, encoding="utf-8")
    ps = ("Add-Type -AssemblyName System.Speech;"
          "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
          f"$s.SelectVoice('Microsoft Haruka Desktop'); $s.Rate = {rate};"
          f"$s.SetOutputToWaveFile('{out}');"
          f"$s.Speak([IO.File]::ReadAllText('{txt}', [Text.Encoding]::UTF8)); $s.Dispose()")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True, capture_output=True)
    txt.unlink()


def voicevox_wav(text, speaker, speed):
    q = json.loads(mv.api("POST", "/audio_query", {"text": text, "speaker": speaker}))
    q.update(speedScale=speed, pitchScale=mv.PITCH, intonationScale=mv.INTONATION,
             prePhonemeLength=0.15, postPhonemeLength=0.3,
             outputSamplingRate=mv.SAMPLING_RATE, outputStereo=False)
    return mv.api("POST", "/synthesis", {"speaker": speaker}, q, timeout=mv.SYNTH_TIMEOUT)


def make_audio(text, speaker, speed, engine, read):
    """読み上げ音声を作って wav のパスを返す（キャッシュあり）"""
    CACHE_DIR.mkdir(exist_ok=True)
    spoken = read(text)
    key = hashlib.md5(f"{engine}|{speaker}|{speed}|{spoken}".encode("utf-8")).hexdigest()
    wav = CACHE_DIR / f"{key}.wav"
    if wav.exists():
        return wav
    if engine == "sapi":
        sapi_wav(spoken, wav, speed)
    else:
        wav.write_bytes(voicevox_wav(spoken, speaker, speed))
    return wav


# ---------- ボイス選択 ----------
def load_voices():
    return json.loads(VOICES.read_text(encoding="utf-8")) if VOICES.exists() else {}


def save_voice(name, speaker):
    v = load_voices()
    v[name] = speaker
    VOICES.write_text(json.dumps(v, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def choose_speaker(name, default, speed):
    """ボイスの一覧を出して番号を入力してもらう。Enter なら default。t 番号 で試聴。"""
    styles = mv.fetch_styles()
    names = {sid: f"{n}（{st}）" for sid, n, st in styles}
    if default not in names:
        default = styles[0][0]
    if not sys.stdin.isatty():
        print(f"ボイス: {default} {names[default]}")
        return default
    print(f"\n「{name}」のボイスを選んでください（番号 スタイル）")
    mv.list_speakers(styles)
    print(f"\n今の設定: {default} {names[default]}　速さ {speed}")
    while True:
        s = input("番号を入力（Enter=今の設定 / t 番号=試聴 / q=やめる）: ").strip().lower()
        s = s.translate(str.maketrans("０１２３４５６７８９　ｔｑ", "0123456789 tq"))
        if s == "":
            return default
        if s == "q":
            sys.exit("中止しました")
        if s.startswith("t"):
            rest = s[1:].strip()
            sid = int(rest) if rest.isdigit() else default
            if sid not in names:
                print(f"  {sid} は一覧にありません")
                continue
            print(f"  試聴: {sid} {names[sid]} …")
            try:
                mv.PREVIEW.write_bytes(voicevox_wav(PREVIEW_TEXT, sid, speed))
                mv.play_wav(mv.PREVIEW)
            except Exception as e:
                print(f"  音声を作れませんでした（{e}）")
            continue
        if s.isdigit() and int(s) in names:
            print(f"  → {int(s)} {names[int(s)]} に決定")
            return int(s)
        print("  一覧にある番号を入力してください（例: 3 / 試聴は t 3）")


# ---------- 動画 ----------
def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *map(str, args)], check=True)


def build(script, engine, speaker, speed, edge, audio_only):
    read = mv.make_reader(mv.load_user_yomi())
    slides = script["slides"]
    total = len(slides)
    OUT_DIR.mkdir(exist_ok=True)
    name = script["category"]
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        segs = []
        texts = []
        for i, sl in enumerate(slides):
            say = narration(sl)
            texts.append(f"--- {i + 1}. {sl.get('title', '')}\n{say}\n")
            print(f"  [{i + 1}/{total}] {sl.get('title', '')[:30]} … 音声", end="", flush=True)
            wav = make_audio(say, speaker, speed, engine, read) if say else None
            if audio_only:
                seg = tdp / f"seg{i:03d}.m4a"
                if wav is None:
                    ff("-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", 2, "-c:a", "aac", "-b:a", "96k", seg)
                else:
                    ff("-i", wav, "-af", f"apad=pad_dur={PAUSE_AFTER_SLIDE}", "-c:a", "aac", "-b:a", "96k", seg)
            else:
                print("、スライド", end="", flush=True)
                seg = tdp / f"seg{i:03d}.mp4"
                hp = tdp / f"slide{i:03d}.html"
                hp.write_text(slide_html(script, i, sl, total), encoding="utf-8")
                png = tdp / f"slide{i:03d}.png"
                render_png(edge, hp, png)
                video = ["-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-pix_fmt", "yuv420p",
                         "-r", FPS, "-c:a", "aac", "-b:a", "96k", "-shortest", seg]
                if wav is None:
                    ff("-loop", 1, "-framerate", FPS, "-i", png, "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                       "-t", 2, *video)
                else:
                    ff("-loop", 1, "-framerate", FPS, "-i", png, "-i", wav, "-af", f"apad=pad_dur={PAUSE_AFTER_SLIDE}",
                       *video)
            segs.append(seg)
            print(" OK")
        lst = tdp / "list.txt"
        lst.write_text("".join(f"file '{s.as_posix()}'\n" for s in segs), encoding="utf-8")
        out = OUT_DIR / (f"{name}.m4a" if audio_only else f"{name}.mp4")
        ff("-f", "concat", "-safe", 0, "-i", lst, "-c", "copy", "-movflags", "+faststart", out)
        if not audio_only:
            ff("-i", out, "-vn", "-c:a", "copy", "-movflags", "+faststart", OUT_DIR / f"{name}.m4a")
        (OUT_DIR / f"{name}.txt").write_text(f"{script['subject']}｜{script['title']}\n\n" + "\n".join(texts),
                                             encoding="utf-8")
        print(f"-> {out.relative_to(ROOT)}（{out.stat().st_size / 1e6:.1f} MB）")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", help="分野名（tools/lecture/<名前>.json）または all")
    ap.add_argument("--engine", choices=["voicevox", "sapi"], default="voicevox")
    ap.add_argument("--speaker", type=int, help="話者番号（一覧を出さずにこの番号で作る）")
    ap.add_argument("--speakers", action="store_true", help="ボイスの番号一覧を表示して終了")
    ap.add_argument("--speed", type=float, help=f"話す速さ（1.0 が標準。既定 {SPEED}）")
    ap.add_argument("--each", action="store_true", help="複数の分野を作るとき、分野ごとにボイスを選ぶ")
    ap.add_argument("--audio-only", action="store_true", help="m4a だけ作る（動画を作らない）")
    a = ap.parse_args()

    if a.engine == "voicevox":
        mv.check_engine()
    if a.speakers:
        mv.list_speakers()
        return
    if not a.names:
        ap.error("分野名を指定してください（例: 電源 / all）")

    need("ffmpeg")
    edge = None if a.audio_only else find_edge()
    voices = load_voices()

    names = a.names
    if names == ["all"]:
        names = sorted(p.stem for p in LECTURE_DIR.glob("*.json") if p.name != "voices.json")
    # 複数の分野をまとめて作るときは、ボイスを 1 回だけ選んで全部に使う（--each なら分野ごとに選ぶ）
    common = a.speaker
    if common is None and a.engine == "voicevox" and len(names) > 1 and not a.each:
        speed0 = a.speed if a.speed is not None else float(voices.get("speed", SPEED))
        common = choose_speaker("、".join(names), voices.get("default", mv.SPEAKER), speed0)
        save_voice("default", common)
    # 先に全分野のボイスを決めてから（--each のときは分野ごとに聞く）、あとは放置で全部作る
    plan = []
    for n in names:
        script = load_script(n)
        speed = a.speed if a.speed is not None else float(script.get("speed", voices.get("speed", SPEED)))
        default = script.get("speaker", voices.get(n, voices.get("default", mv.SPEAKER)))
        if common is not None:
            speaker = common
        elif a.engine == "voicevox":
            speaker = choose_speaker(n, default, speed)
        else:
            speaker = default
        if a.engine == "voicevox" and speaker != voices.get(n):
            save_voice(n, speaker)
        plan.append((script, speaker, speed))
    if len(plan) > 1:
        print("\n作る動画:")
        for script, speaker, speed in plan:
            print(f"  {script['category']}　話者 {speaker}　速さ {speed}")
        print("ここからは自動で進みます（終わるまで放置で OK）\n")
    for script, speaker, speed in plan:
        print(f"== {script['subject']}｜{script['title']}（話者 {speaker}, 速さ {speed}, {a.engine}）")
        build(script, a.engine, speaker, speed, edge, a.audio_only)
    print(f"\n全部できました → {OUT_DIR}")


if __name__ == "__main__":
    main()
