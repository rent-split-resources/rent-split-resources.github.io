"""Check crawlable output and deployment URLs without third-party dependencies."""
import argparse
from html.parser import HTMLParser
from ipaddress import ip_address
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from content import RESOURCES


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.links, self.assets, self.ids, self.schemas = [], [], set(), []
        self.canonicals, self.description, self.robots, self.verification = [], '', '', ''
        self.og_urls, self.urls = [], []
        self.h1 = 0
        self.title = ''
        self.in_title = self.in_json = False
        self.json_text = ''
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.urls.extend(a[key] for key in ('href', 'src') if a.get(key))
        if a.get('id'):
            assert a['id'] not in self.ids, f'Duplicate ID: {a["id"]}'
            self.ids.add(a['id'])
        if tag == 'h1':
            self.h1 += 1
        if tag == 'a' and a.get('href'):
            self.links.append(a['href'])
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonicals.append(a.get('href'))
        if tag == 'link' and a.get('rel') in ('stylesheet', 'icon'):
            self.assets.append(a['href'])
        if tag == 'script' and a.get('src'):
            self.assets.append(a['src'])
        if tag == 'meta':
            if a.get('property') == 'og:url': self.og_urls.append(a.get('content', ''))
            if a.get('name') == 'description': self.description = a.get('content', '')
            if a.get('name') == 'robots': self.robots = a.get('content', '')
            if a.get('name') == 'google-site-verification': self.verification = a.get('content', '')
        if tag == 'title': self.in_title = True
        if tag == 'script' and a.get('type') == 'application/ld+json':
            self.in_json, self.json_text = True, ''

    def handle_data(self, data):
        if self.in_title: self.title += data
        if self.in_json: self.json_text += data

    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False
        if tag == 'script' and self.in_json:
            self.schemas.append(json.loads(self.json_text))
            self.in_json = False


def assert_public_urls(value):
    if isinstance(value, dict):
        for item in value.values():
            assert_public_urls(item)
    elif isinstance(value, list):
        for item in value:
            assert_public_urls(item)
    elif isinstance(value, str) and value.startswith(('http://', 'https://', '//')):
        hostname = (urlsplit(value).hostname or '').rstrip('.').lower()
        assert hostname != 'localhost' and not hostname.endswith('.localhost'), f'Localhost URL in production: {value}'
        try:
            address = ip_address(hostname)
        except ValueError:
            return
        assert not address.is_loopback and not address.is_unspecified, f'Localhost URL in production: {value}'


def check(site_url, directory, verification=''):
    site_url = site_url.rstrip('/')
    assert_public_urls(site_url)
    base_parts = urlsplit(site_url)
    base_path = base_parts.path.rstrip('/') + '/'
    files = sorted(directory.rglob('*.html'))
    pages = {file.relative_to(directory).as_posix(): Page(file.read_text(encoding='utf-8')) for file in files}
    titles, descriptions = set(), set()
    expected_urls = set()
    for filename, page in pages.items():
        assert page.h1 == 1, f'{filename}: expected one H1'
        assert page.title and page.title not in titles, f'{filename}: missing or duplicate title'
        assert page.description and page.description not in descriptions, f'{filename}: missing or duplicate description'
        titles.add(page.title)
        descriptions.add(page.description)
        assert page.schemas, f'{filename}: missing structured data'
        assert page.verification == verification, f'{filename}: verification mismatch'
        page_path = filename.removesuffix('index.html') if filename != '404.html' else filename
        current_url = site_url + '/' + page_path
        assert page.og_urls == [current_url], f'{filename}: wrong Open Graph URL {page.og_urls}'
        assert_public_urls(page.urls + page.og_urls + page.schemas)
        for data in page.schemas:
            for node in data.get('@graph', [data]):
                if node.get('@type') == 'WebSite':
                    assert node.get('url') == site_url + '/', f'{filename}: wrong WebSite URL'
                    assert node.get('@id') == site_url + '/#website', f'{filename}: wrong WebSite ID'
                elif node.get('@type') in ('Article', 'CollectionPage', 'AboutPage'):
                    assert node.get('url') == current_url, f'{filename}: wrong structured-data page URL'
        if filename == '404.html':
            assert 'noindex' in page.robots and not page.canonicals, '404 must not be indexable'
        else:
            assert 'noindex' not in page.robots
            assert page.canonicals == [current_url], f'{filename}: wrong canonical {page.canonicals}'
            expected_urls.add(current_url)
        for href in page.links + page.assets:
            target = urlsplit(urljoin(current_url, href))
            if target.scheme not in ('http', 'https') or target.netloc != base_parts.netloc:
                continue
            assert target.path.startswith(base_path), f'{filename}: link escapes repository path: {href}'
            relative = unquote(target.path[len(base_path):])
            disk_path = directory / relative
            if disk_path.is_dir(): disk_path /= 'index.html'
            assert disk_path.is_file(), f'{filename}: broken internal link: {href}'
            if target.fragment and disk_path.suffix == '.html':
                target_page = pages[disk_path.relative_to(directory).as_posix()]
                assert unquote(target.fragment) in target_page.ids, f'{filename}: missing fragment: {href}'
    ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    sitemap = ET.parse(directory / 'sitemap.xml')
    locations = [node.text for node in sitemap.findall('s:url/s:loc', ns)]
    assert len(locations) == len(set(locations)), 'Duplicate sitemap locations'
    assert set(locations) == expected_urls, 'Sitemap must contain every indexable page and no external URL'
    assert len(expected_urls) == 10, f'Expected ten indexable pages, found {len(expected_urls)}'
    robots = (directory / 'robots.txt').read_text(encoding='utf-8')
    assert f'Sitemap: {site_url}/sitemap.xml' in robots and 'Disallow:' not in robots
    supplied = {r[3] for r in RESOURCES}
    assert len(supplied) == 23, 'Expected all 23 supplied references'
    assert supplied <= set(pages['resources/index.html'].links), 'A supplied reference is missing from static HTML'
    assert (directory / '.nojekyll').exists()
    print(f'PASS: {len(expected_urls)} indexable pages, 404, canonical and Open Graph URLs, JSON-LD, internal links, all 23 references, sitemap, verification tag, and no localhost URLs.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-url', required=True)
    parser.add_argument('--directory', type=Path, default=PROJECT / '_site')
    parser.add_argument('--verification', default='')
    args = parser.parse_args()
    check(args.site_url, args.directory.resolve(), args.verification)
