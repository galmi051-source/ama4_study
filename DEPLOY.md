# GitHub Pages に公開して iPhone で使うまでの手順

上から順にやれば終わります。所要 20 分くらい。
以下 `<ユーザー名>` は自分の GitHub アカウント名に読み替えてください。
リポジトリ名は **`ama4_study`** にしてください（公開 URL のパスとビルド設定がこの名前で自動的に合います。別名にしてもワークフローはリポジトリ名を自動で拾うので動きますが、URL が変わります）。

## 0. 前提

- GitHub アカウントがある（無料プランで OK）
- `git` が入っている（`git --version` で確認。無ければ https://git-scm.com/download/win）
- このフォルダには既に `git init` 済みです（`.git` があります）。まだ何もコミットしていません

## 1. GitHub にリポジトリを作る（Web 画面）

1. https://github.com/new を開く
2. **Repository name**：`ama4_study`
3. **Public** を選ぶ（理由は下の「公開／非公開について」）
4. 「Add a README file」「.gitignore」「license」は **全部チェックしない**（手元に既にあるため）
5. 緑の **Create repository** を押す
6. 次に出る画面の URL `https://github.com/<ユーザー名>/ama4_study.git` を控える

## 2. 最初の push（手元の PowerShell）

プロジェクトのフォルダ（`pubspec.yaml` があるところ）で：

```bash
git add -A
```

```bash
git commit -m "Web版（PWA）・GitHub Pages デプロイ"
```

```bash
git remote add origin https://github.com/<ユーザー名>/ama4_study.git
```

```bash
git push -u origin main
```

初回はブラウザで GitHub のログインを求められることがあります（Git Credential Manager）。指示に従ってログインしてください。
音声ファイル 35MB が上がるので 1〜2 分かかります。

## 3. GitHub Pages を有効にする（Web 画面・1 回だけ）

1. `https://github.com/<ユーザー名>/ama4_study` を開く
2. 上のタブの **Settings**（歯車）→ 左メニューの **Pages**（「Code and automation」の中）
3. **Build and deployment** の **Source** のプルダウンを **「Deploy from a branch」→「GitHub Actions」** に変える（保存ボタンは無い。変えた瞬間に反映）

これだけです。`.github/workflows/deploy.yml` が「main に push されたらビルドして Pages に載せる」設定になっています。

## 4. 最初の公開を確認する

1. リポジトリの **Actions** タブを開く。「Deploy to GitHub Pages」というワークフローが動いている（黄色→緑になれば完了。3〜5 分）
   - 手順 3 より先に push した場合、最初の実行は Pages 未設定で失敗していることがあります。その場合は Actions → 左の「Deploy to GitHub Pages」→ 右上 **Run workflow** → **Run workflow** で再実行
2. 緑になったら `https://<ユーザー名>.github.io/ama4_study/` を PC のブラウザで開いて動くことを確認

赤（失敗）になったら、その実行をクリック → 失敗した job（build / deploy）→ 赤い行を開くとログが見えます。よくある原因：
- `flutter analyze` で警告扱いのエラー → 手元で `flutter analyze` を通してから push
- Pages の Source が GitHub Actions になっていない → 手順 3

## 5. iPhone でホーム画面に追加する

1. iPhone の **Safari** で `https://<ユーザー名>.github.io/ama4_study/` を開く（Chrome など他のブラウザでは「ホーム画面に追加」しても全画面にならないので Safari で）
2. 一度ホーム画面まで表示されるのを待つ（この時点でアプリ本体と問題データが端末に保存される）
3. 下の **共有ボタン**（□に↑）→ 下にスクロール → **「ホーム画面に追加」** → 右上 **追加**
4. ホーム画面に「4アマ学習」のアイコン（濃紺にアンテナ）が出る。以後はここから起動。Safari の枠が無い全画面で開く
5. 初回起動後、**設定（右上のアイコン）→「音声をまとめてダウンロード」** を Wi-Fi 環境で 1 回押しておくと、電波の無い場所でも全問聞けます（約 35MB）。押さなくても、再生した音声から順に端末に残ります

## 6. 以後の更新のしかた

問題を足したり直したりしたら：

```bash
python tools/make_voice.py
```

```bash
git add -A
```

```bash
git commit -m "問題追加"
```

```bash
git push
```

push して 3〜5 分で公開が更新されます。iPhone 側は **アプリを一度完全に閉じて（上スワイプで終了）、開き直す** と新しい版になります（1 回目の起動で裏で取得、2 回目で切り替わることがあります）。

## 公開／非公開について

- **無料プランでは GitHub Pages は Public リポジトリでしか使えません。** Private で Pages を使うには GitHub Pro（月 $4）が必要です
- 公開されるもの：ソースコード、問題 JSON、VOICEVOX の音声ファイル。URL を知っている人は誰でもアプリを開けます（検索エンジンには基本的に載りませんが、非公開ではありません）
- 気になる点：
  - `reidai_based.json` は日本無線協会の例題を言い換えたものです。個人利用の範囲なら問題になりにくいですが、公開リポジトリに置く形になります
  - VOICEVOX の音声は、キャラクターごとの利用規約でクレジット表記（例「VOICEVOX:ずんだもん」）が求められます。README に使用キャラクターを書いておくのが無難です（`tools/voice_setting.json` に選んだボイスが入っています）
- Private にしたい場合の代替案：Cloudflare Pages（無料・Private でも可・GitHub 連携でビルド自動化可）か、Netlify。必要ならワークフローを作り替えます

## 容量について

- 音声 35MB ＋ その他で 40MB 弱。GitHub の制限（1 ファイル 100MB、リポジトリ推奨 1GB 以下、Pages サイト 1GB 以下、Pages 転送 100GB/月）には遠く及びません
- 問題が今の 3〜4 倍に増えても余裕です
- Git は履歴を全部持つので、音声を作り直すたびに +35MB 溜まります。年に数回なら気にしなくて OK。気になってきたら Git LFS（無料枠 1GB）に移せます
