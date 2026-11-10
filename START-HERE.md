# Your RentSplit Guide website

This project is ready to upload to a GitHub repository. It contains:

- A custom responsive homepage and a simple rent calculator: monthly rent, roommates, and one equal share.
- Six original guides with worked calculations.
- All 17 reading links and all 6 profile links you supplied.
- Automatic production metadata, a sitemap, structured data, and Google verification support.

## See it locally

Open a terminal in this folder, run `python preview.py`, and visit **http://localhost:8000**. Python 3.12 or newer is required.

## Put it online

1. Create a public GitHub repository with a `main` branch.
2. Upload this folder's source contents, including `.github/workflows/deploy.yml`.
3. In **Settings → Pages**, choose **GitHub Actions**.
4. In **Actions**, run **Build and deploy GitHub Pages**.

Do not upload the generated `_site` folder; the workflow creates the live version using your actual GitHub Pages address.

## Connect Search Console

1. Add a URL-prefix property for your exact published site address.
2. Choose HTML tag verification and copy its `content` token.
3. Add that token as the GitHub Actions repository variable `GOOGLE_SITE_VERIFICATION`.
4. Run the deployment again, then verify in Search Console.
5. Submit your site's `sitemap.xml` and inspect the homepage, resources page, and guides.

The sitemap covers your site's ten pages. The 23 external URLs are linked in the resource library. Their hosting sites and search engines control whether they can be crawled or indexed; faster indexing is not guaranteed.

See [README.md](README.md) for detailed instructions, the project-site robots.txt limitation, and the checks included with this project.

This project has been created and checked locally. It has not yet been published to GitHub or submitted to Search Console.
