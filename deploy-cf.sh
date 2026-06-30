#!/usr/bin/env bash
# ============================================================
# deploy-cf.sh — Cloudflare Pages 直接デプロイ (wrangler)
# GitHub認証不要で確実にデプロイする経路。
# Gadget Line と同一方式。
# ============================================================
set -euo pipefail

PROJECT="vpn-security-master"     # Cloudflare Pages プロジェクト名
DIST="site"                       # 公開ディレクトリ
BRANCH="${1:-main}"               # 第1引数でブランチ指定可（既定: main）

cd "$(dirname "$0")"

echo "==> 静的サイトを再生成 (auto_publish.py)"
python3 auto_publish.py

echo "==> Cloudflare Pages へデプロイ: project=$PROJECT branch=$BRANCH dir=$DIST"
npx --yes wrangler pages deploy "$DIST" \
  --project-name "$PROJECT" \
  --branch "$BRANCH" \
  --commit-dirty=true

echo "==> 完了: https://vpn.best-recommend.com"
