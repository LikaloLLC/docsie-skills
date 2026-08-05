"""Group a changelog CSV by product area and save one release-notes article per area.

Usage: python main.py <inputs.json> <output-folder>
inputs.json: {"book_id": "boo_...", "changelog_csv": "area,type,summary\\n..."}

Runs as a Docsie Python step, or on your own machine or CI with DOCSIE_WORKFLOW_URL and
DOCSIE_WORKFLOW_TOKEN set and sdk/docsie_workflows.py on the Python path.
"""
import csv
import io
import json
import sys
from collections import OrderedDict
from pathlib import Path

from docsie_workflows import Docsie

SECTIONS = (('new', 'New'), ('improved', 'Improved'), ('fixed', 'Fixed'))


def group(changelog_csv):
    areas = OrderedDict()
    for row in csv.DictReader(io.StringIO(changelog_csv)):
        area = (row.get('area') or '').strip()
        kind = (row.get('type') or '').strip().lower()
        summary = (row.get('summary') or '').strip()
        if not area or not summary or kind not in dict(SECTIONS):
            continue
        entries = areas.setdefault(area, {key: [] for key, _ in SECTIONS})
        if summary not in entries[kind]:
            entries[kind].append(summary)
    return areas


def markdown(entries):
    parts = []
    for key, heading in SECTIONS:
        if entries[key]:
            parts.append(f'## {heading}\n\n' + '\n'.join(f'- {line.rstrip(".")}.' for line in entries[key]))
    return '\n\n'.join(parts) + '\n'


def main():
    inputs = json.loads(Path(sys.argv[1]).read_text())
    output = Path(sys.argv[2])
    output.mkdir(parents=True, exist_ok=True)
    api = Docsie()
    created = []
    for area, entries in group(inputs['changelog_csv']).items():
        article = api.call('import_markdown_as_article', book_id=inputs['book_id'], title=area,
                           markdown_content=markdown(entries))
        created.append({'area': area, 'article_id': article.get('id')})
    (output / 'result.json').write_text(json.dumps({'articles': created}))
    print(f'Saved {len(created)} release-notes articles.')


if __name__ == '__main__':
    main()
