from __future__ import annotations

import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "dist"
REQUIRED_PAGES = ("index.html", "about.html", "products.html", "portfolio.html", "contact.html")
GENERATED_PAGES = ("broach-tools.html", "pto-components.html")
CATEGORY_FILES = {"broach": "broach-tools.html", "pto": "pto-components.html"}
ROOT_ASSETS = ("CNAME", "robots.txt", "sitemap.xml", "googlee924bcab1d62bc5e.html")


class ProductCardParser(HTMLParser):
    def __init__(self, source: str) -> None:
        super().__init__()
        self.source = source
        self.line_offsets = [0]
        self.line_offsets.extend(index + 1 for index, character in enumerate(source) if character == "\n")
        self.article_start: int | None = None
        self.cards: list[tuple[str, str]] = []

    def source_offset(self) -> int:
        line, column = self.getpos()
        return self.line_offsets[line - 1] + column

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "article":
            return
        attributes = dict(attrs)
        if "product-card" in (attributes.get("class") or "").split():
            self.article_start = self.source_offset()

    def handle_endtag(self, tag: str) -> None:
        if tag != "article" or self.article_start is None:
            return
        end = self.source_offset() + len("</article>")
        card = self.source[self.article_start:end]
        self.article_start = None
        tag_match = re.search(r'class="product-tag">([^<]+)</span>', card)
        if tag_match is not None:
            self.cards.append((tag_match.group(1).strip().lower(), card))


class LocalReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.references.append(value)


def validate_html_references(
    root: Path = ROOT,
    page_names: tuple[str, ...] = REQUIRED_PAGES,
    generated_pages: tuple[str, ...] = (),
) -> None:
    errors: list[str] = []
    for page_name in page_names:
        page = root / page_name
        parser = LocalReferenceParser()
        parser.feed(page.read_text(encoding="utf-8"))
        for reference in parser.references:
            parsed = urlsplit(reference)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = (page.parent / unquote(parsed.path)).resolve()
            if (
                target.parent == root.resolve()
                and target.name in generated_pages
            ):
                continue
            if not target.is_relative_to(root.resolve()) or not target.exists():
                errors.append(f"{page_name}: missing local reference {reference}")

    for css_file in (root / "css").glob("*.css"):
        css_text = css_file.read_text(encoding="utf-8")
        for reference in re.findall(r'url\(["\']?([^"\')]+)', css_text):
            parsed = urlsplit(reference)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = (css_file.parent / unquote(parsed.path)).resolve()
            if not target.is_relative_to(root.resolve()) or not target.exists():
                errors.append(f"{css_file.name}: missing local reference {reference}")

    if errors:
        raise SystemExit("Static-site validation failed:\n" + "\n".join(errors))


def product_cards_by_category() -> dict[str, list[str]]:
    source = (ROOT / "products.html").read_text(encoding="utf-8")
    parser = ProductCardParser(source)
    parser.feed(source)

    categories = {"broach": [], "pto": []}
    for product_tag, card in parser.cards:
        if "broach" in product_tag or "tooling" in product_tag:
            categories["broach"].append(card)
        elif "yoke" in product_tag or "pto" in product_tag:
            categories["pto"].append(card)

    if not categories["broach"] or not categories["pto"]:
        raise SystemExit("Static-site validation failed: product categories are empty.")
    if sum(map(len, categories.values())) != len(parser.cards):
        raise SystemExit("Static-site validation failed: one or more products lack a category.")
    return categories


