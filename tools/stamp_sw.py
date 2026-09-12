"""ビルド後に build/web/sw.js へ版数と問題ファイル一覧を埋め込む。

    python tools/stamp_sw.py <version>

version は GitHub Actions ではコミット SHA、ローカルでは日時。
"""
import json
import os
import sys

root = os.path.join(os.path.dirname(__file__), '..')
version = sys.argv[1] if len(sys.argv) > 1 else 'dev'
files = sorted(f for f in os.listdir(os.path.join(root, 'assets', 'questions')) if f.endswith('.json'))
path = os.path.join(root, 'build', 'web', 'sw.js')
with open(path, encoding='utf-8') as f:
    s = f.read()
s = s.replace('__BUILD_VERSION__', version).replace('__QUESTION_FILES__', json.dumps(files, ensure_ascii=False))
with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(s)
print(f'sw.js: version={version} questions={files}')
