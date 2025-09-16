"""Static gallery sorter

Usage:
  python3 scripts/sort_gallery.py --input index.html --output index.sorted.html --by name
  python3 scripts/sort_gallery.py --input index.html --output index.sorted.html --by date --order desc

This script finds the gallery <div class="grid"> ... </div> and sorts its immediate
.child <article class="card"> blocks by the card title (h3.title) or by the date
found in <p class="sub">. It preserves everything else unchanged and creates a
backup of the original file.
"""
import argparse
import re
from datetime import datetime
from html import unescape

CARD_RE = re.compile(r"(<!-- ▶▶ PHOTO CARD START -->\s*)(<article[\s\S]*?</article>)(\s*<!-- ◀◀ PHOTO CARD END -->)", re.M)
GRID_RE = re.compile(r"(<div class=\"grid\">)([\s\S]*?)(</div>\s*</section>)", re.M)

TITLE_RE = re.compile(r"<h3\s+class=\"title\">\s*([^<]+?)\s*</h3>", re.I)
SUB_RE = re.compile(r"<p\s+class=\"sub\">\s*([^<]+?)\s*</p>", re.I)


def parse_date_from_sub(text):
    if not text:
        return None
    # Normalize hyphens
    norm = text.replace('\u2010','-').replace('\u2011','-').replace('\u2012','-').replace('\u2013','-').replace('\u2014','-')
    # ISO YYYY-MM-DD
    m = re.search(r"(\d{4}-\d{2}-\d{2})", norm)
    if m:
        try:
            return datetime.fromisoformat(m.group(1))
        except Exception:
            pass
    # Try month name formats
    m = re.search(r"([A-Za-z]{3,9}\s+\d{1,2},\s*\d{4})", norm)
    if m:
        try:
            return datetime.strptime(m.group(1), "%B %d, %Y")
        except Exception:
            try:
                return datetime.strptime(m.group(1), "%b %d, %Y")
            except Exception:
                pass
    m = re.search(r"(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})", norm)
    if m:
        try:
            return datetime.strptime(m.group(1), "%d %B %Y")
        except Exception:
            try:
                return datetime.strptime(m.group(1), "%d %b %Y")
            except Exception:
                pass
    # mm/dd/yyyy
    m = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", norm)
    if m:
        try:
            return datetime.strptime(m.group(1), "%m/%d/%Y")
        except Exception:
            pass
    return None


def extract_cards(grid_html):
    # Find all article.card blocks using the PHOTO CARD START/END comment markers
    cards = []
    for m in CARD_RE.finditer(grid_html):
        prefix = m.group(1)
        article = m.group(2)
        suffix = m.group(3)
        title_m = TITLE_RE.search(article)
        sub_m = SUB_RE.search(article)
        title = unescape(title_m.group(1).strip()) if title_m else ''
        sub = unescape(sub_m.group(1).strip()) if sub_m else ''
        date = parse_date_from_sub(sub)
        cards.append({'prefix':prefix,'article':article,'suffix':suffix,'title':title,'sub':sub,'date':date})
    return cards


def replace_grid(original_html, sorted_cards):
    # Rebuild the inner grid portion keeping outer wrapper intact
    def repl(m):
        start = m.group(1)
        inner = m.group(2)
        end = m.group(3)
        # Build new inner content
        joined = '\n'.join([c['prefix'] + c['article'] + c['suffix'] for c in sorted_cards])
        return start + '\n' + joined + '\n' + end
    return GRID_RE.sub(repl, original_html, count=1)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', default='index.html')
    p.add_argument('--output', default=None)
    p.add_argument('--by', choices=['name','date'], default='name')
    p.add_argument('--order', choices=['asc','desc'], default='asc')
    args = p.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        html = f.read()

    g = GRID_RE.search(html)
    if not g:
        print('No grid section found. Aborting.')
        return

    cards = extract_cards(g.group(2))
    if not cards:
        print('No photo cards found between the markers. Aborting.')
        return

    if args.by == 'name':
        cards.sort(key=lambda c: c['title'].lower() if c['title'] else '')
        if args.order == 'desc':
            cards.reverse()
    else:
        # date sort: None dates treated as very old or very new depending on order
        def keyfunc(c):
            if c['date']:
                return c['date']
            return datetime.min if args.order == 'asc' else datetime.max
        cards.sort(key=keyfunc, reverse=(args.order=='desc'))

    out_html = replace_grid(html, cards)

    out_path = args.output or args.input
    # backup original
    if out_path == args.input:
        with open(args.input + '.bak', 'w', encoding='utf-8') as f:
            f.write(html)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(out_html)
    print(f'Wrote sorted HTML to {out_path}')


if __name__ == '__main__':
    main()