def build_category_page(category: str, cards: list[str]) -> str:
    page_data = {
        "broach": {
            "title": "Broach Tools & Dies | Star Engineering Tools",
            "description": "Explore keyway, spline, surface, round and custom broach tools and dies from Star Engineering Tools, Ludhiana.",
            "label": "Precision tooling",
            "heading": "Broach tools<br>made for accuracy.",
            "intro": "Explore our broaching tools and dies for internal profiles, splines and external surfaces. Share your drawing or specification to discuss the right tooling for your application.",
            "section_label": "Broaching range",
            "section_heading": "Find the tooling for your application",
            "section_intro": "Browse available tool profiles and enquire about custom sizes, materials or specifications.",
            "other_label": "PTO yokes and components",
            "other_href": "pto-components.html",
        },
        "pto": {
            "title": "PTO Shaft Yokes & Components | Star Engineering Tools",
            "description": "Explore PTO shaft yokes and power transmission components from Star Engineering Tools, Ludhiana.",
            "label": "Power transmission",
            "heading": "PTO components<br>built for the job.",
            "intro": "Browse our PTO shaft yokes and power transmission components. Contact our team to discuss models, fitment, drawings and application requirements.",
            "section_label": "PTO product range",
            "section_heading": "Yokes and components",
            "section_intro": "Explore the range and contact us with your fitment or component requirements.",
            "other_label": "Broach tools and dies",
            "other_href": "broach-tools.html",
        },
    }[category]
    product_markup = "\n                    ".join(cards)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{page_data['description']}">
    <meta name="theme-color" content="#10243a">
    <title>{page_data['title']}</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header class="site-header">
        <nav class="container nav-wrap" aria-label="Main navigation">
            <a class="brand" href="index.html" aria-label="Star Engineering Tools home"><img src="images/logo.png" alt=""><span>Star Engineering Tools<small>Precision in motion</small></span></a>
            <details class="nav-menu"><summary aria-label="Open navigation menu">Menu</summary><div class="nav-links"><a href="index.html">Home</a><a href="about.html">About</a><a href="products.html" aria-current="page">Products</a><a href="portfolio.html">Gallery</a><a href="contact.html">Contact</a><a class="nav-cta" href="contact.html">Get a quote</a></div></details>
        </nav>
    </header>
    <main>
        <section class="page-hero"><div class="container"><div class="breadcrumbs"><a href="index.html">Home</a> / <a href="products.html">Products</a> / {page_data['label']}</div><span class="eyebrow">{page_data['label']}</span><h1>{page_data['heading']}</h1><p>{page_data['intro']}</p><div class="hero-actions"><a class="button" href="contact.html">Discuss your requirement <span aria-hidden="true">→</span></a><a class="button button-outline" href="products.html">Browse all products</a></div></div></section>
        <section class="section section-white">
            <div class="container">
                <div class="product-category-switch"><span>Explore product categories</span><a href="{page_data['other_href']}">{page_data['other_label']} <span aria-hidden="true">→</span></a></div>
                <div class="section-heading"><span class="eyebrow">{page_data['section_label']}</span><h2>{page_data['section_heading']}</h2><p>{page_data['section_intro']}</p></div>
                <div class="product-toolbar">
                    <label class="product-search-label" for="product-search">Search this category</label>
                    <input id="product-search" class="product-search" type="search" placeholder="Search products..." autocomplete="off">
                    <p class="product-status" id="product-status" aria-live="polite"></p>
                </div>
                <p class="product-empty" id="product-empty" hidden>No matching products found. Try another search.</p>
                <div class="product-grid" data-product-section>
                    {product_markup}
                </div>
                <div class="center-action"><a class="button button-dark" href="contact.html">Ask us about a product <span aria-hidden="true">→</span></a></div>
            </div>
        </section>
    </main>
    <footer class="site-footer"><div class="container"><div class="footer-grid"><div><a class="brand" href="index.html"><img src="images/logo.png" alt=""><span>Star Engineering Tools<small>Precision in motion</small></span></a><p>Precision engineering for a world in motion.</p></div><div><h2 class="footer-title">Explore</h2><div class="footer-links"><a href="index.html">Home</a><a href="about.html">About us</a><a href="products.html">All products</a><a href="portfolio.html">Gallery</a><a href="contact.html">Contact</a></div></div><div><h2 class="footer-title">Visit us</h2><p>Back Side of Gurudwara, Near Ganpati Chowk,<br>Ludhiana, Punjab - 141010, India</p><a href="tel:+919814573978">+91 98145 73978</a></div></div><div class="footer-bottom">© 2026 Star Engineering Tools. All rights reserved. <a href="https://www.youtube.com/@STAR_ENGG_TOOLS" target="_blank" rel="noopener noreferrer">YouTube</a></div></div></footer>
    <script src="js/site.js" defer></script>
</body>
</html>
"""


def copy_tree(source: Path, destination: Path) -> None:
    if not source.exists():
        raise SystemExit(f"Required site directory is missing: {source.relative_to(ROOT)}")
    shutil.copytree(source, destination, dirs_exist_ok=True)


def build_site() -> None:
    missing_pages = [page for page in REQUIRED_PAGES if not (ROOT / page).is_file()]
    if missing_pages:
        raise SystemExit("Required site pages are missing: " + ", ".join(missing_pages))

    categories = product_cards_by_category()
    for category, cards in categories.items():
        category_page = ROOT / CATEGORY_FILES[category]
        category_page.write_text(build_category_page(category, cards), encoding="utf-8")

    validate_html_references(page_names=REQUIRED_PAGES + GENERATED_PAGES)
    OUTPUT.mkdir(exist_ok=True)

    for page in ROOT.glob("*.html"):
        shutil.copy2(page, OUTPUT / page.name)

    for asset in ROOT_ASSETS:
        source = ROOT / asset
        if source.is_file():
            shutil.copy2(source, OUTPUT / asset)

    copy_tree(ROOT / "css", OUTPUT / "css")
    copy_tree(ROOT / "js", OUTPUT / "js")
    copy_tree(ROOT / "images", OUTPUT / "images")
    validate_html_references(
        OUTPUT,
        REQUIRED_PAGES + GENERATED_PAGES,
    )
    print(
        f"Built {len(REQUIRED_PAGES) + len(GENERATED_PAGES)} site pages "
        f"({len(categories['broach'])} broach tools, {len(categories['pto'])} PTO products) "
        f"and static assets in {OUTPUT}"
    )


if __name__ == "__main__":
    build_site()
