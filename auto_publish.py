#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_publish.py — VPNセキュリティーマスター 静的サイトジェネレーター

articles/*.json の記事データから site/ 配下に静的HTMLを生成する。
Gadget Line と同一方式（Python静的生成 → Cloudflare Pages デプロイ）。
デザインは「ていねいな暮らし」風ミニマル（白基調・ブルーグレー）。

使い方:
    python3 auto_publish.py            # 全記事 + index を再生成
    python3 auto_publish.py --new      # 対話で新規記事JSONの雛形を作成

記事JSONのオプションフラグ:
    "featured": true   → ヒーローカルーセルに表示
    "special": true    → SPECIAL カルーセルに表示
    "pickup": true      → PICKUP 欄に表示
    "image": "...url"  → サムネ画像URL（無ければ emoji プレースホルダ）
"""

import json
import os
import sys
import glob
import html
import datetime

# ---- パス設定 ----------------------------------------------------------
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "articles")
SITE_DIR = os.path.join(ROOT, "site")
ART_OUT = os.path.join(SITE_DIR, "articles")

SITE_NAME = "VPNセキュリティーマスター"
SITE_DESC = "VPNとオンラインセキュリティを、ていねいにやさしく。"
DOMAIN = "https://vpn.best-recommend.com"
YEAR = datetime.date.today().year

# サイトのカテゴリ（ナビ・サイドバー共通）
CATEGORIES = ["VPN基礎", "VPN比較", "セキュリティ対策", "海外動画視聴", "トラブル解決", "編集部日記"]


# ---- 共通パーツ --------------------------------------------------------
def head(title, desc, pp="", canonical=""):
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE_NAME}">
<link rel="stylesheet" href="{pp}css/style.css">
</head>
<body>"""


def header(pp=""):
    nav = "".join(f'<a href="{pp}index.html#articles">{html.escape(c)}</a>' for c in CATEGORIES)
    return f"""<header class="site-header">
  <div class="container header-inner">
    <a class="logo" href="{pp}index.html"><span class="mark">&#9670;</span>{SITE_NAME}</a>
    <button class="nav-toggle" aria-label="メニュー" aria-expanded="false">&#9776;</button>
    <nav class="nav">{nav}</nav>
    <button class="search-btn" aria-label="検索" onclick="document.getElementById('site-search')&&document.getElementById('site-search').focus()">&#128269;</button>
  </div>
</header>"""


def footer(pp=""):
    links = "".join(f'<a href="{pp}index.html#articles">{html.escape(c)}</a>' for c in CATEGORIES[:4])
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-inner">
      <div class="brand">{SITE_NAME}
        <p>{SITE_DESC}<br>当サイトはアフィリエイト広告を利用しています。</p>
      </div>
      <div class="footer-links">{links}</div>
    </div>
    <div class="copyright">&copy; <span data-year>{YEAR}</span> {SITE_NAME}. All Rights Reserved.</div>
  </div>
</footer>
<script src="{pp}js/main.js"></script>"""


# ---- 記事本文ブロック --------------------------------------------------
def render_block(b):
    t = b.get("type")
    if t == "h2":
        return f'<h2 id="{b.get("id","")}">{html.escape(b["text"])}</h2>'
    if t == "h3":
        return f'<h3>{html.escape(b["text"])}</h3>'
    if t == "p":
        cls = ' class="lead"' if b.get("lead") else ""
        return f'<p{cls}>{b["text"]}</p>'
    if t == "balloon":
        side = "balloon right" if b.get("right") else "balloon"
        face = b.get("face", "&#128100;")
        name = html.escape(b.get("name", ""))
        return f'''<div class="{side}">
      <div class="avatar"><div class="face">{face}</div><div class="name">{name}</div></div>
      <div class="bubble">{b["text"]}</div>
    </div>'''
    if t == "point":
        head_label = html.escape(b.get("label", "POINT"))
        items = "".join(f"<li>{i}</li>" for i in b.get("items", []))
        lst = "ol" if b.get("ordered") else "ul"
        return f'<div class="point-box"><span class="pb-head">{head_label}</span><{lst}>{items}</{lst}></div>'
    if t == "figure":
        cap = b.get("caption", "")
        caphtml = f"<figcaption>{html.escape(cap)}</figcaption>" if cap else ""
        return f'<figure><img src="{html.escape(b["src"])}" alt="{html.escape(b.get("alt", cap))}" loading="lazy">{caphtml}</figure>'
    if t == "ul":
        return "<ul>" + "".join(f"<li>{i}</li>" for i in b["items"]) + "</ul>"
    if t == "ol":
        return "<ol>" + "".join(f"<li>{i}</li>" for i in b["items"]) + "</ol>"
    if t == "callout":
        cls = "callout warn" if b.get("warn") else "callout"
        return f'<div class="{cls}">{b["text"]}</div>'
    if t == "table":
        hr = "".join(f"<th>{html.escape(h)}</th>" for h in b["headers"])
        rows = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in b["rows"])
        return f'<div class="table-wrap"><table class="cmp"><thead><tr>{hr}</tr></thead><tbody>{rows}</tbody></table></div>'
    if t == "cta":
        return f'''<div class="cta-box">
      <h3>{html.escape(b["title"])}</h3>
      <p>{html.escape(b.get("text",""))}</p>
      <a class="btn" href="{b.get("url","#")}" rel="nofollow sponsored">{html.escape(b.get("label","詳しく見る"))}</a>
    </div>'''
    return ""


def build_toc(blocks):
    items = [b for b in blocks if b.get("type") == "h2" and b.get("id")]
    if not items:
        return ""
    lis = "".join(f'<li><a href="#{b["id"]}">{html.escape(b["text"])}</a></li>' for b in items)
    return f'<div class="toc"><h4>目次</h4><ol>{lis}</ol></div>'


# ---- サムネ（画像 or SVGアイキャッチ） ---------------------------------
# カテゴリごとの配色とモチーフ（オリジナルSVG・外部依存なし）
CAT_STYLE = {
    "VPN基礎":       ("#a8bdc0", "#c8d6d7", "lock"),
    "VPN比較":       ("#9bb0b3", "#bccccd", "chart"),
    "セキュリティ対策": ("#a3b6c0", "#c4d2d8", "shield"),
    "海外動画視聴":   ("#aeb9c4", "#cdd5dd", "globe"),
    "トラブル解決":   ("#b0bcb6", "#cfd7d2", "wrench"),
    "編集部日記":     ("#b9b3a6", "#d6d1c7", "pen"),
}

def _svg_motif(kind, cx, cy, color):
    if kind == "lock":
        return f'<rect x="{cx-22}" y="{cy-8}" width="44" height="34" rx="5" fill="{color}"/><path d="M{cx-13} {cy-8} v-8 a13 13 0 0 1 26 0 v8" fill="none" stroke="{color}" stroke-width="6"/><circle cx="{cx}" cy="{cy+7}" r="5" fill="#fff"/>'
    if kind == "chart":
        return f'<rect x="{cx-26}" y="{cy-2}" width="12" height="26" rx="2" fill="{color}"/><rect x="{cx-8}" y="{cy-16}" width="12" height="40" rx="2" fill="{color}"/><rect x="{cx+10}" y="{cy-26}" width="12" height="50" rx="2" fill="{color}"/>'
    if kind == "shield":
        return f'<path d="M{cx} {cy-26} l24 9 v14 c0 16 -12 24 -24 30 c-12 -6 -24 -14 -24 -30 v-14 z" fill="{color}"/><path d="M{cx-9} {cy+2} l7 8 14 -15" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
    if kind == "globe":
        return f'<circle cx="{cx}" cy="{cy}" r="28" fill="none" stroke="{color}" stroke-width="5"/><ellipse cx="{cx}" cy="{cy}" rx="12" ry="28" fill="none" stroke="{color}" stroke-width="4"/><line x1="{cx-28}" y1="{cy}" x2="{cx+28}" y2="{cy}" stroke="{color}" stroke-width="4"/>'
    if kind == "wrench":
        return f'<path d="M{cx+18} {cy-20} a14 14 0 1 0 6 18 l12 12 8 -8 -12 -12 a14 14 0 0 0 -14 -10 z" fill="{color}"/>'
    if kind == "pen":
        return f'<path d="M{cx-20} {cy+20} l4 -14 28 -28 10 10 -28 28 z" fill="{color}"/><path d="M{cx+12} {cy-22} l10 10" stroke="#fff" stroke-width="3"/>'
    return f'<circle cx="{cx}" cy="{cy}" r="22" fill="{color}"/>'


def svg_eyecatch(art):
    cat = art.get("category", "VPN基礎")
    c1, c2, kind = CAT_STYLE.get(cat, CAT_STYLE["VPN基礎"])
    motif = _svg_motif(kind, 200, 95, "#ffffff")
    return (
        f'<svg viewBox="0 0 400 240" xmlns="http://www.w3.org/2000/svg" '
        f'preserveAspectRatio="xMidYMid slice" role="img" aria-label="{html.escape(art["title"])}" '
        f'style="width:100%;height:100%;display:block">'
        f'<rect width="400" height="240" fill="{c1}"/>'
        f'<circle cx="330" cy="40" r="80" fill="{c2}" opacity="0.55"/>'
        f'<circle cx="60" cy="210" r="60" fill="{c2}" opacity="0.4"/>'
        f'{motif}'
        f'<text x="200" y="170" text-anchor="middle" fill="#ffffff" '
        f'font-family="serif" font-size="15" letter-spacing="2" opacity="0.95">{html.escape(cat)}</text>'
        f'</svg>'
    )


def thumb(art, cls="ph"):
    img = art.get("image")
    if img:
        return f'<img src="{html.escape(img)}" alt="{html.escape(art["title"])}" loading="lazy">'
    return svg_eyecatch(art)


# ---- 1記事をHTML化 -----------------------------------------------------
def build_article(art):
    slug = art["slug"]
    title = art["title"]
    desc = art.get("description", "")
    cat = art.get("category", "VPN基礎")
    date = art.get("date", str(datetime.date.today()))
    canonical = f"{DOMAIN}/articles/{slug}.html"
    body_html = build_toc(art["blocks"]) + "".join(render_block(b) for b in art["blocks"])
    schema = {
        "@context": "https://schema.org", "@type": "Article", "headline": title,
        "description": desc, "datePublished": date,
        "author": {"@type": "Organization", "name": SITE_NAME},
        "publisher": {"@type": "Organization", "name": SITE_NAME},
        "mainEntityOfPage": canonical,
    }
    out = f"""{head(title + " | " + SITE_NAME, desc, "../", canonical)}
{header("../")}
<section class="article-hero">
  <div class="container">
    <div class="breadcrumb"><a href="../index.html">HOME</a> &nbsp;/&nbsp; <span>{html.escape(cat)}</span></div>
    <span class="cat">{html.escape(cat)}</span><span class="date">{html.escape(date)}</span>
    <h1>{html.escape(title)}</h1>
  </div>
</section>
{f'<figure class="article-eyecatch"><img src="{html.escape(art["image"])}" alt="{html.escape(title)}" loading="eager"></figure>' if art.get("image") else ""}
<article class="article-body">
  <div class="container">{body_html}</div>
</article>
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
{footer("../")}
</body>
</html>"""
    os.makedirs(ART_OUT, exist_ok=True)
    with open(os.path.join(ART_OUT, slug + ".html"), "w", encoding="utf-8") as f:
        f.write(out)
    return {**art, "date": date, "category": cat}


# ---- index 各パーツ ----------------------------------------------------
def hero_slides(items):
    s = ""
    for a in items:
        img = a.get("image")
        if img:
            style = f' style="background-image:url({html.escape(img)})"'
            ph = ""
            cls = "hero-slide"
        else:
            style = ""
            ph = f'<div class="hero-svg">{svg_eyecatch(a)}</div>'
            cls = "hero-slide hero-svg-slide"
        s += f"""<div class="{cls}"{style}>{ph}
        <div class="hero-caption">
          <a href="articles/{a['slug']}.html">
            <span class="cat">{html.escape(a['category'])}</span><span class="date">{html.escape(a['date'])}</span>
            <h2>{html.escape(a['title'])}</h2>
          </a>
        </div></div>"""
    return s


def entry_card(a, blog=False):
    if blog:
        return f"""<a class="entry blog-entry" href="articles/{a['slug']}.html">
        <div class="thumb">{thumb(a)}</div>
        <span class="date">{html.escape(a['date'])}</span>
        <h3>{html.escape(a['title'])}</h3>
      </a>"""
    return f"""<a class="entry" href="articles/{a['slug']}.html">
        <div class="thumb">{thumb(a)}</div>
        <p class="cat">{html.escape(a['category'])}<span class="date">{html.escape(a['date'])}</span></p>
        <h3>{html.escape(a['title'])}</h3>
      </a>"""


def special_slides(items):
    s = ""
    for a in items:
        s += f"""<div class="special-slide">
        <a class="card-lg" href="articles/{a['slug']}.html">{thumb(a)}
          <div class="cap"><span class="cat">{html.escape(a['category'])}</span><span class="date">{html.escape(a['date'])}</span>
          <h3>{html.escape(a['title'])}</h3></div>
        </a></div>"""
    return s


def build_index(cards):
    by_date = sorted(cards, key=lambda c: c["date"], reverse=True)
    featured = [c for c in by_date if c.get("featured")] or by_date[:3]
    special = [c for c in by_date if c.get("special")] or by_date[:3]
    pickup = [c for c in by_date if c.get("pickup")][:4] or by_date[:4]
    latest = by_date[:4]
    blog = [c for c in by_date if c.get("category") == "編集部日記"][:4] or by_date[-4:]

    cat_html = "".join(f'<li><a href="#articles">{html.escape(c)}</a></li>' for c in CATEGORIES)

    out = f"""{head(SITE_NAME + " | VPN・オンラインセキュリティの情報サイト", SITE_DESC, "", DOMAIN + "/")}
{header("")}
<section class="hero">
  <button class="hero-arrow prev" aria-label="前へ">&#8249;</button>
  <div class="hero-track">{hero_slides(featured)}</div>
  <button class="hero-arrow next" aria-label="次へ">&#8250;</button>
  <div class="hero-dots"></div>
</section>

<div class="main-wrap">
  <div class="container">
    <div class="layout">
      <div class="main-col">
        <div class="sec-head"><span class="en">PICKUP</span><span class="ja">注目の記事</span></div>
        <div class="pickup-grid">{"".join(entry_card(a) for a in pickup)}</div>

        <section class="section" id="articles">
          <div class="sec-head"><span class="en">LATEST</span><span class="ja">新着記事</span>
            <a class="viewall" href="#articles">VIEW ALL <span class="circ">&#8594;</span></a></div>
          <div class="col4">{"".join(entry_card(a) for a in latest)}</div>
        </section>
      </div>

      <aside class="sidebar">
        <h4>CATEGORY</h4>
        <ul class="cat-list">{cat_html}</ul>
        <h4>SEARCH</h4>
        <form class="search-box" onsubmit="return false;">
          <input id="site-search" type="search" placeholder="記事を探す" aria-label="記事を探す">
          <button type="submit" aria-label="検索">&#128269;</button>
        </form>
      </aside>
    </div>

    <section class="section">
      <div class="sec-head"><span class="en">SPECIAL</span><span class="ja">特集記事</span></div>
      <div class="special-carousel">
        <button class="special-arrow prev" aria-label="前へ">&#8249;</button>
        <div class="special-track">{special_slides(special)}</div>
        <button class="special-arrow next" aria-label="次へ">&#8250;</button>
      </div>
    </section>

    <section class="section">
      <div class="sec-head"><span class="en">BLOG</span><span class="ja">編集部日記</span>
        <a class="viewall" href="#articles">VIEW ALL <span class="circ">&#8594;</span></a></div>
      <div class="blog-grid">{"".join(entry_card(a, blog=True) for a in blog)}</div>
    </section>
  </div>
</div>
{footer("")}
</body>
</html>"""
    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(out)


# ---- 新規記事JSON雛形 --------------------------------------------------
def new_article_template():
    slug = input("slug (英数字): ").strip() or "sample-article"
    title = input("タイトル: ").strip() or "サンプル記事タイトル"
    tmpl = {
        "slug": slug, "title": title,
        "description": "記事の概要（120字程度）。",
        "category": CATEGORIES[0], "date": str(datetime.date.today()),
        "emoji": "&#9670;", "image": "",
        "featured": False, "special": False, "pickup": False,
        "blocks": [
            {"type": "p", "text": "導入文。"},
            {"type": "h2", "id": "s1", "text": "見出し1"},
            {"type": "p", "text": "本文。<strong>強調</strong>可。"},
            {"type": "cta", "title": "おすすめVPNをチェック", "text": "30日返金保証つき。", "label": "公式サイトへ", "url": "#"},
        ],
    }
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, slug + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tmpl, f, ensure_ascii=False, indent=2)
    print("作成:", path)


# ---- メイン ------------------------------------------------------------
def main():
    if "--new" in sys.argv:
        new_article_template()
        return
    os.makedirs(SITE_DIR, exist_ok=True)
    cards = []
    for jf in sorted(glob.glob(os.path.join(DATA_DIR, "*.json"))):
        if os.path.basename(jf).startswith("_"):
            continue
        with open(jf, encoding="utf-8") as f:
            art = json.load(f)
        cards.append(build_article(art))
        print("記事生成:", art["slug"] + ".html")
    build_index(cards)
    print(f"index.html 生成完了（記事 {len(cards)} 本）")


if __name__ == "__main__":
    main()
