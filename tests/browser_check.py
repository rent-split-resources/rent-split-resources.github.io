"""Optional local browser checks. Requires Python Playwright and Chromium.
Start `python preview.py` in another terminal, then run this script.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJECT = Path(__file__).resolve().parents[1]
ARTIFACTS = PROJECT / '.preview'
ARTIFACTS.mkdir(exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1)
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto('http://localhost:8000/', wait_until='networkidle')
    assert page.locator('h1').inner_text() == 'A fair split.\nA better home.'
    page.screenshot(path=str(ARTIFACTS / 'homepage-desktop.png'), full_page=True)
    assert page.locator('#rent-form input, #rent-form select').count() == 2
    page.get_by_role('button', name='Split rent', exact=True).click()
    assert '$800' in page.locator('#calc-results').inner_text()
    page.locator('#people').select_option('4')
    assert page.locator('.result-stale').is_visible()
    page.get_by_role('button', name='Split rent', exact=True).click()
    assert '$600' in page.locator('#calc-results').inner_text()
    assert page.locator('.result-stale').count() == 0
    page.locator('#people').select_option('3')
    page.locator('#rent').fill('1000')
    page.get_by_role('button', name='Split rent', exact=True).click()
    result = page.locator('#calc-results').inner_text()
    assert '$333.34' in result and '$333.33' in result and '$1,000.00' in result
    assert '1 roommate pays $333.34; 2 pay $333.33' in result
    page.locator('#rent').fill('-5')
    assert not page.locator('#rent').evaluate('(input) => input.checkValidity()')
    page.locator('#rent').fill('')
    assert not page.locator('#rent').evaluate('(input) => input.checkValidity()')
    page.locator('#rent').fill('0')
    page.get_by_role('button', name='Split rent', exact=True).click()
    assert '$0.00' in page.locator('#calc-results').inner_text()

    page.goto('http://localhost:8000/resources/', wait_until='networkidle')
    assert page.locator('[data-resource]:visible').count() == 23
    page.get_by_role('button', name='Profiles', exact=True).click()
    assert page.locator('[data-resource]:visible').count() == 6
    page.locator('#resource-search').fill('goodreads')
    assert page.locator('[data-resource]:visible').count() == 1
    page.locator('#resource-search').fill('no-matching-article-1234')
    assert page.locator('#no-resources').is_visible()
    page.goto('http://localhost:8000/resources/#bill-resources', wait_until='networkidle')
    assert page.locator('[data-resource]:visible').count() == 7

    for width in [320, 390, 768, 1440]:
        page.set_viewport_size({'width': width, 'height': 900})
        page.goto('http://localhost:8000/', wait_until='networkidle')
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), f'Homepage overflow at {width}px'
        if width == 390:
            page.screenshot(path=str(ARTIFACTS / 'homepage-mobile.png'), full_page=True)
        page.get_by_role('button', name='Split rent', exact=True).click()
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), f'Calculator overflow at {width}px'

    page.set_viewport_size({'width': 390, 'height': 900})
    for path in ['guides/', 'guides/how-to-split-rent-fairly/', 'guides/split-rent-by-room-size/', 'guides/couples-and-shared-rooms/', 'guides/split-utilities-and-shared-bills/', 'guides/split-restaurant-bill-tax-tip/', 'guides/divide-a-rent-increase/', 'resources/', 'about/', '404.html']:
        page.goto('http://localhost:8000/' + path, wait_until='networkidle')
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), f'Mobile overflow: {path}'

    # Large supported amounts must fit the simplified result card too.
    page.goto('http://localhost:8000/', wait_until='networkidle')
    page.locator('#rent').fill('10000000')
    page.locator('#people').select_option('2')
    page.get_by_role('button', name='Split rent', exact=True).click()
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Large equal result overflows'

    no_js = browser.new_context(java_script_enabled=False)
    static = no_js.new_page()
    static.goto('http://localhost:8000/resources/')
    assert static.locator('[data-resource]:visible').count() == 23
    assert not static.locator('#resource-controls').is_visible()
    static.goto('http://localhost:8000/guides/how-to-split-rent-fairly/')
    assert static.locator('article h2').count() >= 6
    assert not errors, f'Browser JavaScript errors: {errors}'
    no_js.close()
    browser.close()
    print('PASS: two-field calculator, equal splits, rounding, validation, desktop/mobile layouts, resource filters, no-JavaScript content, and browser console.')
