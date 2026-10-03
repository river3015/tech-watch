import html
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from .collector import JST, canonical_url

CATEGORIES = {'community': 'IT界隈の話題・読みもの', 'engineering': '企業の実践・技術ブログ',
              'official': '公式の更新情報', 'news': '技術ニュース',
              'podcast': 'ポッドキャスト'}


def category(article):
    values = {s['category'] for s in article['sources']}
    return next((c for c in CATEGORIES if c in values), 'news')


def curate(articles, limit=5):
    groups = defaultdict(list)
    for article in sorted(articles, key=lambda a: (a.get('published_at') or a['collected_at'], a['id']), reverse=True):
        groups[category(article)].append(article)
    selected = []
    for group in CATEGORIES:
        # Round robin across sources to avoid a prolific feed filling the digest.
        queues = defaultdict(list)
        for article in groups[group]:
            queues[article['sources'][0]['id']].append(article)
        count = 0
        while any(queues.values()) and count < limit:
            for queue in queues.values():
                if queue and count < limit:
                    selected.append(queue.pop(0))
                    count += 1
    return selected


def md_text(value):
    for char in ('\\', '[', ']', '*', '_', '`', '<', '>'):
        value = value.replace(char, '\\' + char)
    return value.replace('\n', ' ')


def digest(day, articles):
    selected = curate(articles)
    lines = [f'# {day} のまとめ', '', f'収集 {len(articles)} 件 / ピックアップ {len(selected)} 件', '',
             '各カテゴリから最大5件を、情報源が偏らないように選んでいます。概要は配信フィードの抜粋です。', '']
    for group, label in CATEGORIES.items():
        rows = [a for a in selected if category(a) == group]
        if not rows:
            continue
        lines.extend([f'## {label}', ''])
        for a in rows:
            url = a['url'].replace('(', '%28').replace(')', '%29')
            lines.append(f'- [{md_text(a["title"])}]({url}) — {md_text(a["sources"][0]["name"])}')
        lines.append('')
    if not selected:
        lines.append('新着記事はありません。収集結果も確認してください。')
    return '\n'.join(lines) + '\n'


def card(article, picked):
    escape = html.escape
    try:
        url = canonical_url(article['url'])
    except ValueError:
        return ''
    label = CATEGORIES[category(article)]
    sources = ' / '.join(s['name'] for s in article['sources'])
    date = article_day(article) if article.get('published_at') else '公開日不明（収集日で表示）'
    return f'''<article class="card" data-category="{category(article)}" data-picked="{str(picked).lower()}">
<div class="meta">{escape(label)} <span>{escape(date)}</span></div>
<h2><a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(article['title'])}</a></h2>
<p>{escape(article.get('summary', ''))}</p><footer>{escape(sources)}</footer></article>'''


def article_day(article):
    timestamp = article.get('published_at') or article['collected_at']
    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    return (dt if dt.tzinfo else dt.replace(tzinfo=JST)).astimezone(JST).strftime('%Y-%m-%d')


