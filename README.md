# RentSplit Guide

A complete static website for GitHub Pages: a simple two-field rent calculator, six original guides, and all **23 supplied references** (17 reading links and 6 profiles).

The site has ten indexable pages plus a custom 404. HTML is generated before deployment, so the guides, navigation, and external links are available without JavaScript. There are no runtime frameworks, external font requests, analytics, accounts, or package dependencies for the build.

## Preview on your computer

Requires Python 3.12 or newer. In this project's folder, run:

```powershell
python preview.py
```

Open **http://localhost:8000**. Stop the server with Ctrl+C. For a different port, run `python preview.py --port 8001`.

Do not publish the local preview build: it intentionally uses localhost in its canonical URLs. The included GitHub workflow generates production URLs automatically.

## Publish to GitHub Pages

1. Create a GitHub repository, for example `rent-split-resources`, with a `main` branch. A public repository is the straightforward option for free GitHub Pages hosting.
2. Upload **the contents of this folder** to the repository root. Include the hidden `.github/workflows/deploy.yml` file. Do not upload the generated `_site`, `.preview`, or `__pycache__` folders.
3. Open the repository's **Settings → Pages**. Under **Build and deployment**, choose **GitHub Actions** as the source.
4. Open **Actions → Build and deploy GitHub Pages → Run workflow**, and run it on `main`. Future pushes to `main` rebuild and deploy automatically.
5. Open the published URL shown by the deployment. It will usually be `https://YOUR-USERNAME.github.io/rent-split-resources/`.

The `configure-pages` action reads your actual Pages address, including the repository subdirectory or a configured custom domain. The build uses that address for canonical links, internal URLs, Open Graph metadata, structured data, and the sitemap. No placeholder username is shipped to production. If you change the domain or repository URL, rerun the workflow.

If you use a default branch other than `main`, update `on.push.branches` in the workflow. Uploading only `build.py` or choosing “Deploy from a branch” will not build this project; use the included GitHub Actions workflow.

## Google Search Console: verify, submit, inspect

For a standard GitHub project address, create a **URL-prefix property** containing the exact published URL, including `https://` and the repository directory. A Domain property requires DNS control; you cannot verify ownership of `github.io` itself. For a custom domain you own, DNS verification is an option.

### HTML-tag verification

1. In Search Console, select the HTML tag verification method. It gives you a tag like `<meta name="google-site-verification" content="YOUR_TOKEN">`.
2. In your GitHub repository, go to **Settings → Secrets and variables → Actions → Variables** and add a repository variable named **`GOOGLE_SITE_VERIFICATION`**.
3. Set its value to **only the content token**, without the full tag or quotation marks. This is a public verification token, not a private API credential.
4. Run the Pages workflow again. Check the published homepage's source for the verification tag, then click **Verify** in Search Console. Leave the token in place to retain verification.

### Submit the sitemap

Submit the **published site's** sitemap under Search Console's **Sitemaps** section:

```text
https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/sitemap.xml
```

The sitemap contains the homepage, guide index, six guides, resource library, and about page. It deliberately excludes the 404 and all external URLs. You do not own those external pages through your GitHub Pages property.

### Inspect published pages

Use **URL Inspection → Test live URL** for the homepage, `/resources/`, and the guides you want to prioritize. Check that:

- The live page is available and indexing is allowed.
- The user-declared canonical is that page's exact public URL.
- Rendered content includes the page's headings and ordinary links.
- The sitemap URL loads as XML and lists the actual deployed domain and repository path.

After a successful live test, use **Request indexing** where Search Console offers it. A live test does not mean a page is already indexed. Search engines may take time, choose another canonical, or decline to index a page. Repeated submissions do not guarantee faster crawling. Google, other engines, and AI search services independently decide what to crawl, index, rank, or cite.

The `/resources/` page supplies ordinary crawlable links to all 23 external pages; those links have no `nofollow` attribute. They support discovery but cannot override an external host's robots rules, `noindex`, login requirement, canonical, or availability. Only request inspection for external URLs through a separately verified property that covers them.

### GitHub project-site robots.txt detail

The build includes a permissive `robots.txt` and a sitemap reference. On a project site (`username.github.io/repository/`), this file lives at `/repository/robots.txt`. Crawlers use **`/robots.txt` at the origin**, so the project-level file does not control crawling. Check the actual origin's robots file if crawling is blocked; edit it only if you control that root site. Submit the project sitemap directly in Search Console. On a user site or a custom domain served at `/`, the generated robots file is at the correct origin root.

## Content and design

- Six guides cover equal rent shares, bedroom sizes, couples, utilities and reimbursements, restaurant tax and tips, and rent increases.
- Each guide has its own title, description, canonical, visible table of contents, worked examples, related reading, Article markup, and breadcrumbs.
- The library groups the supplied links by rent, bills, profiles, and additional reading. Search and filters enhance the page; all links are already in its HTML.
- The visual design uses a quiet green palette, editorial typography, small custom SVG icons, and responsive layouts.
- The calculator has only **monthly rent** and **number of roommates**, with one equal share shown in dollars. A short note handles any rounding cents. The guides explain room-size methods, couples, and utility bills separately.
- Content is original to this project. External page text has not been copied or presented as reviewed. Supplied link availability could not be independently checked in the build environment; check the external pages before publication and maintain the list over time.
- No fabricated author credentials, reviews, traffic counts, or indexing guarantees are included. Semantic HTML and accurate structured data expose the same useful content to visitors and crawlers.

Edit `content.py` for guides and links, `build.py` for page structure, and `assets/style.css` for design. Keep the assumptions and numerical examples accurate when editing. `lastmod` dates are intentionally omitted from the sitemap rather than invented on every deployment.

## Checks

Python builds and checks the static pages; Node runs the calculator arithmetic checks. There is no `npm install` step.

```powershell
node --test tests/calculator.test.js
python build.py --site-url https://YOUR-USERNAME.github.io/YOUR-REPOSITORY
python tests/check_site.py --site-url https://YOUR-USERNAME.github.io/YOUR-REPOSITORY
```

The static checker verifies unique titles and descriptions, canonical URLs, structured-data JSON, every internal link and fragment, all 23 supplied references, the sitemap, and verification tags. The production workflow runs these checks before deploying.

An optional browser check is available in `tests/browser_check.py`. It needs Python Playwright with Chromium installed and the local preview server running. It checks responsive layouts, calculator interactions, resource filtering, and content with JavaScript disabled. It saves local screenshots under `.preview/`.

## Files

```text
.github/workflows/deploy.yml   GitHub Pages build, checks, and deployment
assets/app.js                  Calculator and resource filters
assets/style.css               Responsive visual design
assets/favicon.svg             Local SVG favicon
build.py                       Static HTML and sitemap builder
content.py                     Original guides and all supplied references
preview.py                     Local preview server
tests/                         Arithmetic, static-output, and optional browser checks
```

The project is prepared locally. Publishing requires your GitHub repository; Search Console verification and URL Inspection require access to your Google account. Neither has been performed by this project generator.
