import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime
from tech_watch.collector import JST
from tech_watch.site import build, curate


def article(i, source='one', cat='community'):
    return {'id':str(i), 'title':'<script>alert(1)</script>', 'url':f'https://example.com/{i}', 'summary':'<img src=x onerror=alert(1)>', 'published_at':None, 'collected_at':'2026-10-03T12:00:00+09:00', 'sources':[{'id':source, 'name':source, 'category':cat}]}

class SiteTests(unittest.TestCase):
    def test_balanced_selection(self):
        rows = [article(i) for i in range(10)] + [article(11, 'two')] + [article(12, 'official', 'official')]
        picked = curate(rows)
        self.assertEqual(len(picked), 6)
        self.assertIn('two', [a['sources'][0]['id'] for a in picked])
        self.assertIn('official', [a['sources'][0]['id'] for a in picked])

    def test_build_escape_archive_empty_and_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(build(root/'data', root/'public', datetime(2026, 10, 3, 12, tzinfo=JST)), 0)
            day = root/'data/2026/10/03'
            day.mkdir(parents=True)
            (day/'articles.json').write_text(json.dumps([article(1)]))
            (day/'collection.json').write_text(json.dumps({'collected_at':'2026-10-03T12:00:00+09:00','sources':[{'status':'error','name':'bad','error':'URLError'}], 'successes':0, 'failures':1}))
            self.assertEqual(build(root/'data', root/'public', datetime(2026, 10, 3, 12, tzinfo=JST)), 1)
            page = (root/'public/index.html').read_text()
            self.assertNotIn('<script>alert', page)
            self.assertNotIn('<img src', page)
            self.assertIn('2026-10-03.html', page)
            self.assertIn('URLError', page)
            self.assertTrue((day/'digest.md').exists())
            self.assertEqual(page, (root/'public/2026-10-03.html').read_text())

    def test_publication_days_across_collection_archives_and_jst_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first, second, unknown = article(1), article(2), article(3)
            first['title'] = 'Yesterday only'
            first['published_at'] = '2026-10-02T14:59:00Z'
            second['title'] = 'Today only'
            second['published_at'] = '2026-10-02T15:00:00Z'
            unknown['title'] = 'Unknown publication date'
            unknown['collected_at'] = '2026-10-03T12:00:00+09:00'
            for day, rows in [('03', [first, unknown]), ('04', [second])]:
                path = root / 'data/2026/10' / day
                path.mkdir(parents=True)
                (path/'articles.json').write_text(json.dumps(rows))
            self.assertEqual(build(root/'data', root/'public', datetime(2026,10,3,12,tzinfo=JST)), 2)
            today = (root/'public/index.html').read_text()
            yesterday = (root/'public/2026-10-02.html').read_text()
            self.assertIn('Today only', today)
            self.assertIn('Unknown publication date', today)
            self.assertNotIn('Yesterday only', today)
            self.assertIn('Yesterday only', yesterday)
            self.assertNotIn('Today only', yesterday)
            self.assertIn('aria-current=page', today)
            self.assertIn('<option value="all">この日の全記事</option>', today)
            self.assertEqual(today, (root/'public/2026-10-03.html').read_text())
            build(root/'data', root/'public', datetime(2026,10,5,12,tzinfo=JST))
            empty_today = (root/'public/index.html').read_text()
            self.assertIn('<h1>2026-10-05', empty_today)
            self.assertNotIn('Today only', empty_today)
            self.assertIn('2026-10-03.html', empty_today)

if __name__ == '__main__':
    unittest.main()
