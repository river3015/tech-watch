import hashlib
import html
import json
import os
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

JST = ZoneInfo('Asia/Tokyo')
MAX_BYTES = 5 * 1024 * 1024


def text(value):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', ' ', value or ''))).strip()


def canonical_url(url):
    p = urllib.parse.urlsplit(url.strip())
    if p.scheme not in ('https', 'http') or not p.hostname or p.username or p.password:
        raise ValueError('invalid article URL')
    query = [(k, v) for k, v in urllib.parse.parse_qsl(p.query, keep_blank_values=True)
             if not k.lower().startswith('utm_') and k.lower() not in ('fbclid', 'gclid')]
    return urllib.parse.urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path or '/',
                                   urllib.parse.urlencode(query), ''))


def parse_date(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.strip().replace('Z', '+00:00'))
    except ValueError:
        try:
            dt = parsedate_to_datetime(value)
        except (ValueError, TypeError, OverflowError):
            return None
    return (dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)).isoformat()


def matches_keywords(value, words):
    for word in words:
        if word.isascii() and word.isalnum():
            if re.search(r'(?<![a-zA-Z0-9])' + re.escape(word) + r'(?![a-zA-Z0-9])', value, re.IGNORECASE):
                return True
        elif word.casefold() in value.casefold():
            return True
    return not words


def parse_feed(payload):
    if b'<!DOCTYPE' in payload.upper() or b'<!ENTITY' in payload.upper():
        raise ValueError('DTD is not supported')
    root = ET.fromstring(payload)
    local = lambda tag: tag.rsplit('}', 1)[-1]
    if local(root.tag) not in ('rss', 'RDF', 'feed'):
        raise ValueError('not an RSS/Atom feed')
    result = []
    for node in root.iter():
        if local(node.tag) not in ('item', 'entry'):
            continue
        values = {}
        link = ''
        for child in node:
            name = local(child.tag)
            value = ''.join(child.itertext()).strip()
            values.setdefault(name, value)
            if name == 'link':
                if child.get('href') and child.get('rel', 'alternate') == 'alternate':
                    link = child.get('href')
                elif not child.get('href') and value:
                    link = value
        try:
            url = canonical_url(link)
        except ValueError:
            continue
        title = text(values.get('title'))
        if not title:
            continue
        result.append({'id': hashlib.sha256(url.encode()).hexdigest(), 'url': url,
                       'title': title, 'summary': text(values.get('description') or values.get('summary'))[:240],
                       'published_at': parse_date(values.get('pubDate') or values.get('published') or values.get('date') or values.get('updated'))})
    return result


def fetch(url):
    if urllib.parse.urlsplit(url).scheme != 'https':
        raise ValueError('feed URL must use HTTPS')
    request = urllib.request.Request(url, headers={'User-Agent': 'tech-watch/0.1 (personal RSS reader)', 'Accept': 'application/rss+xml, application/atom+xml, application/xml, text/xml'})
    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = response.read(MAX_BYTES + 1)
            if len(payload) > MAX_BYTES:
                raise ValueError('feed too large')
            return payload
        except (OSError, ValueError):
            if attempt:
                raise
            time.sleep(1)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temporary, path)


def collect(config_path, data_dir, now=None, fetcher=fetch):
    now = now or datetime.now(JST)
    config = json.loads(Path(config_path).read_text(encoding='utf-8'))
    data_dir = Path(data_dir)
    day_dir = data_dir / now.astimezone(JST).strftime('%Y/%m/%d')
    seen = {}
    for path in sorted(data_dir.glob('*/*/*/articles.json')):
        for article in json.loads(path.read_text(encoding='utf-8')):
            seen[article['id']] = (path, article)
    day_path = day_dir / 'articles.json'
    articles = json.loads(day_path.read_text(encoding='utf-8')) if day_path.exists() else []
    # Use the same objects for current-day attribution merges.
    for article in articles:
        seen[article['id']] = (day_path, article)
    changed = set()
    statuses = []
    successes = 0
    for source in config['sources']:
        if not source.get('enabled', True):
            continue
        status = {'source_id': source['id'], 'name': source['name'], 'new': 0}
        try:
            entries = parse_feed(fetcher(source['url']))
            successes += 1
            status.update(status='ok', fetched=len(entries))
            for article in entries[:config.get('max_items_per_source', 30)]:
                if article['published_at']:
                    published = datetime.fromisoformat(article['published_at'])
                    if published < now - timedelta(days=config.get('lookback_days', 7)) or published > now + timedelta(days=1):
                        continue
                words = source.get('keywords', [])
                if not matches_keywords(article['title'] + ' ' + article['summary'], words):
                    continue
                attribution = {'id': source['id'], 'name': source['name'], 'category': source['category']}
                if article['id'] in seen:
                    path, previous = seen[article['id']]
                    if not any(s['id'] == source['id'] for s in previous['sources']):
                        previous['sources'].append(attribution)
                        changed.add(path)
                    continue
                article.update(collected_at=now.isoformat(), sources=[attribution])
                articles.append(article)
                seen[article['id']] = (day_path, article)
                status['new'] += 1
        except Exception as error:
            # Do not persist remote error bodies or credentials.
            status.update(status='error', error=type(error).__name__)
        statuses.append(status)
    write_json(day_path, articles)
    for path in changed - {day_path}:
        existing = json.loads(path.read_text(encoding='utf-8'))
        write_json(path, [seen[a['id']][1] for a in existing])
    report = {'collected_at': now.isoformat(), 'sources': statuses, 'successes': successes,
              'failures': sum(s['status'] == 'error' for s in statuses)}
    write_json(day_dir / 'collection.json', report)
    return report