def build(data_dir, output_dir, now=None):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    today = (now or datetime.now(JST)).astimezone(JST).strftime('%Y-%m-%d')
    groups = defaultdict(list)
    reports = []
    has_data = False
    for path in sorted(Path(data_dir).glob('*/*/*/articles.json')):
        has_data = True
        collection_day = '-'.join(path.parent.parts[-3:])
        articles = json.loads(path.read_text(encoding='utf-8'))
        for article in articles:
            groups[article_day(article)].append(article)
        report_path = path.parent / 'collection.json'
        if report_path.exists():
            reports.append(json.loads(report_path.read_text(encoding='utf-8')))
        # The persisted digest remains a record of that collection day's new items.
        (path.parent / 'digest.md').write_text(digest(collection_day, articles), encoding='utf-8')
    (output / 'style.css').write_text(CSS, encoding='utf-8')
    (output / 'app.js').write_text(JS, encoding='utf-8')
    if not has_data:
        (output / 'index.html').write_text(shell('<h1>tech-watch</h1><p>まだ収集データがありません。先に収集処理を実行してください。</p>', ''), encoding='utf-8')
        return 0
    groups.setdefault(today, [])
    days = sorted(groups, reverse=True)
    report = max(reports, key=lambda r: r['collected_at']) if reports else None
    failures = [s for s in report['sources'] if s['status'] == 'error'] if report else []
    status = '収集結果の記録なし'
    if report:
        status = f'最終収集 {html.escape(report["collected_at"][:19].replace("T", " "))} JST · 成功 {report["successes"]} / 失敗 {report["failures"]}'
    errors = ''.join(f'<li>{html.escape(s["name"])}：{html.escape(s["error"])}</li>' for s in failures)
    archive = ''.join(f'<a href="{day}.html">{day}<span>{len(groups[day])}件</span></a>' for day in days)
    for day in days:
        articles = sorted(groups[day], key=lambda a: (a.get('published_at') or a['collected_at'], a['id']), reverse=True)
        selected = curate(articles)
        ids = {a['id'] for a in selected}
        tabs = ''.join(f'<a href="{date}.html" {"aria-current=page" if date == day else ""}>{date}{"（今日）" if date == today else ""}<span>{len(groups[date])}件</span></a>' for date in days)
        body = f'''<div class="eyebrow">DAILY TECH JOURNAL</div><h1>{day}<small>日々の技術と、界隈の話題。</small></h1>
<p class="intro">日本時間の公開日ごとに、その日の全記事を読めます。公開日不明の記事は収集日に表示します。</p>
<nav class="day-tabs" aria-label="公開日を選択">{tabs}</nav>
<div class="stats"><strong>{len(articles)}</strong> この日の記事 <strong>{len(selected)}</strong> ピックアップ</div>
<details class="health" {'open' if failures else ''}><summary>{status}</summary><ul>{errors}</ul><p>概要はフィードの抜粋です。収集済みの記事を表示しています。</p></details>
<div class="controls"><label>記事を検索<input id="search" type="search" placeholder="キーワード・情報源で検索"></label>
<label>カテゴリ<select id="category"><option value="all">すべて</option>{''.join(f'<option value="{key}">{label}</option>' for key, label in CATEGORIES.items())}</select></label>
<label>表示<select id="mode"><option value="all">この日の全記事</option><option value="picked">ピックアップ（最大20件）</option></select></label></div>
<p id="count" aria-live="polite"></p><div class="cards">{''.join(card(a, a['id'] in ids) for a in articles)}</div>
<p id="empty" hidden>この日、または選択した条件に合う記事がありません。別の日付や収集結果を確認してください。</p>'''
        page = shell(body, archive)
        (output / f'{day}.html').write_text(page, encoding='utf-8')
        if day == today:
            (output / 'index.html').write_text(page, encoding='utf-8')
    return len(days)


