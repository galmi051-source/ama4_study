# 4アマ ながら学習（個人用）

第四級アマチュア無線技士の試験対策アプリ。問題・正解・解説を VOICEVOX の音声で読み上げます（音声ファイルが無い文は端末の音声合成で代わりに読みます）。

## 機能
- **今日の復習**：間違えた問題と、復習期限が来た問題＋新しい問題10問。正解するほど次の出題が先に延びる（1→3→7→14→30日）
- **ながら聞き**：問題 → 選択肢 → 考える時間 → 正解 → 解説 を自動で連続再生。画面は点けたまま
- **分野を選んで解く／苦手な問題**
- **模擬試験**：法規12問＋無線工学12問／60分。各科目8問（40点）以上で合格判定
- **合格見込みメーター**：12問中何問取れそうかをSメーター風に表示
- 各問題で「問題／答え／解説」を個別に読み上げ。速さと考える時間は設定から変更

## Web 版（iPhone はこちら）
Windows しか無くても iPhone で使えるように、Web アプリ（PWA）としても動きます。
- 公開手順は **[DEPLOY.md](DEPLOY.md)**（GitHub Pages・`git push` で自動公開）
- 手元で動かす：`flutter run -d chrome`（または `-d edge`）
- 公開用と同じビルドを試す：`powershell -ExecutionPolicy Bypass -File tools/build_web.ps1` → `python -m http.server 8080 -d build/web` → http://localhost:8080/?sw=1
- 仕組みのメモ：
  - 音声再生は `web/index.html` の `window.ama4Audio`（`<audio>` 1 個を使い回し、最初のタップで有効化）。iOS Safari の自動再生制限対策
  - オフライン対応は `web/sw.js`。アプリ本体と問題は初回に、音声は再生したものから順にキャッシュ。設定から全音声の一括ダウンロードも可
  - アイコンは `python tools/make_icons.py` で生成

## セットアップ
```bash
flutter create --org com.example --platforms android,ios ama4_study
# このフォルダの lib/ assets/ tools/ pubspec.yaml analysis_options.yaml を上書きコピー
cd ama4_study
flutter pub get
flutter run
```

### Android（必須）
`android/app/src/main/AndroidManifest.xml` の `<manifest>` 直下に追加（Android 11以降で音声合成を使うため）：
```xml
<queries>
  <intent>
    <action android:name="android.intent.action.TTS_SERVICE" />
  </intent>
</queries>
```
端末の「設定 → テキスト読み上げ」で日本語の音声データが入っているか確認してください。

### iOS（任意：画面を消しても読み上げを続けたい場合）
`ios/Runner/Info.plist` に追加：
```xml
<key>UIBackgroundModes</key>
<array>
  <string>audio</string>
</array>
```

## VOICEVOX で読み上げ音声を作る
1. VOICEVOX（https://voicevox.hiroshiba.jp/）をインストールして起動しておく
2. プロジェクトのフォルダで
   ```bash
   python tools/make_voice.py
   ```
3. `flutter run` でビルドし直す

- `tools/daihon.tsv` に台本（読み上げる文の一覧）が作られ、`assets/voice/` に音声ができます
- ffmpeg が入っていれば .m4a（小さい）、無ければ .wav で保存します
- 2回目以降は、文章が変わった行と新しい問題の分だけ作ります。問題を追加・修正したら同じコマンドを実行するだけです
- ボイスの選び方：実行するとボイスの一覧が出るので番号を入力。Enter だけなら前回と同じボイス、`t 8` のように入力すると試聴できます。選んだボイスは `tools/voice_setting.json` に保存され、次回の既定になります
- 一覧を出さずにすぐ作りたいときは `python tools/make_voice.py --speaker 8`。ボイスを変えると全部作り直しになります（開始前に確認が出ます）
- 読み間違いを直す：`python tools/make_voice.py --only-daihon` で台本だけ作って確認 → 全問に効かせたい読みは `tools/yomi.tsv` に「表記<TAB>読み」で追加、その問題だけなら JSON の `readQuestion` / `readExplanation` に書く
- 読み上げ速度の設定は音声ファイルの再生速度にも反映されます（0.5 が等倍）

