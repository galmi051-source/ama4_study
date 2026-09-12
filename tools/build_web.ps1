# ローカルで公開用と同じビルドをして build/web に出す（動作確認用）
#   powershell -ExecutionPolicy Bypass -File tools/build_web.ps1
#   その後:  python -m http.server 8080 -d build/web   → http://localhost:8080/
param([string]$BaseHref = "/")
Set-Location (Join-Path $PSScriptRoot "..")
flutter build web --release --no-wasm-dry-run --base-href $BaseHref
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python tools/stamp_sw.py (Get-Date -Format "yyyyMMddHHmmss")
