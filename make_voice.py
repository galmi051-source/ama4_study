#!/usr/bin/env python3
"""
VOICEVOX で読み上げ音声をまとめて作るスクリプト（標準ライブラリだけで動きます）。

使い方（プロジェクトのフォルダで）:
  1. VOICEVOX を起動しておく（アプリを開くだけでOK。裏でエンジンが http://127.0.0.1:50021 に立ち上がる）
  2. python tools/make_voice.py
     → ボイスの一覧が出るので番号を入力（Enter だけなら前回と同じボイス）
       「t 番号」で試聴できる
  3. flutter run でビルドし直す

やること:
  - assets/questions/*.json を全部読み、tools/daihon.tsv（台本）を作り直す
  - 台本の各行を VOICEVOX で音声にして assets/voice/<キー>.m4a（ffmpeg が無ければ .wav）に保存
  - 前回から文章が変わっていない行はスキップするので、2回目以降は差分だけ作られる
  - 台本から消えた行の音声ファイルは削除する

オプション:
  --speakers        使える話者と ID の一覧を表示して終了
  --speaker 3       番号を直接指定（一覧を出さずにすぐ作り始める）
  --only-daihon     台本だけ作って音声は作らない（読み方の確認用）
  --force           全部作り直す

読み間違いを直したいとき:
  - 全問に効かせたい単語は tools/yomi.tsv に「表記<TAB>読み」で追加
  - その問題だけなら、問題 JSON に readQuestion / readExplanation を書く
  直したら再度このスクリプトを実行すれば、変わった行だけ作り直されます。
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# ===== 設定 =====
ENGINE = "http://127.0.0.1:50021"
SPEAKER = 3            # 初回の既定ボイス（3 = ずんだもん ノーマル）。2回目以降は前回選んだボイスが既定になる
SPEED = 0.9           # 話す速さ（1.0 が標準）
PITCH = 0.0
INTONATION = 1.0
PRE_SILENCE = 0.1      # 音声の前後の無音（秒）
POST_SILENCE = 0.2
SAMPLING_RATE = 24000
M4A_BITRATE = "64k"    # ffmpeg がある場合の圧縮率
SYNTH_TIMEOUT = 600    # 1件あたりの待ち時間の上限（秒）。遅いPCでも待てるよう長め
STOP_AFTER_FAILS = 3   # 連続でこの回数失敗したら、VOICEVOX が固まっているとみなして止める

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = ROOT / "assets" / "questions"
VOICE_DIR = ROOT / "assets" / "voice"
DAIHON = ROOT / "tools" / "daihon.tsv"
YOMI = ROOT / "tools" / "yomi.tsv"
CACHE = ROOT / "tools" / "voice_cache.json"
SETTING = ROOT / "tools" / "voice_setting.json"   # 前回選んだボイス
PREVIEW = ROOT / "tools" / "preview.wav"
PREVIEW_TEXT = "第1問。法規。4アマで操作できる無線設備は、145メガヘルツで空中線電力20ワット以下です。"
AUDIO_EXTS = (".m4a", ".wav", ".mp3")

# ===== 読み方の変換（アプリ側 tts_service.dart の normalize と同じ考え方＋α） =====
LETTERS = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                   "エー ビー シー ディー イー エフ ジー エイチ アイ ジェイ ケー エル エム "
                   "エヌ オー ピー キュー アール エス ティー ユー ブイ ダブリュー エックス ワイ ゼット".split()))
DIGITS_EN = "ゼロ ワン ツー スリー フォー ファイブ シックス セブン エイト ナイン".split()

# 英字略語（前後が英字でないときだけ置き換える。長いものから順に）
ABBR = {
    "CATV": "シーエーティーブイ", "SSB": "エスエスビー", "DSB": "ディーエスビー", "SWR": "エスダブリューアール",
    "LPF": "ローパスフィルタ", "HPF": "ハイパスフィルタ", "BPF": "バンドパスフィルタ",
    "BEF": "バンドエリミネーションフィルタ", "ALC": "エーエルシー", "IDC": "アイディーシー",
    "AGC": "エージーシー", "BFO": "ビーエフオー", "VOX": "ボックス", "RIT": "アールアイティー",
    "BCI": "ビーシーアイ", "TVI": "ティーブイアイ", "PLL": "ピーエルエル", "VCO": "ブイシーオー",
    "VHF": "ブイエイチエフ", "UHF": "ユーエイチエフ", "SHF": "エスエイチエフ", "HF": "エイチエフ",
    "FET": "エフイーティー", "NPN": "エヌピーエヌ", "PNP": "ピーエヌピー", "PTT": "ピーティーティー",
    "CBT": "シービーティー", "LED": "エルイーディー", "IC": "アイシー", "CW": "シーダブリュー",
    "FM": "エフエム", "AM": "エーエム",
}
# 漢字の読み（VOICEVOX が読み間違えやすいもの）
KANJI = {
    "聴守": "ちょうしゅ", "暗語": "あんご", "常置場所": "じょうちばしょ", "失そう": "しっそう",
    "空電": "くうでん", "定在波比": "ていざいはひ", "逓倍": "ていばい", "明りょう度": "めいりょうど",
    "自局": "じきょく", "他局": "たきょく", "相手局": "あいてきょく", "導波器": "どうはき",
    "給電点": "きゅうでんてん", "分流器": "ぶんりゅうき", "弁別器": "べんべつき", "緩衝": "かんしょう",
    "混変調": "こんへんちょう", "低調波": "ていちょうは", "側波帯": "そくはたい", "抑圧搬送波": "よくあつはんそうは",
    "擬似": "ぎじ", "呼出符号": "よびだしふごう", "呼出事項": "よびだしじこう", "免許人": "めんきょにん",
    "5D-2V": "ごディーにブイ", "3D-2V": "さんディーにブイ",
}
SYMBOLS = {
    "〔": "", "〕": "", "Ω": "オーム", "Ω": "オーム", "λ": "ラムダ", "×": "かける", "÷": "わる",
    "=": "イコール", "√": "ルート", "π": "パイ", "≒": "およそ", "→": "、", "~": "から", "〜": "から",
    "%": "パーセント", "−": "ひく", "+": "たす", "(": "、", ")": "、",
}
NUM = r"(?<![A-Za-z0-9.])(\d[\d.]*)\s*"
UNITS = [
    ("GHz", "ギガヘルツ"), ("MHz", "メガヘルツ"), ("kHz", "キロヘルツ"), ("Hz", "ヘルツ"),
    ("mA", "ミリアンペア"), ("kW", "キロワット"), ("mW", "ミリワット"), ("W(?![A-Za-z])", "ワット"),
    ("V(?![A-Za-z])", "ボルト"), ("A(?![A-Za-z0-9])", "アンペア"), ("dB", "デシベル"),
    ("km", "キロメートル"), ("m(?![A-Za-z])", "メートル"),
]
UNIT_RULES = [(re.compile(NUM + u), r) for u, r in UNITS]
BLANK = re.compile(r"[（(［\[][\s　]*[)）］\]]")


def load_user_yomi():
    d = {}
    if YOMI.exists():
        for line in YOMI.read_text(encoding="utf-8-sig").splitlines():
            if not line.strip() or line.startswith("#") or "\t" not in line:
                continue
            k, v = line.split("\t", 1)
            d[k.strip()] = v.strip()
    return d


def spell(s):
    return "".join(LETTERS.get(c.upper(), c) for c in s)


def make_reader(user_yomi):
    words = {**KANJI, **user_yomi}
    word_keys = sorted(words, key=len, reverse=True)
    abbr_re = re.compile(r"(?<![A-Za-z])(" + "|".join(sorted(ABBR, key=len, reverse=True)) + r")(?![A-Za-z])")

    def read(text):
        t = unicodedata.normalize("NFKC", text)
        t = BLANK.sub("かっこ", t)
        for k in word_keys:
            t = t.replace(unicodedata.normalize("NFKC", k), words[k])
        t = re.sub(r"(\d+),(\d{3})", r"\1\2", t)                       # 1,506.5 → 1506.5
        # 電波の型式（J3E, A1A など）
        t = re.sub(r"(?<![A-Za-z0-9])([A-Z])([0-9])([A-Z])(?![A-Za-z0-9])",
                   lambda m: LETTERS[m[1]] + DIGITS_EN[int(m[2])] + LETTERS[m[3]], t)
        t = abbr_re.sub(lambda m: ABBR[m[1]], t)
        t = re.sub(r"(?<![A-Za-z])([A-Z]{1,2})級", lambda m: spell(m[1]) + "きゅう", t)   # A級, AB級
        t = re.sub(r"(?<![A-Za-z])([A-Z])層", lambda m: LETTERS[m[1]] + "そう", t)        # E層
        t = re.sub(r"(?<![A-Za-z])([NP])形", lambda m: LETTERS[m[1]] + "がた", t)        # N形
        t = re.sub(r"(?<![A-Za-z])([A-Za-z])[:：]", lambda m: spell(m[1]) + "は、", t)     # A：〇〇
        t = re.sub(r"(\d+)/(\d+)", r"\2分の\1", t)
        for k, v in SYMBOLS.items():
            t = t.replace(k, v)
        for rule, rep in UNIT_RULES:
            t = rule.sub(lambda m, r=rep: m[1] + r, t)
        t = re.sub(r"(?<![A-Za-z])km(?![A-Za-z])", "キロメートル", t)                 # 数百km
        t = re.sub(r"(?<![A-Za-z])([A-Z]{1,4})(?![A-Za-z])", lambda m: spell(m[1]), t)  # 残った A, B, CQ など
        t = re.sub(r"[ \t]+", "、", t)
        t = re.sub(r"、+([。、？！])", r"\1", t)
        t = re.sub(r"、{2,}", "、", t)
        return t.strip().strip("、").strip()
    return read


def end(s):
    s = s.strip()
    return s if not s or re.search(r"[。？！?!]$", s) else s + "。"


def safe_key(s):
    return re.sub(r"[^A-Za-z0-9_-]", "_", s)


# ===== 台本づくり（アプリの tts_service.dart と同じキーを使う） =====
def build_daihon():
    read = make_reader(load_user_yomi())
    rows, ids = [], set()
    files = sorted(QUESTIONS_DIR.glob("*.json"))
    if not files:
        sys.exit(f"問題ファイルが見つかりません: {QUESTIONS_DIR}")
    count = 0
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        items = data if isinstance(data, list) else data.get("questions", [])
        for q in items:
            qid, choices, ans = str(q.get("id", "")), q.get("choices") or [], int(q.get("answer") or 0)
            if not qid or not (1 <= ans <= len(choices)) or qid in ids:
                continue  # アプリでも除外される問題
            ids.add(qid)
            count += 1
            k = safe_key(qid)
            body = end(read(q.get("readQuestion") or q["question"]))
            for i, c in enumerate(choices, 1):
                body += f"{i}番、{end(read(c))}"
            rows.append((f"{k}_q", body))
            rows.append((f"{k}_a", f"正解は、{ans}番。{end(read(choices[ans - 1]))}"))
            ex = (q.get("readExplanation") or q.get("explanation") or "").strip()
            if ex:
                rows.append((f"{k}_e", "解説。" + end(read(ex))))
    rows += [
        ("sys_houki", "法規。"), ("sys_kougaku", "無線工学。"),
        ("sys_correct", "正解です。"), ("sys_wrong", "不正解です。"),
        ("sys_sample", read("周波数は145MHz、空中線電力は20W、抵抗は50Ωです。")),
    ]
    for n in range(1, max(count, 50) + 1):
        rows.append((f"sys_dai_{n:03d}", f"第{n}問。"))
    with DAIHON.open("w", encoding="utf-8-sig", newline="\n") as fp:
        fp.write("key\t読み上げる文\n")
        for k, t in rows:
            fp.write(f"{k}\t{t}\n")
    print(f"台本を作りました: {DAIHON.relative_to(ROOT)}（問題 {count} 問 / {len(rows)} 行）")
    return rows


# ===== VOICEVOX =====
def api(method, path, params=None, body=None, timeout=120):
    url = ENGINE + path + ("?" + urllib.parse.urlencode(params) if params else "")
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"} if data else {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def check_engine():
    try:
        v = json.loads(api("GET", "/version", timeout=5))
        print(f"VOICEVOX エンジン {v} に接続しました")
    except Exception:
        sys.exit("VOICEVOX に接続できません。VOICEVOX を起動してからもう一度実行してください。\n"
                 f"（接続先: {ENGINE}）")


def fetch_styles():
    """[(番号, キャラクター名, スタイル名)]。歌唱用のスタイルは除く。"""
    styles = []
    for s in json.loads(api("GET", "/speakers")):
        for st in s["styles"]:
            if st.get("type", "talk") == "talk":
                styles.append((st["id"], s["name"], st["name"]))
    return styles


def list_speakers(styles=None):
    styles = styles or fetch_styles()
    chars = {}
    for sid, name, style in styles:
        chars.setdefault(name, []).append(f"{sid:>3} {style}")
    for name, items in chars.items():
        print(f"  {name}")
        print("     " + " / ".join(items))


def play_wav(path):
    try:
        if sys.platform.startswith("win"):
            import winsound
            winsound.PlaySound(str(path), winsound.SND_FILENAME)
            return
        players = [["afplay"]] if sys.platform == "darwin" else \
            [["aplay", "-q"], ["paplay"], ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"]]
        for cmd in players:
            if shutil.which(cmd[0]):
                subprocess.run(cmd + [str(path)], check=False)
                return
        print(f"  再生できるプレーヤーが見つかりません。{path} を開いて聞いてください。")
    except Exception as e:
        print(f"  再生できませんでした（{e}）。{path} を開いて聞いてください。")


def load_saved_speaker():
    try:
        return int(json.loads(SETTING.read_text(encoding="utf-8"))["speaker"])
    except Exception:
        return None


def choose_speaker():
    """一覧を出して番号を入力してもらう。Enter だけなら前回と同じ。"""
    styles = fetch_styles()
    names = {sid: f"{name}（{style}）" for sid, name, style in styles}
    default = load_saved_speaker()
    if default not in names:
        default = SPEAKER if SPEAKER in names else styles[0][0]
    if not sys.stdin.isatty():          # 自動実行などで入力できないときは前回のまま
        print(f"ボイス: {default} {names[default]}")
        return default

    print("\n使えるボイス（番号 スタイル）")
    list_speakers(styles)
    print(f"\n前回のボイス: {default} {names[default]}")
    while True:
        s = input("番号を入力（Enter=前回と同じ / t 番号=試聴 / q=やめる）: ").strip().lower()
        s = s.translate(str.maketrans("０１２３４５６７８９　ｔｑ", "0123456789 tq"))
        if s == "":
            return default
        if s == "q":
            sys.exit("中止しました")
        m = re.fullmatch(r"t\s*(\d+)?", s)
        if m:
            sid = int(m[1]) if m[1] else default
            if sid not in names:
                print(f"  {sid} は一覧にありません")
                continue
            print(f"  試聴: {sid} {names[sid]} …")
            try:
                PREVIEW.write_bytes(synth(PREVIEW_TEXT, sid))
                play_wav(PREVIEW)
            except urllib.error.URLError as e:
                print(f"  音声を作れませんでした（{e}）")
            continue
        if s.isdigit() and int(s) in names:
            sid = int(s)
            print(f"  → {sid} {names[sid]} に決定")
            return sid
        print("  一覧にある番号を入力してください（例: 3 / 試聴は t 3）")


def synth(text, speaker):
    q = json.loads(api("POST", "/audio_query", {"text": text, "speaker": speaker}))
    q.update(speedScale=SPEED, pitchScale=PITCH, intonationScale=INTONATION,
             prePhonemeLength=PRE_SILENCE, postPhonemeLength=POST_SILENCE,
             outputSamplingRate=SAMPLING_RATE, outputStereo=False)
    return api("POST", "/synthesis", {"speaker": speaker}, q, timeout=SYNTH_TIMEOUT)


HELP_STUCK = """
VOICEVOX から応答がありません。次を順に試してください。
  1. VOICEVOX を一度終了して起動し直す
  2. VOICEVOX の設定で、エンジンの動作モードを「CPU」にする（GPU モードで固まることがあります）
  3. VOICEVOX の画面で短い文を再生してみて、普通にしゃべるか確かめる
  4. このスクリプトをもう一度実行する（できた分はスキップされ、続きから作ります）"""


def warm_up(speaker):
    """最初にボイスを読み込んで、応答するか・どのくらいの速さかを確かめる。"""
    print("ボイスを準備しています（初回はモデルの読み込みで数十秒かかることがあります）…", flush=True)
    t = time.time()
    try:
        try:
            api("POST", "/initialize_speaker", {"speaker": speaker, "skip_reinit": "true"}, timeout=SYNTH_TIMEOUT)
        except urllib.error.HTTPError:
            pass  # 古いエンジンにはこの機能が無い
        t2 = time.time()
        synth("これはテストです。", speaker)
        test_sec = time.time() - t2
    except (urllib.error.URLError, OSError) as e:
        sys.exit(f"テスト音声を作れませんでした（{e}）\n{HELP_STUCK}")
    print(f"準備OK（読み込み {t2 - t:.0f}秒、短い文の合成 {test_sec:.1f}秒）")
    if test_sec > 5:
        print("  ※ 合成がかなり遅いです。VOICEVOX の動作モードや、他に重いソフトが動いていないか確認してください。")


def main():
    ap = argparse.ArgumentParser(description="VOICEVOX で4アマ問題の読み上げ音声を作る")
    ap.add_argument("--speakers", action="store_true")
    ap.add_argument("--speaker", type=int, default=None)
    ap.add_argument("--only-daihon", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    if a.speakers:
        check_engine()
        list_speakers()
        return

    rows = build_daihon()
    if a.only_daihon:
        return
    check_engine()
    speaker = a.speaker if a.speaker is not None else choose_speaker()
    previous = load_saved_speaker()
    SETTING.write_text(json.dumps({"speaker": speaker}), encoding="utf-8")

    ffmpeg = shutil.which("ffmpeg")
    ext = ".m4a" if ffmpeg else ".wav"
    if not ffmpeg:
        print("ffmpeg が見つからないので .wav で保存します（容量が大きめ。ffmpeg を入れると .m4a に圧縮されます）")
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    setting = f"{speaker}|{SPEED}|{PITCH}|{INTONATION}|{PRE_SILENCE}|{POST_SILENCE}|{SAMPLING_RATE}|{ext}"

    todo = []
    for key, text in rows:
        h = hashlib.sha1(f"{setting}|{text}".encode("utf-8")).hexdigest()
        if not a.force and cache.get(key) == h and (VOICE_DIR / f"{key}{ext}").exists():
            continue
        todo.append((key, text, h))
    print(f"作成する音声: {len(todo)} 件（変更なし {len(rows) - len(todo)} 件はスキップ）")
    if previous is not None and previous != speaker and len(todo) > 50 and sys.stdin.isatty():
        if input("ボイスが変わったので全体を作り直します。続けますか？ [Y/n]: ").strip().lower() in ("n", "no"):
            SETTING.write_text(json.dumps({"speaker": previous}), encoding="utf-8")
            sys.exit("中止しました（ボイスは前回のまま）")

    if todo:
        warm_up(speaker)
    start, failed, streak = time.time(), [], 0
    for i, (key, text, h) in enumerate(todo, 1):
        t_item = time.time()
        try:
            wav = synth(text, speaker)
            out = VOICE_DIR / f"{key}{ext}"
            if ffmpeg:
                tmp = VOICE_DIR / f"{key}.tmp.wav"
                tmp.write_bytes(wav)
                subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", str(tmp),
                                "-c:a", "aac", "-b:a", M4A_BITRATE, str(out)], check=True)
                tmp.unlink()
            else:
                out.write_bytes(wav)
            for other in AUDIO_EXTS:   # 形式を変えたときの古いファイルを消す
                if other != ext:
                    (VOICE_DIR / f"{key}{other}").unlink(missing_ok=True)
            cache[key] = h
            CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")  # 途中で止めても続きから作れる
            streak = 0
        except subprocess.CalledProcessError as e:
            failed.append(key)
            print(f"\n  失敗: {key}（ffmpeg での変換に失敗: {e}）")
        except (urllib.error.URLError, OSError) as e:
            failed.append(key)
            streak += 1
            print(f"\n  失敗: {key}（{e}、{time.time() - t_item:.0f}秒待ちました）")
            if streak >= STOP_AFTER_FAILS:
                print(f"\n連続で {streak} 件失敗したので中断します。")
                print(HELP_STUCK)
                sys.exit(1)
        if i % 10 == 0 or i == len(todo):
            el = time.time() - start
            print(f"\r  {i}/{len(todo)}  経過 {el:.0f}秒  残り約 {el / i * (len(todo) - i):.0f}秒   ", end="", flush=True)
    print()

    keys = {k for k, _ in rows}
    removed = 0
    for f in VOICE_DIR.iterdir():
        if f.suffix in AUDIO_EXTS and f.stem not in keys:
            f.unlink()
            cache.pop(f.stem, None)
            removed += 1
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")

    size = sum(f.stat().st_size for f in VOICE_DIR.iterdir() if f.suffix in AUDIO_EXTS)
    print(f"完了: {VOICE_DIR.relative_to(ROOT)}（合計 {size / 1024 / 1024:.1f}MB, 古いファイル {removed} 件削除）")
    if failed:
        print(f"失敗 {len(failed)} 件: もう一度実行すると失敗分だけ作り直します")
    print("次は flutter run（または再ビルド）でアプリに反映してください。")


if __name__ == "__main__":
    main()
