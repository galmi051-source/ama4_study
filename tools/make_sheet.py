"""暗記シート（A4・PDF）を作る。  python tools/make_sheet.py

tools/sheet/暗記シート.html を Edge で PDF にして lectures/暗記シート.pdf に出す。
内容を直したいときは HTML を編集して実行し直す。
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "sheet" / "暗記シート.html"
OUT = ROOT / "lectures" / "暗記シート.pdf"
EDGE = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]


def main():
    edge = next((c for c in EDGE if Path(c).exists()), None)
    if not edge:
        sys.exit("Edge が見つかりません")
    OUT.parent.mkdir(exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("CHROME_") and k.upper() != "__COMPAT_LAYER"}
    profile = Path(tempfile.gettempdir()) / "ama4_lecture_edge_profile"
    OUT.unlink(missing_ok=True)
    subprocess.run([edge, "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={profile}",
                    "--no-pdf-header-footer", f"--print-to-pdf={OUT}", SRC.as_uri()],
                   capture_output=True, timeout=120, env=env)
    if not OUT.exists():
        sys.exit("PDF を作れませんでした")
    print(f"-> {OUT.relative_to(ROOT)}（{OUT.stat().st_size / 1e6:.1f} MB）")


if __name__ == "__main__":
    main()
