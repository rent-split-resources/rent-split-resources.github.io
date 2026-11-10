# Your RentSplit Guide website

This update is prepared for **https://rent-split-resources.github.io/**. It contains:

- A custom responsive homepage and a simple rent calculator: monthly rent, roommates, and one equal share.
- Six original guides with worked calculations.
- All 17 reading links and all 6 profile links you supplied.
- Correct production canonical URLs, Open Graph URLs, structured data, and a sitemap.

## See it locally

Open a terminal in this folder, run `python preview.py`, and visit **http://localhost:8000**. Python 3.12 or newer is required. The preview writes to `.preview/local-site` and leaves the production `_site` folder untouched.

## Put it online

1. Open the repository that publishes **https://rent-split-resources.github.io/**.
2. Upload the contents of `UPLOAD-TO-GITHUB` (or extract `rent-split-resources-upload.zip` first). Replace the existing `.github/workflows/static.yml` using the contents of `COPY-WORKFLOW.txt` if GitHub blocks the hidden folder upload.
3. In **Settings → Pages**, choose **GitHub Actions**.
4. In **Actions**, run **Build and deploy GitHub Pages**.

The upload package includes corrected HTML at its root, plus the source files. The provided workflow rebuilds the site and publishes `_site`. Leave **Custom domain** empty. Follow [DEPLOY-NOW.md](DEPLOY-NOW.md) for exact upload steps.

## Connect Search Console

1. Add a URL-prefix property for `https://rent-split-resources.github.io/`.
2. Choose HTML tag verification and copy its `content` token.
3. Add that token as the GitHub Actions repository variable `GOOGLE_SITE_VERIFICATION`.
4. Run the deployment again, then verify in Search Console.
5. Submit `https://rent-split-resources.github.io/sitemap.xml` and inspect the homepage, resources page, and guides.

The sitemap covers your site's ten pages. The 23 external URLs are linked in the resource library. Their hosting sites and search engines control whether they can be crawled or indexed; faster indexing is not guaranteed.

See [README.md](README.md) for detailed instructions, the project-site robots.txt limitation, and the checks included with this project.

The previous version is already live according to the owner. These corrected files still need to be uploaded to GitHub and deployed.
