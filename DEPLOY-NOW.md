# Update the live website

Live address: **https://rent-split-resources.github.io/**

The supplied live HTML used localhost for canonical, Open Graph, and structured-data URLs. This package fixes those values across the site. The sitemap and robots.txt also use the live address.

## 1. Upload the corrected files

Open the GitHub repository that publishes the live address above. Choose **Add file → Upload files**.

On your computer, open `Documents/rent-split-resources/UPLOAD-TO-GITHUB` and upload its visible contents to the repository root. Alternatively, extract `rent-split-resources-upload.zip` and upload the extracted contents. Commit the changes to `main`.

The website's `index.html` must be directly at the repository root, with `guides/`, `resources/`, `about/`, `assets/`, `404.html`, `sitemap.xml`, and `robots.txt` alongside it. The package also supplies the updated `build.py`, `content.py`, `preview.py`, and `tests/` for future builds. Upload all these files so an old build cannot replace the corrected HTML.

Do not upload the ZIP file by itself or the containing `UPLOAD-TO-GITHUB` directory as a nested folder. Do not upload `.preview`, `__pycache__`, or `_site` as nested folders.

## 2. Replace the Pages workflow

Your reported workflow filename was `.github/workflows/static.yml`.

1. In GitHub's Code tab, open `.github/workflows/static.yml` and click the pencil to edit it.
2. Open the visible local `COPY-WORKFLOW.txt` file.
3. Copy all its contents and replace the entire GitHub workflow file contents with them.
4. Commit the change to `main`.

If `static.yml` does not exist, choose **Add file → Create new file**, enter `.github/workflows/static.yml` as the filename, paste the same contents, and commit. GitHub creates the hidden folders automatically. If your active Pages workflow has a different filename, replace that existing workflow instead. Keep only one active Pages deployment workflow; disable any older duplicate through **Actions → select the old workflow → ... → Disable workflow**.

The corrected workflow builds with `SITE_URL: https://rent-split-resources.github.io`, validates the pages, and publishes only `_site`. It does not publish a local preview.

## 3. Deploy and check

1. Under **Settings → Pages → Build and deployment**, set **Source** to **GitHub Actions**. Leave **Custom domain** empty.
2. Open **Actions → Build and deploy GitHub Pages**. The commit should start a run; if needed choose **Run workflow → main → Run workflow**.
3. Wait for both build and deploy to succeed, then refresh the live website and view its source.

The live homepage must contain:

```html
<link rel="canonical" href="https://rent-split-resources.github.io/">
```

Each other indexable page has its own canonical, for example:

```html
<link rel="canonical" href="https://rent-split-resources.github.io/guides/how-to-split-rent-fairly/">
```

The 404 page intentionally has `noindex` and no canonical. Check that the live homepage, guides, sitemap, and robots.txt contain no localhost URLs. The published sitemap is **https://rent-split-resources.github.io/sitemap.xml**.

## Future edits

Edit the source, run `python build.py`, and check with `python tests/check_site.py --site-url https://rent-split-resources.github.io`. The default build uses the live address. `python preview.py` builds into `.preview/local-site` and cannot overwrite production output. Once the corrected workflow is installed, pushing source updates to `main` rebuilds the deployed pages automatically.

The prepared files have been checked locally. This session cannot access GitHub, so it has not uploaded these changes or verified the corrected live deployment.
