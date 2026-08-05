---
name: release-notes
description: Turn a changelog into release notes, one article per product area, in a consistent format.
---

# Release notes

Turn a changelog into release notes that customers can read: one article per product area.

## When to use

You are given a release name, a changelog and a book to write into. The changelog is usually CSV with the columns `area,type,summary` (see `examples/changelog.csv`), but it can also be a plain bullet list.

`type` is one of `new`, `improved` or `fixed`.

## Output format

For each product area, write one article titled with the area name, for example `Editor`.

Use these sections, in this order, and leave out any section that would be empty:

1. **New**
2. **Improved**
3. **Fixed**

Each entry is one bullet. Follow `references/style.md` for wording.

## Saving

Save one article per area in the book you are given. Do not create shelves or books, and do not publish.

## Rules

- Use only what the changelog says. Never invent features, numbers or dates.
- Merge duplicate entries for the same change.
- Leave out internal entries such as refactoring, test or build changes.

## Python step

`scripts/main.py` does the same job without rewording: it groups the CSV by area and saves one article per area. Use it when the changelog is already written for customers.

Inputs: `book_id`, `changelog_csv` (the CSV text). It writes `result.json` with the IDs of the articles it created.
