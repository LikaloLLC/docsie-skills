---
name: data-explorer
description: Analyze tabular data in a pivot table with charts, from workspace CSV, Excel or JSON files, AI Tables or sample data, and export formatted Excel files or a written report.
---

# Data Explorer

## When to use
The user wants to analyze, pivot, chart, compare or summarize data in a file, a spreadsheet or an AI Table.

## Open it
1. Open the screen with `app__data-explorer__explorer`.
2. If the user named a file, find it with `list_files` and pass its `file_id` (and `sheet` for Excel). For an AI Table, pass `table_id`. For a demo, pass `sample: true`. Otherwise pass nothing: the screen lets the user pick.
3. To start from a view, pass field names in `rows`, `columns` and `values`, and a `chart`.

## Rules
- The user explores in the screen. Don't repeat its numbers in the chat.
- When the screen sends you a view to write up, write the report in Markdown from that view only, then export it with `export_document` and `output_format` "docx".
