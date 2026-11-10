"""Build production pages for RentSplit Guide; use preview.py for local previews."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import shutil
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

from content import GUIDES, RESOURCES

PROJECT = Path(__file__).resolve().parent
SITE_NAME = "RentSplit Guide"
PRODUCTION_URL = "https://rent-split-resources.github.io"
SITE_URL = ""
BASE = "/"
OUT = PROJECT / "_site"

ICONS = {
    "home": '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1Z"/>',
    "floorplan": '<rect x="3" y="3" width="18" height="18" rx="1"/><path d="M13 3v9h8M3 12h5m0 0v9m0-9h5"/>',
    "people": '<circle cx="9" cy="8" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3m1-16a3 3 0 0 1 0 6m3 10v-3a6 6 0 0 0-3-5"/>',
    "bolt": '<path d="m14 2-10 12h7l-1 8 10-12h-7Z"/>',
    "receipt": '<path d="M5 3 8 5l4-2 4 2 3-2v18l-3-2-4 2-4-2-3 2Zm4 5h6m-6 4h6m-6 4h3"/>',
    "trend": '<path d="M3 17 9 11l4 4 8-10m-6 0h6v6M3 21h18"/>',
    "book": '<path d="M12 5v16M3 3c4 0 7 1 9 3 2-2 5-3 9-3v15c-4 0-7 1-9 3-2-2-5-3-9-3Z"/>',
    "arrow": '<path d="M5 12h14m-6-6 6 6-6 6"/>',
    "external": '<path d="M14 3h7v7m0-7L10 14M9 3H4a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h16a1 1 0 0 0 1-1v-5"/>',
    "check": '<path d="m5 12 4 4L19 6"/>',
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def icon(name: str, cls: str = "") -> str:
    return f'<svg class="icon {esc(cls)}" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'


def link(path: str = "") -> str:
    return BASE + path.lstrip("/")


def url(path: str = "") -> str:
    return SITE_URL + "/" + path.lstrip("/")


def rich(content: str) -> str:
    return content.replace("{{ROOT}}", BASE)


def schema(data: dict) -> str:
    # Escape '<' to prevent any future content field from closing a script tag.
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace("<", "\\u003c") + "</script>"


def guide_card(g: dict, index: int) -> str:
    return f'''<a class="guide-card{' featured' if index == 0 else ''}" href="{link('guides/' + g['slug'] + '/')}">
        <div class="card-top"><span class="icon-box">{icon(g['icon'])}</span><span class="card-number">0{index + 1}</span></div>
        <span class="eyebrow">{g['category']}</span><h3>{g['short_title']}</h3><p>{esc(g['description'])}</p>
        <div class="card-bottom"><span>{g['minutes']} min read</span><span class="circle-arrow">{icon('arrow')}</span></div></a>'''


def layout(title: str, description: str, body: str, path: str = "", section: str = "", extra_schema: dict | None = None, noindex: bool = False, verification: str = "") -> str:
    canonical = "" if noindex else f'<link rel="canonical" href="{esc(url(path))}">'
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large"
    verify_tag = f'<meta name="google-site-verification" content="{esc(verification)}">' if verification else ""
    website = {"@context": "https://schema.org", "@type": "WebSite", "@id": url() + "#website", "name": SITE_NAME, "url": url(), "inLanguage": "en"}
    def active(name: str) -> str:
        return ' aria-current="page"' if name == section else ""
    guide_nav = link() + "#guides" if not path else link("guides/")
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta name="robots" content="{robots}">{canonical}{verify_tag}
<meta name="theme-color" content="#f8f9f5"><meta property="og:type" content="{'article' if section == 'article' else 'website'}"><meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{esc(url(path))}">
<meta name="twitter:card" content="summary"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(description)}">
<link rel="icon" href="{link('assets/favicon.svg')}" type="image/svg+xml"><link rel="stylesheet" href="{link('assets/style.css')}">
<script src="{link('assets/app.js')}" defer></script>{schema(extra_schema or website)}
</head><body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="container header-inner"><a class="brand" href="{link()}" aria-label="RentSplit Guide home"><span class="brand-mark">{icon('home')}</span><span>RentSplit<span class="brand-light"> Guide</span><span class="brand-dot">.</span></span></a>
<nav aria-label="Main navigation"><a href="{guide_nav}"{active('guides')}>The guides</a><a href="{link('resources/')}"{active('resources')}>Resources</a><a href="{link('about/')}"{active('about')}>About</a></nav>
<a class="button header-cta" href="{link()}#calculator">Let’s split rent {icon('arrow')}</a></div></header>
<main id="main">{body}</main>
<footer class="site-footer"><div class="container"><div class="footer-top"><div><a class="brand" href="{link()}"><span class="brand-mark">{icon('home')}</span><span>RentSplit<span class="brand-light"> Guide</span><span class="brand-dot">.</span></span></a><p>A little clarity for life together.</p></div>
<div class="footer-links"><a href="{link('guides/')}">All guides</a><a href="{link('resources/')}">Resource library</a><a href="{link('about/')}">About &amp; privacy</a><a href="{link('sitemap.xml')}">Sitemap</a></div></div>
<div class="footer-bottom"><span>Free to use. Made for shared living.</span><span>Educational examples. Your household agreement comes first.</span></div></div></footer>
</body></html>'''


def calculator() -> str:
    options = ''.join(f'<option value="{n}"{" selected" if n == 3 else ""}>{n} roommates</option>' for n in range(2, 9))
    return f'''<section class="calculator simple-calculator" id="calculator" aria-labelledby="calc-title"><div class="calc-heading"><span class="eyebrow"><span class="status-dot"></span> RENT SPLIT CALCULATOR</span><span class="tiny-pill">FREE TOOL</span></div>
<h2 id="calc-title">Split the rent. Simply.</h2><p class="calc-subtitle">Enter the rent and how many people are sharing.</p>
<form id="rent-form"><div class="input-grid"><div class="form-field"><label for="rent">Monthly rent ($)</label><input id="rent" name="rent" type="number" min="0" max="10000000" step="0.01" value="2400" required inputmode="decimal"></div><div class="form-field"><label for="people">Roommates</label><select id="people" name="people">{options}</select></div></div>
<button class="button calc-submit" type="submit">Split rent {icon('arrow')}</button><p id="calc-error" class="form-error" role="alert" hidden></p></form>
<div id="calc-results" class="calc-results" aria-live="polite" aria-atomic="true"><div class="result-eyebrow">PER PERSON</div><div class="result-amount">$800<span>.00 <small>/ month</small></span></div><p class="result-detail">$2,400.00 ÷ 3 roommates</p></div>
<p class="calc-note">{icon('check')} Your numbers stay in your browser. No sign-up.</p><noscript><p class="noscript-note">For an equal rent split, divide the monthly rent by the number of roommates. The example above is $2,400 ÷ 3 = $800 each. Enable JavaScript to calculate your own amount.</p></noscript></section>'''


def homepage() -> str:
    cards = ''.join(guide_card(g, i) for i, g in enumerate(GUIDES))
    return f'''<div class="container"><section class="hero"><div class="hero-copy"><span class="eyebrow hero-eyebrow"><span class="small-line"></span> A LITTLE MATH. A LOT MORE HARMONY.</span>
<h1>A fair split.<br>A <span class="highlight">better home.</span></h1><p class="hero-description">Take the awkward out of shared expenses. Practical guides and simple calculations for rent, roommates, and everything in between.</p>
<div class="hero-actions"><a class="button button-dark" href="#guides">Find your starting point {icon('arrow')}</a><a class="text-link" href="{link('resources/')}">Browse resources {icon('external')}</a></div>
<div class="hero-note"><div class="little-home" aria-hidden="true">{icon('home')}<span>÷</span></div><p>Good living starts with a good agreement.<br><strong>We’ll help you work out the numbers.</strong></p></div>
<div class="hero-stats"><div><strong>06</strong><span>practical guides</span></div><div><strong>{len(RESOURCES)}</strong><span>resource links</span></div><div><strong>Zero</strong><span>sign-ups needed</span></div></div></div>{calculator()}</section></div>
<div class="topic-strip"><div class="container"><span>SHARED LIVING, SIMPLIFIED</span><span>{icon('home')} Rent &amp; roommates</span><span>{icon('floorplan')} Unequal rooms</span><span>{icon('bolt')} Household bills</span><span>{icon('receipt')} Dinner &amp; tip</span></div></div>
<section class="section container" id="guides"><div class="section-heading"><div><span class="eyebrow">THE KNOW-HOW</span><h2>A guide for your kind of shared life.</h2></div><p>No complicated jargon. Just clear methods,<br class="desktop-break"> real examples, and a place to start.</p></div><div class="guide-grid">{cards}</div></section>
<section class="method-section"><div class="container method-layout"><div><span class="eyebrow">FAIR IS SOMETHING YOU AGREE ON</span><h2>Better conversations.<br>Fewer surprises.</h2><p>A calculator gives you a number.<br>A shared plan makes it work.</p><a class="text-link" href="{link('guides/how-to-split-rent-fairly/')}">Build your roommate agreement {icon('arrow')}</a></div><ol class="steps"><li><span>01</span><div><h3>Put everything on the table.</h3><p>List the rent, bills, room differences, and who’s sharing.</p></div></li><li><span>02</span><div><h3>Pick a method together.</h3><p>Equal shares, room size, or another arrangement you all accept.</p></div></li><li><span>03</span><div><h3>Write it down. Check in.</h3><p>Agree on amounts and dates, then revisit when life changes.</p></div></li></ol></div></section>
<section class="section container"><div class="library-banner"><div class="library-art" aria-hidden="true"><span>{icon('book')}</span><div class="art-dots">···</div></div><div class="library-copy"><span class="eyebrow">KEEP EXPLORING</span><h2>A useful next read, all in one place.</h2><p>17 reading links and 6 profiles covering rent calculations, shared bills, and making the numbers add up.</p></div><a class="button button-dark" href="{link('resources/')}">Open the library {icon('arrow')}</a></div></section>
<section class="container faq-section"><div><span class="eyebrow">A FEW COMMON QUESTIONS</span><h2>Let’s clear things up.</h2></div><div class="faq-list"><details><summary>What is the fairest way to split rent?</summary><p>There is no universal formula. Equal shares can suit similar rooms; a shared-space and room-size method can account for different bedrooms. Choose a method everyone understands and agrees to. <a href="{link('guides/how-to-split-rent-fairly/')}">Compare the options.</a></p></details><details><summary>How should we split utilities?</summary><p>Divide agreed shared bills separately from rent. For equal shares, usage-based bills, and partial months, use the <a href="{link('guides/split-utilities-and-shared-bills/')}">utilities guide</a>.</p></details><details><summary>What if two people share one bedroom?</summary><p>Allocate private costs once per room and shared costs per person. Our <a href="{link('guides/couples-and-shared-rooms/')}">couples and shared bedrooms guide</a> walks through an example. The simple calculator divides rent equally by person.</p></details><details><summary>Do you save my numbers?</summary><p>No. Calculations run in your browser. This site uses no analytics, accounts, or tracking cookies. Your hosting provider still handles ordinary page requests. <a href="{link('about/')}">Read about the site.</a></p></details></div></section>'''


def breadcrumb(label: str, parent: str | None = None) -> str:
    middle = f'<li><a href="{link("guides/")}">Guides</a></li>' if parent else ""
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb"><ol><li><a href="{link()}">Home</a></li>{middle}<li aria-current="page">{esc(label)}</li></ol></nav>'


def breadcrumbs_schema(label: str, path: str, is_guide: bool = False) -> dict:
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": url()}]
    if is_guide:
        items.append({"@type": "ListItem", "position": 2, "name": "Guides", "item": url("guides/")})
    items.append({"@type": "ListItem", "position": len(items) + 1, "name": label, "item": url(path)})
    return {"@type": "BreadcrumbList", "itemListElement": items}


def article(g: dict) -> tuple[str, dict]:
    toc = ''.join(f'<a href="#{sid}">{esc(title.split(". ", 1)[-1])}</a>' for sid, title, _ in g["sections"])
    sections = ''.join(f'<section id="{sid}"><h2>{title}</h2>{rich(content)}</section>' for sid, title, content in g["sections"])
    faqs = ''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in g["faq"])
    related = ''.join(guide_card(next(x for x in GUIDES if x['slug'] == slug), i + 1) for i, slug in enumerate(g['related']))
    body = f'''<div class="container">{breadcrumb(g['title'], 'guides')}<header class="article-header"><span class="eyebrow">{g['category']} <span class="meta-dot">·</span> {g['minutes']} MIN READ</span><h1>{g['title']}</h1><p>{g['intro']}</p><div class="article-byline">A practical guide from RentSplit Guide <span>·</span> Worked examples included</div></header>
<div class="article-layout"><aside class="article-toc"><span class="eyebrow">IN THIS GUIDE</span><nav aria-label="Table of contents">{toc}<a href="#questions">Common questions</a></nav><a class="toc-calculator" href="{link()}#calculator">Try the rent calculator {icon('arrow')}</a></aside><article class="article-body"><div class="takeaway"><span class="eyebrow">THE STARTING POINT</span><p>{g['takeaway']}</p></div>{sections}<section id="questions"><h2>Common questions</h2><div class="faq-list">{faqs}</div></section><div class="article-end"><p>Keep the conversation going.</p><a class="text-link" href="{link('resources/')}">Explore the external reading library {icon('arrow')}</a></div></article></div>
<section class="section related-section"><div class="section-heading"><div><span class="eyebrow">YOUR NEXT READ</span><h2>Keep making sense of it.</h2></div><a class="text-link" href="{link('guides/')}">All guides {icon('arrow')}</a></div><div class="guide-grid related-grid">{related}</div></section></div>'''
    path = 'guides/' + g['slug'] + '/'
    data = {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "headline": g['title'], "description": g['description'], "mainEntityOfPage": url(path), "url": url(path), "inLanguage": "en", "author": {"@type": "Organization", "name": SITE_NAME, "url": url('about/')}, "publisher": {"@type": "Organization", "name": SITE_NAME, "url": url()}},
        breadcrumbs_schema(g['title'], path, True),
    ]}
    return body, data


def resources_page() -> str:
    groups = [("rent", "rent-resources", "Rent & roommates", "Room prices, rent increases, and sharing a home."), ("bills", "bill-resources", "Shared bills & restaurant splits", "Everyday expenses, tax, tips, and group payments."), ("profiles", "profile-resources", "Profiles & link pages", "Six Rent Split Calculator profiles from across the web."), ("other", "more-resources", "More reading", "An additional reference from the collection.")]
    content = ""
    for category, section_id, title, description in groups:
        items = [(i, r) for i, r in enumerate(RESOURCES) if r[0] == category]
        rows = ''.join(f'''<article class="resource-row" data-resource data-category="{category}"><span class="resource-number">{i+1:02d}</span><div><span class="resource-publisher">{esc(r[2])}</span><h3><a href="{esc(r[3])}">{esc(r[1])} {icon('external')}</a></h3><p>{esc(r[4])}</p></div><span class="external-label">{'PROFILE' if category == 'profiles' else 'EXTERNAL READ'}</span></article>''' for i, r in items)
        content += f'<section class="resource-group" id="{section_id}" data-resource-group><div class="resource-group-heading"><h2>{title} <span>{len(items):02d}</span></h2><p>{description}</p></div>{rows}</section>'
    return f'''<div class="container">{breadcrumb('Resource library')}<header class="page-header"><span class="eyebrow">THE READING ROOM</span><h1>Good resources.<br>All in one place.</h1><p>17 reading links on rent splitting and shared bills, plus 6 Rent Split Calculator profiles. Start with a topic, then find your next useful read.</p></header>
<div class="resource-controls" id="resource-controls" hidden><div class="filter-buttons" aria-label="Filter resources"><button type="button" data-filter="all" aria-pressed="true" class="is-active">All resources <span>{len(RESOURCES)}</span></button><button type="button" data-filter="rent" aria-pressed="false">Rent &amp; roommates</button><button type="button" data-filter="bills" aria-pressed="false">Shared bills</button><button type="button" data-filter="profiles" aria-pressed="false">Profiles</button><button type="button" data-filter="other" aria-pressed="false">More reading</button></div><div class="resource-search"><label class="sr-only" for="resource-search">Search resources by topic or publisher</label><input type="search" id="resource-search" placeholder="Search the library…" autocomplete="off"></div></div>
<p class="resource-count" id="resource-count" role="status">{len(RESOURCES)} resources in the collection</p><div class="resource-library">{content}</div><p id="no-resources" class="empty-state" hidden>No matching resources. Try another topic or clear your search.</p>
<aside class="reading-note"><span class="icon-box">{icon('book')}</span><div><h2>A note on this collection</h2><p>These articles are hosted on other websites. Topic labels reflect the supplied links; the full text and availability have not been independently verified. For step-by-step explanations on this site, start with <a href="{link('guides/')}">our original guides</a>.</p></div></aside></div>'''


def about_page() -> str:
    return f'''<div class="container">{breadcrumb('About')}<header class="page-header"><span class="eyebrow">A LITTLE CLARITY FOR LIFE TOGETHER</span><h1>Make the numbers<br>easier to talk about.</h1><p>RentSplit Guide is a free educational resource for people sharing homes, bills, and the occasional dinner receipt.</p></header><div class="about-layout"><div class="article-body"><section><h2>What you’ll find here</h2><p>Our original guides explain common ways to allocate rent and shared expenses, with formulas, assumptions, and worked examples. The calculator divides monthly rent equally between roommates using just two fields. The resource library collects 17 reading links and 6 Rent Split Calculator profiles on external websites.</p><p>The aim is to help you understand the choices and agree on a method. A mathematical result is a starting point for a conversation; it does not decide what every household should consider fair.</p></section><section><h2>How the examples work</h2><p>The calculator displays dollar amounts with two decimal places. Enter the monthly rent and number of roommates to see an equal share per person.</p><p>When rent cannot divide evenly into cents, a short rounding note shows how to cover the difference. For unequal bedrooms, follow the <a href="{link('guides/split-rent-by-room-size/')}">room-size guide</a> and its worked example.</p></section><section><h2>Your privacy</h2><p>The calculator runs entirely in your browser. This site does not send your calculator inputs to a server, save them in local storage, or use analytics, advertising cookies, or accounts. Your numbers reset when the page reloads.</p><p>GitHub Pages or another hosting provider receives ordinary requests when you visit, including connection information such as an IP address. External websites linked from the resource library have their own privacy practices. A Search Console verification tag, if configured by the site owner, does not add visitor analytics.</p></section><section><h2>Using the guidance</h2><p>This site provides general education, not individualized legal, tax, or financial advice. Your lease, local requirements, and household agreement may affect what you owe. Restaurant taxes and service-charge practices also vary. Verify actual bills and agreements before paying.</p><p>External links are a reading collection, not an endorsement of a publisher or a claim that its content has been reviewed. All internal guides remain available without JavaScript.</p></section></div><aside class="about-card"><span class="icon-box">{icon('home')}</span><h2>One home.<br>A shared plan.</h2><p>Start with the basics, then make the method your own.</p><a class="button button-dark" href="{link('guides/how-to-split-rent-fairly/')}">Read the first guide {icon('arrow')}</a></aside></div></div>'''


def build(site_url: str, verification: str = "", output: Path | None = None) -> None:
    global SITE_URL, BASE, OUT
    parts = urlsplit(site_url)
    if parts.scheme not in ('http', 'https') or not parts.netloc or parts.query or parts.fragment or parts.username or parts.password:
        raise ValueError('Use a complete site URL without credentials, query parameters, or fragments.')
    if any(segment in ('.', '..') for segment in parts.path.split('/')) or '%' in parts.path or '\\' in site_url or any(c.isspace() for c in site_url):
        raise ValueError('Use a plain, normalized site URL, including the repository path when needed.')
    SITE_URL = site_url.rstrip('/')
    BASE = (parts.path.rstrip('/') + '/') or '/'
    OUT = (output or PROJECT / '_site').resolve()
    # Never clear an arbitrary output directory; overwrite only generated files.
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copytree(PROJECT / 'assets', OUT / 'assets', dirs_exist_ok=True)
    pages: list[str] = []

    def write_page(path: str, title: str, description: str, body: str, section: str = '', data: dict | None = None, noindex: bool = False) -> None:
        destination = OUT / (path + 'index.html' if path != '404.html' else path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(layout(title, description, body, path, section, data, noindex, verification), encoding='utf-8')
        if not noindex:
            pages.append(path)

    write_page('', 'Rent Split Calculator & Roommate Guides | RentSplit Guide', 'Divide monthly rent with a simple two-field calculator. Explore six roommate guides and 23 resources on fair rent, shared bills, tax, and tips.', homepage())
    guides_body = f'<div class="container">{breadcrumb("Guides")}<header class="page-header"><span class="eyebrow">THE KNOW-HOW</span><h1>Shared living.<br>Clearly explained.</h1><p>Six practical guides to help you choose a method, understand the calculation, and agree on what comes next.</p></header><div class="guide-grid all-guides">' + ''.join(guide_card(g, i) for i, g in enumerate(GUIDES)) + '</div></div>'
    write_page('guides/', 'Rent Splitting & Shared Expense Guides | RentSplit Guide', 'Explore six original guides on fair rent, room sizes, couples, utilities, restaurant bills, and rent increases, with formulas and worked examples.', guides_body, 'guides', {"@context": "https://schema.org", "@graph": [{"@type": "CollectionPage", "name": "Rent splitting and shared expense guides", "url": url('guides/')}, breadcrumbs_schema('Guides', 'guides/')]})
    for g in GUIDES:
        body, data = article(g)
        write_page('guides/' + g['slug'] + '/', g['title'] + ' | RentSplit Guide', g['description'], body, 'article', data)
    resource_data = {"@context": "https://schema.org", "@graph": [{"@type": "CollectionPage", "name": "Rent and bill splitting resource library", "url": url('resources/'), "mainEntity": {"@type": "ItemList", "numberOfItems": len(RESOURCES), "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": r[1], "url": r[3]} for i, r in enumerate(RESOURCES)]}}, breadcrumbs_schema('Resource library', 'resources/')]}
    write_page('resources/', '23 Rent Splitting Resources & Profiles | RentSplit Guide', 'Browse 17 reading links and 6 profiles covering rent calculators, roommate costs, utilities, restaurant bills, tax, tips, and rent increases.', resources_page(), 'resources', resource_data)
    write_page('about/', 'About & Privacy | RentSplit Guide', 'Learn how RentSplit Guide explains shared expenses, how the calculator handles your numbers, and the assumptions behind its educational examples.', about_page(), 'about', {"@context": "https://schema.org", "@graph": [{"@type": "AboutPage", "name": "About RentSplit Guide", "url": url('about/')}, breadcrumbs_schema('About', 'about/')]})
    write_page('404.html', 'Page not found | RentSplit Guide', 'Find the rent calculator, guides, and resource library from the RentSplit Guide homepage.', f'<div class="container error-page"><span class="eyebrow">404 · A SMALL DETOUR</span><h1>This page has<br>moved out.</h1><p>Let’s get you back to the guides and the numbers.</p><a class="button button-dark" href="{link()}">Back to the homepage {icon("arrow")}</a></div>', noindex=True)
    ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
    root = ET.Element(ns + 'urlset')
    for path in pages:
        ET.SubElement(ET.SubElement(root, ns + 'url'), ns + 'loc').text = url(path)
    ET.indent(root)
    ET.ElementTree(root).write(OUT / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    (OUT / 'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: ' + url('sitemap.xml') + '\n', encoding='utf-8')
    (OUT / '.nojekyll').write_text('', encoding='utf-8')
    print(f'Built {len(pages)} indexable pages + 404 at {OUT}')
    print(f'Canonical base: {SITE_URL}')
    print(f'Sitemap: {url("sitemap.xml")}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-url', default=PRODUCTION_URL, help='Public site URL; defaults to https://rent-split-resources.github.io. Use preview.py for a local preview.')
    parser.add_argument('--verification', default='', help='Google Search Console HTML meta tag content value (optional).')
    parser.add_argument('--output', type=Path, default=PROJECT / '_site')
    args = parser.parse_args()
    build(args.site_url, args.verification, args.output)
