# 同梱フォント（assets/fonts/NotoSansJP-*.otf）の作り方

Web 版はブラウザの日本語フォントを使えない（Flutter は Google Fonts から字形を都度ダウンロードする）ので、
オフラインでも文字が出るように Noto Sans JP を日本語の範囲だけ切り出して同梱している。
通常は作り直す必要はない。

```bash
pip install fonttools
curl -L -o NotoSansJP-Regular.otf https://github.com/notofonts/noto-cjk/raw/main/Sans/SubsetOTF/JP/NotoSansJP-Regular.otf
curl -L -o NotoSansJP-Bold.otf    https://github.com/notofonts/noto-cjk/raw/main/Sans/SubsetOTF/JP/NotoSansJP-Bold.otf
R="U+0020-007E,U+00A0-00FF,U+2000-206F,U+2100-214F,U+2190-21FF,U+2200-22FF,U+2460-24FF,U+25A0-25FF,U+2600-26FF,U+3000-30FF,U+3200-33FF,U+4E00-9FFF,U+FF00-FFEF"
python -m fontTools.subset NotoSansJP-Regular.otf --unicodes="$R" --output-file=assets/fonts/NotoSansJP-Regular.otf
python -m fontTools.subset NotoSansJP-Bold.otf    --unicodes="$R" --output-file=assets/fonts/NotoSansJP-Bold.otf
```

ライセンス：SIL Open Font License 1.1（© Google / Adobe）。
