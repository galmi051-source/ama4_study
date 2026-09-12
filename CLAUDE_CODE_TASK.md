# 依頼：Flutterアプリを iPhone で使える Web 版（PWA）にして GitHub Pages に公開したい

## 状況

- 手元に Flutter プロジェクト `ama4_study` のフォルダがある（`lib/` `assets/` `tools/` `pubspec.yaml` `analysis_options.yaml` `README.md`）
- **`android/` `ios/` `web/` などのプラットフォーム用フォルダはまだ無い**（`flutter create` で作る必要がある）
- 第四級アマチュア無線技士の試験対策アプリ。問題・正解・解説を音声で読み上げる。完全に個人用で、配布はしない
- 開発環境は **Windows**。Mac は持っていないので iOS ネイティブビルドはできない。だから Web 版にして iPhone の Safari から「ホーム画面に追加」で使いたい
- `assets/voice/` に VOICEVOX で作った音声ファイル（`.m4a`、約450ファイル）が入っている。これらをアプリに同梱して再生する
- 私は Flutter は触れるが Web デプロイはあまり詳しくない

## ゴール

1. ローカルで `flutter run -d chrome` が動く
2. GitHub Pages に公開され、iPhone の Safari で開ける
3. 「ホーム画面に追加」でアプリのように全画面で起動する
4. 問題・正解・解説の VOICEVOX 音声が iPhone で鳴る
5. **今後 `git push` するだけで自動的に再公開される**（手作業でのビルド・アップロードは避けたい）

## やってほしいこと

### 1. Web プラットフォームを追加

```
flutter create --org com.tky --platforms web .
```

既存の `lib/` `assets/` `pubspec.yaml` は上書きしないこと。`flutter pub get` して `flutter run -d chrome` が通るところまで確認してほしい。

エラーが出たら直してほしい。特に以下は Web で問題が出るかもしれない箇所：

- `wakelock_plus`（`lib/screens/listen_screen.dart` で使用）— Web では Screen Wake Lock API になるはず。iOS Safari が未対応なら、例外で落ちないように try-catch するか、Web では無効にする
- `audioplayers`（`lib/services/tts_service.dart` で使用）— `AssetSource` で `assets/voice/*.m4a` を再生している
- `flutter_tts` — 音声ファイルが無い文の読み上げに使うフォールバック。Web では Web Speech API になる
- `AssetManifest.loadFromAssetBundle` — `assets/voice/` にあるファイルの一覧取得に使っている。Web でも動くか確認してほしい

### 2. iOS Safari の音声再生対策（重要）

iOS Safari は、**ユーザーの操作なしに音を鳴らせない**制限がある。特に「ながら聞き」画面（`lib/screens/listen_screen.dart`）は、問題→選択肢→正解→解説を自動で連続再生するので、ここが動かないと困る。

最初の1音が再生できれば以降は続けられるはずなので、再生開始ボタンのタップをきっかけに音声を有効化する形にしてほしい。無音を1回鳴らして解除する、`AudioPlayer` のインスタンスを使い回す、などやり方はいくつかあると思うので、確実な方法を選んでほしい。**実機で確認できないので、なぜその方法なら動くはずかを説明してほしい。**

あわせて以下も確認・対応してほしい：

- iPhone のサイレントスイッチが ON でも音が出るようにできるか（`audioplayers` の AudioContext 設定）
- 画面をロックしたとき・別アプリに切り替えたときに再生がどうなるか。止まる場合はその旨をアプリ内に一言表示してほしい
- 再生が失敗したときに黙って止まらず、画面に理由が出るようにしてほしい

### 3. PWA として整える

- `web/manifest.json`：アプリ名は「4アマ ながら学習」、`display: standalone`、`orientation: portrait`
- アイコン：無線っぽいシンプルなもの（アンテナや電波のモチーフ）を作って必要なサイズを揃えてほしい。凝らなくていい
- iOS Safari 用の `apple-touch-icon` と、ホーム画面から起動したときに全画面になる meta タグを `web/index.html` に追加
- オフラインで使えるようにしてほしい。電車内など電波が無い場所で使う。音声ファイルが約450個あるので、Service Worker のキャッシュ戦略は考えて決めてほしい（初回に全部キャッシュすると重いかもしれない）
- ブラウザのタブで開いたときのタイトルも設定

### 4. GitHub Pages に自動デプロイ

- GitHub Actions のワークフローを作って、`main` に push したら自動でビルド・公開されるようにしてほしい
- プロジェクト名のサブパス（`https://<ユーザー名>.github.io/ama4_study/`）で公開されるので、`--base-href` の指定を忘れないこと
- `.gitignore` を用意してほしい。`build/` や `.dart_tool/` は除外。ただし **`assets/voice/*.m4a` はコミットに含める**（これが無いと音が鳴らない）
- 音声ファイルの合計サイズを確認して、GitHub の制限に引っかかりそうなら教えてほしい
- リポジトリは公開・非公開どちらがいいか、Pages が使えるかも含めて教えてほしい

### 5. 私がやる作業の手順書

GitHub リポジトリの作成、Pages の設定（どの画面のどこを押すか）、最初の push、iPhone でホーム画面に追加するまでを、上から順にやればいい形で `DEPLOY.md` に書いてほしい。GitHub の Web 画面での操作は、どのメニューかまで具体的に書いてくれると助かる。

## 補足

- `tools/make_voice.py` は VOICEVOX で音声を作り直すスクリプト。問題を追加したら実行する。**この実行は私が手元でやる**ので、GitHub Actions 側で動かす必要はない。生成された音声をコミットして push する流れになる。この流れで問題ないか、もっと良い方法があれば意見がほしい
- 問題データは `assets/questions/*.json`。今後増やしていく
- 作業中に「これは私に確認したほうがいい」と思った判断（無料/有料の分かれ目、リポジトリの公開範囲など）は、勝手に進めず聞いてほしい
- 最後に、実機で確認すべき項目のチェックリストを出してほしい。特に音声まわりは Windows 側で検証できないので、iPhone で何をどう試せばいいか具体的に
