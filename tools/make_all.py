#!/usr/bin/env python3
"""
問題アプリの音声と講義動画を、まとめて自動で作る。

    python tools/make_all.py

最初に次の3つを聞いたら、あとは放置で最後まで進みます（一晩かかります）。
  1. 問題アプリの声
  2. 講義動画の声（今の分野ごとの設定のまま / 全部同じ声 / 分野ごとに選び直す）
  3. 終わったら GitHub に公開（push）するか

やること（この順番）:
  - 講義動画を全部作る（tools/make_lecture.py all。作成済みの音声は再利用）
  - 問題アプリの音声を作る（tools/make_voice.py。変更があった分だけ）
  - 選んだ場合は git commit と push（GitHub Actions がアプリを再公開）

途中で VOICEVOX が固まって失敗しても、少し待って自動でやり直します。
途中で止めても、もう一度実行すれば続きから作ります。
実行中はパソコンがスリープしないようにします（終わったら元に戻ります）。
記録は lectures/make_all.log に残ります。
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import make_voice as mv  # noqa: E402
import make_lecture as ml  # noqa: E402

LOG = ROOT / "lectures" / "make_all.log"
PY = sys.executable
LECTURE_CATEGORIES = ["基礎", "電子回路", "送信機", "受信機", "電波障害", "電源", "空中線", "電波伝搬", "測定",
                      "目的・定義", "無線局の免許", "無線設備", "無線従事者", "運用", "監督", "業務書類"]
RETRY = 4            # 失敗したときにやり直す回数
RETRY_WAIT = 90      # やり直す前に待つ秒数（VOICEVOX が回復するのを待つ）


def log(msg):
    line = f"[{time.strftime('%m/%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def keep_awake(on):
    """Windows のスリープを防ぐ（実行中だけ）"""
    if sys.platform != "win32":
        return
    import ctypes
    ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | (ES_SYSTEM_REQUIRED if on else 0))


def ask(prompt, default=""):
    s = input(prompt).strip()
    return s.translate(str.maketrans("０１２３４５６７８９　ｙｎｅ", "0123456789 yne")) or default


def names_map():
    styles = mv.fetch_styles()
    return {sid: f"{n}（{st}）" for sid, n, st in styles}


def run(args, label):
    """失敗したら待ってやり直す。成功なら True"""
    for attempt in range(1, RETRY + 2):
        log(f"{label} 開始" + (f"（{attempt}回目）" if attempt > 1 else ""))
        t = time.time()
        env = dict(os.environ, AMA4_AUTO="1", PYTHONIOENCODING="utf-8")
        r = subprocess.run([PY, *args], cwd=ROOT, stdin=subprocess.DEVNULL, env=env)
        if r.returncode == 0:
            log(f"{label} 完了（{(time.time() - t) / 60:.0f}分）")
            return True
        log(f"{label} が途中で失敗しました（終了コード {r.returncode}）")
        if attempt <= RETRY:
            log(f"  {RETRY_WAIT}秒待ってやり直します。作成済みの分は再利用されます")
            time.sleep(RETRY_WAIT)
            try:
                mv.api("GET", "/version", timeout=10)
            except Exception:
                log("  VOICEVOX が応答しません。VOICEVOX が起動しているか確認してください（このまま待ちます）")
    return False


def estimate_app_todo():
    """問題アプリで新しく作る必要がある音声の数（概算）"""
    rows = mv.build_daihon()
    have = {f.stem for f in mv.VOICE_DIR.iterdir() if f.suffix in mv.AUDIO_EXTS} if mv.VOICE_DIR.exists() else set()
    return len(rows), sum(1 for k, _ in rows if k not in have)


def main():
    print(__doc__)
    mv.check_engine()
    names = names_map()

    # ---- 1. 問題アプリの声 ----
    print("\n━━━━━━━━ 1. 問題アプリの声 ━━━━━━━━")
    prev_app = mv.load_saved_speaker()
    app_speaker = mv.choose_speaker()
    total, missing = estimate_app_todo()
    if prev_app is not None and prev_app != app_speaker:
        print(f"  ※ 声を変えたので、アプリの音声 {total} 件を全部作り直します（かなり時間がかかります）")
        app_todo = total
    else:
        app_todo = missing
    print(f"  → アプリ：{app_speaker} {names.get(app_speaker, '')}　作成 約{app_todo}件")

    # ---- 2. 講義動画の声 ----
    print("\n━━━━━━━━ 2. 講義動画の声 ━━━━━━━━")
    voices = ml.load_voices()
    for c in LECTURE_CATEGORIES:
        sid = voices.get(c, voices.get("default", mv.SPEAKER))
        print(f"  {c:<8} {sid:>3} {names.get(sid, '?')}")
    print("\n  Enter   ＝ 上の設定のまま（基本編と過去問攻略編は同じ分野なら同じ声）")
    print("  番号    ＝ 全部の動画をその声にする（t 番号 で試聴）")
    print("  e       ＝ 分野ごとに選び直す")
    lecture_speaker = None
    while True:
        s = ask("講義動画の声: ")
        if s == "":
            break
        if s == "e":
            for c in LECTURE_CATEGORIES:
                sid = ml.choose_speaker(c, voices.get(c, voices.get("default", mv.SPEAKER)), float(voices.get("speed", ml.SPEED)))
                ml.save_voice(c, sid)
            break
        if s.startswith("t"):
            rest = s[1:].strip()
            if rest.isdigit() and int(rest) in names:
                mv.PREVIEW.write_bytes(ml.voicevox_wav(ml.PREVIEW_TEXT, int(rest), float(voices.get("speed", ml.SPEED))))
                mv.play_wav(mv.PREVIEW)
            continue
        if s.isdigit() and int(s) in names:
            lecture_speaker = int(s)
            print(f"  → 全部の動画を {lecture_speaker} {names[lecture_speaker]} にします")
            break
        print("  Enter / 番号 / t 番号 / e のどれかを入力してください")

    # ---- 3. 公開するか ----
    print("\n━━━━━━━━ 3. 終わったら公開しますか ━━━━━━━━")
    print("  y ＝ 終わったら git commit と git push をして、アプリに新しい音声を反映する")
    print("  n ＝ 公開しない（あとで自分で push する）")
    publish = ask("公開しますか？ [y/N]: ", "n").lower().startswith("y")

    # ---- 確認 ----
    hours = (app_todo * 22 + 2 * 3600) / 3600
    print("\n━━━━━━━━ 確認 ━━━━━━━━")
    print(f"  アプリの声：{app_speaker} {names.get(app_speaker, '')}（約{app_todo}件）")
    print(f"  講義動画の声：{'全部 ' + str(lecture_speaker) + ' ' + names[lecture_speaker] if lecture_speaker is not None else '分野ごとの設定'}（全32本）")
    print(f"  公開：{'する' if publish else 'しない'}")
    print(f"  目安：{hours:.0f}時間ほど（VOICEVOX の速さによります）")
    if ask("\nこの内容で始めますか？ [Y/n]: ", "y").lower().startswith("n"):
        sys.exit("中止しました")

    # ======== ここから自動 ========
    keep_awake(True)
    ok_lecture = ok_app = False
    try:
        log("===== 自動作成を開始 =====")
        largs = ["tools/make_lecture.py", "all"]
        if lecture_speaker is not None:
            largs += ["--speaker", str(lecture_speaker)]
        else:
            largs += ["--each"]   # 入力なしで動かすので、分野ごとに voices.json の声が使われる
        ok_lecture = run(largs, "講義動画（全32本）")

        ok_app = run(["tools/make_voice.py", "--speaker", str(app_speaker)], "問題アプリの音声")

        if publish and ok_app:
            log("GitHub に公開します")
            subprocess.run(["git", "add", "assets/voice", "tools/voice_cache.json", "tools/voice_setting.json",
                            "tools/daihon.tsv", "tools/lecture/voices.json"], cwd=ROOT)
            msg = f"問題アプリの音声を更新（{time.strftime('%Y-%m-%d')}）"
            c = subprocess.run(["git", "commit", "-m", msg], cwd=ROOT)
            if c.returncode == 0:
                p = subprocess.run(["git", "push"], cwd=ROOT)
                log("push 完了。数分後にアプリに反映されます" if p.returncode == 0 else "push に失敗しました。あとで git push してください")
            else:
                log("コミットする変更がありませんでした")
    finally:
        keep_awake(False)

    log("===== 結果 =====")
    log(f"講義動画：{'完了' if ok_lecture else '一部失敗（もう一度実行すると続きから作ります）'} → {ml.OUT_DIR}")
    log(f"問題アプリ：{'完了' if ok_app else '一部失敗（もう一度実行すると続きから作ります）'}")
    if ok_app and not publish:
        log("アプリに反映するには： git add -A → git commit -m \"音声更新\" → git push")


if __name__ == "__main__":
    main()
