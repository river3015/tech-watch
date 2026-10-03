import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from tech_watch.collector import JST, canonical_url, collect, parse_feed, matches_keywords

RSS = b'''<rss><channel><item><title>AI &amp; tools</title><link>https://example.com/a?utm_source=x</link><description>&lt;b&gt;hello&lt;/b&gt;</description><pubDate>Sat, 03 Oct 2026 10:00:00 +0900</pubDate></item></channel></rss>'''

class CollectorTests(unittest.TestCase):
    def test_keywords_do_not_match_inside_english_words(self):
        self.assertFalse(matches_keywords('doit devenir demain', ['IT', 'AI']))
        self.assertTrue(matches_keywords('AIを使った個人開発', ['AI']))
        self.assertTrue(matches_keywords('働き方の話', ['働き方']))

    def test_formats_and_unsafe_links(self):
        self.assertEqual(parse_feed(RSS)[0]['summary'], 'hello')
        atom = b'''<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>release</title><link href="https://example.com/v1"/><updated>2026-10-03T01:00:00Z</updated></entry><entry><title>bad</title><link href="javascript:alert(1)"/></entry></feed>'''
        self.assertEqual(len(parse_feed(atom)), 1)
        rdf = b'''<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/"><item><title>one</title><link>https://example.com/a</link></item></rdf:RDF>'''
        self.assertEqual(len(parse_feed(rdf)), 1)
        with self.assertRaises(ValueError):
            parse_feed(b'<html/>')
        with self.assertRaises(ValueError):
            parse_feed(b'<!DOCTYPE rss><rss/>')

    def test_podcast_links_fall_back_to_guid_and_enclosure(self):
        feed = b'''<rss><channel>
<item><title>no link</title><guid isPermaLink="false">abc</guid><enclosure url="https://cdn.test/ep1.mp3?rss_browser=x" type="audio/mpeg"/></item>
<item><title>guid</title><guid>https://show.test/ep2</guid><enclosure url="https://cdn.test/ep2.mp3"/></item>
<item><title>page</title><link>https://show.test/ep3</link><enclosure url="https://cdn.test/ep3.mp3"/></item>
</channel></rss>'''
        self.assertEqual([a['url'] for a in parse_feed(feed)],
                         ['https://cdn.test/ep1.mp3', 'https://show.test/ep2', 'https://show.test/ep3'])
        self.assertEqual([a['url'] for a in parse_feed(feed, prefer_enclosure=True)],
                         ['https://cdn.test/ep1.mp3', 'https://cdn.test/ep2.mp3', 'https://cdn.test/ep3.mp3'])

    def test_tracking_normalization(self):
        self.assertEqual(canonical_url('https://example.com/a?utm_source=x&id=2#part'), 'https://example.com/a?id=2')

    def test_reruns_cross_day_merge_and_partial_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = [{'id': 'one', 'name': 'One', 'url': 'https://one.test', 'category': 'community'}]
            config = root / 'sources.json'
            config.write_text(json.dumps({'sources': sources}))
            now = datetime(2026, 10, 3, 12, tzinfo=JST)
            collect(config, root / 'data', now, lambda _: RSS)
            collect(config, root / 'data', now, lambda _: RSS)
            path = root / 'data/2026/10/03/articles.json'
            self.assertEqual(len(json.loads(path.read_text())), 1)
            sources.append({'id': 'two', 'name': 'Two', 'url': 'https://two.test', 'category': 'official'})
            sources.append({'id': 'bad', 'name': 'Bad', 'url': 'https://bad.test', 'category': 'news'})
            config.write_text(json.dumps({'sources': sources}))
            def fetcher(url):
                if 'bad' in url:
                    raise OSError('secret remote body')
                return RSS
            report = collect(config, root / 'data', datetime(2026, 10, 4, 12, tzinfo=JST), fetcher)
            self.assertEqual(report['failures'], 1)
            self.assertEqual(len(json.loads(path.read_text())[0]['sources']), 2)
            self.assertEqual(json.loads((root / 'data/2026/10/04/articles.json').read_text()), [])
            self.assertNotIn('secret', json.dumps(report))

    def test_age_and_keywords(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / 'sources.json'
            config.write_text(json.dumps({'sources': [{'id':'s', 'name':'s', 'url':'https://s.test', 'category':'community', 'keywords':['cloud']}]}))
            collect(config, root / 'data', datetime(2026,10,3,12,tzinfo=JST), lambda _: RSS)
            self.assertEqual(json.loads((root / 'data/2026/10/03/articles.json').read_text()), [])

if __name__ == '__main__':
    unittest.main()