def shell(body, archive):
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>tech-watch · 日々の技術と話題</title><link rel="stylesheet" href="style.css"><script src="app.js" defer></script></head><body><header><a class="brand" href="index.html">tech-watch<span>自分のための、技術の読みもの。</span></a></header><div class="layout"><main>{body}</main><aside><h2>ARCHIVE</h2><nav>{archive}</nav><p>新しい知識も、気軽な話題も。<br>元記事へ進んで続きを読む。</p></aside></div></body></html>'''

CSS = '''
:root{color-scheme:light;--ink:#192c32;--muted:#617278;--accent:#006d68;--line:#dce4e1}*{box-sizing:border-box}body{margin:0;background:#f6f7f2;color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Helvetica Neue","Hiragino Sans",sans-serif;line-height:1.7}header{padding:24px 5vw;border-bottom:1px solid var(--line);background:#fff}.brand{font-size:24px;font-weight:800;text-decoration:none;color:var(--ink);letter-spacing:-1px}.brand span{font-size:12px;color:var(--muted);letter-spacing:0;margin-left:20px;font-weight:400}.layout{max-width:1280px;margin:48px auto;padding:0 32px;display:grid;grid-template-columns:minmax(0,1fr) 210px;gap:48px}.eyebrow{font-size:11px;font-weight:700;letter-spacing:3px;color:var(--accent)}h1{font-size:44px;letter-spacing:-1px;line-height:1.3;margin:16px 0}h1 small{display:block;font-size:23px;margin-top:14px;letter-spacing:0}.intro{color:var(--muted)}.stats{display:flex;align-items:baseline;gap:12px;margin:24px 0}.stats strong{font-size:30px;color:var(--accent)}.health{border:1px solid var(--line);padding:12px 16px;font-size:12px;border-radius:8px;background:#fff}.health summary{cursor:pointer}.controls{display:flex;gap:16px;flex-wrap:wrap;margin:28px 0 12px}.controls label{font-size:11px;color:var(--muted);flex:1}.controls label:first-child{flex:2}input,select{display:block;width:100%;min-width:150px;padding:12px;margin-top:5px;border:1px solid var(--line);border-radius:6px;background:#fff;color:var(--ink);font:inherit;font-size:14px}#count{font-size:12px;color:var(--muted)}.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.card{background:#fff;border:1px solid var(--line);border-radius:10px;padding:22px;display:flex;flex-direction:column}.meta{font-size:10px;color:var(--accent);display:flex;justify-content:space-between;gap:8px}.meta span{color:var(--muted);white-space:nowrap}.card h2{font-size:17px;line-height:1.65;margin:14px 0}.card a{color:var(--ink);text-decoration:none}.card a:hover{color:var(--accent);text-decoration:underline}.card p{font-size:12px;color:var(--muted);overflow-wrap:anywhere;margin-top:0}.card footer{margin-top:auto;padding-top:12px;border-top:1px solid var(--line);font-size:11px;color:var(--muted)}aside h2{font-size:11px;letter-spacing:2px;margin-top:0}aside nav a{display:flex;justify-content:space-between;color:var(--ink);text-decoration:none;padding:10px 0;border-bottom:1px solid var(--line);font-size:13px}aside nav span,aside p{font-size:11px;color:var(--muted)}aside p{margin-top:28px}[hidden]{display:none!important}@media(max-width:850px){.layout{grid-template-columns:1fr;margin:30px auto;padding:0 20px;gap:36px}.brand span{display:block;margin-left:0}.cards{grid-template-columns:1fr}h1{font-size:34px}h1 small{font-size:21px}.controls{gap:10px}aside nav{display:flex;flex-wrap:wrap;gap:16px}aside nav a{gap:12px}}'''

JS = '''
const search = document.querySelector('#search');
if (search) {
  const category = document.querySelector('#category');
  const mode = document.querySelector('#mode');
  const cards = [...document.querySelectorAll('.card')];
  function filter() {
    let count = 0;
    const query = search.value.trim().toLocaleLowerCase();
    for (const card of cards) {
      const show = (mode.value === 'all' || card.dataset.picked === 'true') &&
        (category.value === 'all' || card.dataset.category === category.value) &&
        card.textContent.toLocaleLowerCase().includes(query);
      card.hidden = !show;
      if (show) count++;
    }
    document.querySelector('#count').textContent = `${count} 件を表示`;
    document.querySelector('#empty').hidden = count !== 0;
  }
  [search, category, mode].forEach(el => el.addEventListener('input', filter));
  filter();
}
'''

CSS += """
.day-tabs{display:flex;gap:8px;overflow-x:auto;padding:8px 0 16px}.day-tabs a{flex:0 0 auto;text-decoration:none;color:var(--ink);border:1px solid var(--line);background:#fff;border-radius:8px;padding:10px 14px;font-size:13px}.day-tabs a span{display:block;font-size:11px;color:var(--muted)}.day-tabs a[aria-current=page]{background:var(--accent);color:#fff;border-color:var(--accent)}.day-tabs a[aria-current=page] span{color:#fff}.day-tabs a:focus-visible{outline:3px solid var(--accent);outline-offset:3px}
"""