## 講義動画を作る（分野ごとの解説スライド＋読み上げ）
```bash
python tools/make_lecture.py 電源          # VOICEVOX を起動しておく
python tools/make_lecture.py all
```
- 台本は `tools/lecture/<分野>.json`、図は `tools/lecture/fig/*.svg`、分野ごとの声は `tools/lecture/voices.json`
- 出力は `lectures/<分野>.mp4`（動画）と `.m4a`（音声だけ）。Git には入れない
- VOICEVOX 無しで試すときは `--engine sapi`（Windows 標準の音声）

## 問題の追加
`assets/questions/` に JSON を置いてビルドし直すだけで読み込まれます（ファイル名は自由）。

```json
{
  "id": "H-100",               // 全ファイルで重複しないID
  "subject": "法規",           // 「法規」か「無線工学」
  "category": "運用",
  "question": "問題文",
  "choices": ["選択肢1", "選択肢2", "選択肢3", "選択肢4"],
  "answer": 2,                 // 正解の番号（1〜4）
  "explanation": "解説",
  "image": null,               // 図がある場合 "assets/images/xxx.png"
  "readQuestion": "読み上げ用の問題文（任意）",
  "readExplanation": "読み上げ用の解説（任意）",
  "source": "出典メモ"
}
```
- Ω・MHz・W・V・A などの単位は自動で「オーム」「メガヘルツ」…に変換して読みます
- 「J3E」「5D-2V」のように読み間違えやすいものは readQuestion / readExplanation に読み方を書いてください

## 収録している問題
- `houki_original.json`（22問）/ `kougaku_original.json`（28問）：頻出テーマをもとにした自作問題
- `reidai_based.json`（法規31問・無線工学30問）：日本無線協会が公開している CBT 例題（法規・工学 各3回分）を元に、問題文を言い換えたもの。図が必要な問題と、回をまたいで重複する問題は省略。
  - 正解は例題 PDF の網掛けから読み取れなかったため、内容から判断して設定しています（`answerChecked: false`）。気になる問題は `sourceUrl` の PDF で網掛けを確認してください
  - 法規 No.2 は 2024年2月版で、免許状に関する問題は制度変更で古くなっている可能性があります（`note` に記載）

## 公式の例題を取り込む
日本無線協会がCBT試験の例題（法規・工学 各3回分、正解付き）を公開しています。
https://www.nichimu.or.jp/kshiken/siken/vcmsFolder_856/vcms_856.html

```bash
pip install pdfplumber
python tools/nichimu_pdf_to_json.py 4ama_E_01.pdf --subject 法規 --tag E01
python tools/nichimu_pdf_to_json.py 4ama_A_01.pdf --subject 無線工学 --tag A01
cp nichimu_*.json assets/questions/
```
正解は網掛けから自動推定します。推定できなかった問題や図のある問題は、スクリプトの表示に従って手で補ってください。
正解が未設定（answer: 0）の問題はアプリが自動で除外し、ホームに警告を出します。
同じ PDF を取り込むと `reidai_based.json` と内容が重複するので、協会が例題を新しくしたときなどに使ってください。

## 構成
```
lib/
  main.dart / app_state.dart / theme.dart
  models/question.dart
  data/question_repository.dart   assets/questions/*.json の読み込み
  services/tts_service.dart       読み上げ（VOICEVOX 音声 → 無ければ flutter_tts）と単位の読み替え
  services/progress_store.dart    学習記録・設定（shared_preferences）
  screens/  home / quiz / listen / exam
  widgets/  s_meter / question_widgets
assets/questions/  houki_original.json / kougaku_original.json / reidai_based.json
assets/voice/      VOICEVOX 音声（make_voice.py が作る）
tools/make_voice.py         台本づくり＋VOICEVOX で音声を一括生成
tools/daihon.tsv            台本（make_voice.py が作り直す）
tools/yomi.tsv              読み方の追加辞書
tools/nichimu_pdf_to_json.py
```
