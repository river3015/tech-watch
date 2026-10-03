import json
import tempfile
import unittest
from pathlib import Path
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
            self.assertEqual(build(root/'data', root/'public'), 0)
            day = root/'data/2026/10/03'
            day.mkdir(parents=True)
            (day/'articles.json').write_text(json.dumps([article(1)]))
            (day/'collection.json').write_text(json.dumps({'collected_at':'2026-10-03T12:00:00+09:00','sources':[{'status':'error','name':'bad','error':'URLError'}], 'successes':0, 'failures':1}))
            self.assertEqual(build(root/'data', root/'public'), 1)
            page = (root/'public/index.html').read_text()
            self.assertNotIn('<script>alert', page)
            self.assertNotIn('<img src', page)
            self.assertIn('2026-10-03.html', page)
            self.assertIn('URLError', page)
            self.assertTrue((day/'digest.md').exists())
            self.assertEqual(page, (root/'public/2026-10-03.html').read_text())

if __name__ == '__main__':
    unittest.main()
