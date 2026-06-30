# VPNセキュリティーマスター

VPN・オンラインセキュリティのアフィリエイト情報サイト。
Gadget Line と同一構成（Python静的生成 → Cloudflare Pages）。

## 構成

- **本番ドメイン**: https://vpn.best-recommend.com
- **Cloudflare Pages プロジェクト**: `vpn-security-master`
- **GitHubリポジトリ**: `jplabdiamond-jpg/vpn-security-master`
- **方式**: 静的HTMLサイト（`auto_publish.py` でHTML生成）

## ディレクトリ

```
.
├── articles/            記事ソース(JSON) と _ranking.json
├── site/                公開ディレクトリ（生成物）
│   ├── index.html
│   ├── articles/*.html
│   ├── css/style.css
│   ├── js/main.js
│   └── _headers
├── auto_publish.py      静的サイトジェネレーター
├── deploy-cf.sh         wrangler 直接デプロイ
└── wrangler.toml
```

## 使い方

### サイト再生成

```bash
python3 auto_publish.py
```

### 新規記事の雛形作成

```bash
python3 auto_publish.py --new
```

`articles/<slug>.json` を編集して再生成すると `site/articles/<slug>.html` が出力されます。

## デプロイ（2系統）

1. **GitHub連携**（自動）: `git push` すると Cloudflare Pages が自動ビルド・デプロイ。
2. **直接デプロイ**（確実）: `bash deploy-cf.sh` で wrangler 経由デプロイ（GitHub認証不要）。

## 記事JSONの書き方

`blocks` に各要素を配列で記述：

| type | 用途 |
|------|------|
| `p` | 段落（HTML可: `<strong>` `<a>`） |
| `h2` / `h3` | 見出し（h2は `id` で目次に反映） |
| `ul` / `ol` | リスト（`items`配列） |
| `callout` | 補足ボックス（`warn:true`で警告色） |
| `table` | 比較表（`headers` + `rows`） |
| `cta` | CTAボックス（`title` `text` `label` `url`） |
