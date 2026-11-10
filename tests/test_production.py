"""Regression checks for the localhost metadata seen on the deployed website."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from build import build
import preview
from check_site import Page, check

PUBLIC_URL = 'https://rent-split-resources.github.io'


class ProductionTests(unittest.TestCase):
    def test_cli_defaults_to_live_address(self):
        with TemporaryDirectory() as temporary:
            output = Path(temporary) / 'site'
            subprocess.run([sys.executable, str(PROJECT / 'build.py'), '--output', str(output)], check=True, capture_output=True, text=True)
            with redirect_stdout(StringIO()):
                check(PUBLIC_URL, output)

    def test_preview_preserves_every_production_file(self):
        with TemporaryDirectory() as temporary, redirect_stdout(StringIO()):
            project = Path(temporary)
            production = project / '_site'
            build(PUBLIC_URL, output=production)
            before = {file.relative_to(production): file.read_bytes() for file in production.rglob('*') if file.is_file()}
            with patch.object(preview, 'PROJECT', project):
                local = preview.build_preview(8123)
            after = {file.relative_to(production): file.read_bytes() for file in production.rglob('*') if file.is_file()}
            self.assertEqual(before, after)
            self.assertEqual(Page((local / 'index.html').read_text(encoding='utf-8')).canonicals, ['http://localhost:8123/'])
            check(PUBLIC_URL, production)

    def test_production_checker_rejects_a_local_preview(self):
        with TemporaryDirectory() as temporary, redirect_stdout(StringIO()):
            output = Path(temporary)
            build('http://localhost:8000', output=output)
            with self.assertRaisesRegex(AssertionError, 'Localhost URL'):
                check('http://localhost:8000', output)

    def test_checker_rejects_localhost_even_with_a_correct_canonical(self):
        with TemporaryDirectory() as temporary, redirect_stdout(StringIO()):
            output = Path(temporary)
            build(PUBLIC_URL, output=output)
            homepage = output / 'index.html'
            original = homepage.read_text(encoding='utf-8')
            mutations = {
                'Open Graph': original.replace(f'property="og:url" content="{PUBLIC_URL}/"', 'property="og:url" content="http://localhost:8000/"'),
                'structured data': original.replace(f'"url": "{PUBLIC_URL}/"', '"url": "http://localhost:8000/"'),
                'link': original.replace('href="/resources/"', 'href="http://localhost:8000/resources/"'),
            }
            for label, source in mutations.items():
                with self.subTest(label=label):
                    self.assertNotEqual(original, source)
                    homepage.write_text(source, encoding='utf-8')
                    with self.assertRaisesRegex(AssertionError, 'Localhost URL|Open Graph URL'):
                        check(PUBLIC_URL, output)


if __name__ == '__main__':
    unittest.main()
