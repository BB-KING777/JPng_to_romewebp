# JPng_to_romewebp

うちのサークルで使ってた日本語ファイル名をローマ字に変換するやつです。

## これ何？

日本語のファイル名って海外の人と共有するときとか、サーバーにアップするときとかで文字化けしたりして面倒じゃないですか？そういうときに使えるツールです。

「資料１　売上データ.xlsx」→「shiryo1_uriagedata.xlsx」みたいな感じで変換してくれます。

最近WebPの変換機能も追加しました。PNGとかJPGをWebPにしてファイルサイズ小さくできます。

## 何ができる？

- 日本語ファイル名 → ローマ字ファイル名
- スペースとか変な文字も安全な文字に変換
- 同じ名前のファイルがあったら勝手に番号つけてくれる
- JPG/PNGをWebPに変換（やりたい人だけ）
- 何を変更したかログに残る
- 実行前にプレビューも見れる

## 準備

### 必要なもの

- Python 3.6以上
- MeCab（これがちょっと面倒）
- あとはPythonのライブラリいくつか

### MeCabのインストール

#### Windows
1. [MeCabの公式サイト](https://taku910.github.io/mecab/)からインストーラダウンロード
2. インストールしてPATHを通す（ここで詰まる人多い）

#### Mac
```bash
# Homebrewで入れる
brew install mecab mecab-ipadic

# M1/M2/M3 Macの人は環境変数も設定
export PATH="/opt/homebrew/bin:$PATH"
```

#### Linux（Ubuntu/Debian）
```bash
sudo apt-get install mecab mecab-ipadic-utf8 libmecab-dev
```

### Pythonの準備

```bash
# 仮想環境作る（推奨）
python -m venv venv

# 仮想環境を有効化
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# パッケージインストール
pip install -r requirements.txt
```

## 使い方

1. main.pyをファイルがあるフォルダに置く
2. そのフォルダでコマンド実行

```bash
python main.py
```

3. 画像ファイルがあったらWebP変換するか聞かれる
4. プレビューが表示される
5. よければ「y」で実行

## 実行例

```
日本語ファイル名変換ツール（WebP変換機能付き）
==================================================
変換対象: 3 ファイル

画像ファイル: 1 ファイル
画像ファイル名: スクショ.png

画像ファイル（JPG/PNG）をWebPに変換しますか？ (y/N): y

=== 変換予定のファイル ===

変更前: 会議資料　2024年度.pptx
変更後: kaigishiryo_2024nendo.pptx
--------------------------------------------------
変更前: スクショ.png
変更後: sukusyo.webp
  → 画像形式: WebPに変換
--------------------------------------------------

2 ファイルの名前を変更します。
実行しますか？ (y/N): y
```

## 困ったとき

### MeCabでエラーが出る
- Windowsの人：PATHちゃんと通ってる？管理者権限で再インストールしてみて
- Macの人：Homebrewで入れ直してみて。環境変数も確認
- みんな：`mecab --version`でインストール確認

### Pillowでエラーが出る
```bash
pip install --upgrade pip wheel setuptools
pip install Pillow
```

### 文字化けする
- Windows：`chcp 65001`してからもう一回
- Mac/Linux：ターミナルの文字エンコーディングをUTF-8に

### その他
- エラーメッセージをよく読む
- 一回venv作り直してみる
- Google先生に聞く

## ファイル構成

```
your-project/
├── main.py                    # これがメイン
├── requirements.txt           # 必要なパッケージ
├── README.md                 # これ
├── venv/                     # 仮想環境
└── filename_conversion_log.txt # 実行後にできる履歴
```

## 注意点

- 大事なファイルはバックアップ取ってから使って
- WebP変換すると元のファイルは消える（置き換わる）
- ディレクトリ名は変更されない
- 変更履歴は自動で保存される

## なんで作ったの？

Webサイトに画像を載せる案件で、クライアントから送られてきた画像ファイルが全部日本語＋スペース入りの名前だったんです。

例：「新商品　キャンペーン画像　最終版.jpg」

これをそのままWebサーバーにアップロードすると：

- URLが「%E6%96%B0%E5%95%86%E5%93%81%20%E3%82%AD%E3%83%A3%E3%83%B3%E3%83%9A%E3%83%BC%E3%83%B3%E7%94%BB%E5%83%8F%20%E6%9C%80%E7%B5%82%E7%89%88.jpg」みたいになる
- HTMLのalt属性とかで管理するときに訳わからなくなる
- 開発チームで「あのファイルってどれ？」って毎回なる
- SEO的にもファイル名は英語の方がいい

手動で変換するのも面倒だし、漢字読めないファイルもあったので自動化しました。WebP機能は最近のWeb制作事情を考慮して追加。

## ライセンス

好きに使ってください。改造も配布も自由です。

## バグとか要望

何かあったらIssue立ててください。プルリクも歓迎です。

## その他

- WebP変換は品質80%でやってます（コードいじれば変更可）
- 透明PNGもちゃんとWebPになります
- macOS Big Sur以降なら標準でWebP見れます

---

作った人より
