# Data Explorer: an example Docsie app

A pivot table with ten chart types that opens inside the Docsie chat. Ask the assistant to analyze a CSV or Excel file, an AI Table or the sample data, and the Data Explorer appears in the conversation: drag fields onto rows, columns and values, filter, switch charts, export a formatted Excel workbook, or hand the view back to the assistant to write a report.

This is the same Data Explorer that ships with Docsie, so you don't need to install it: it's already part of every organization's AI assistant. Install this copy only to try how apps are installed, or use it as a starting point for your own app. Docsie's built-in copy and this folder use the same files and the same app interface, so this is a working example of everything an app can do:

| An app can… | How the Data Explorer does it |
|---|---|
| Show its own screen in the chat | `ui/explorer.html`, one self-contained HTML file |
| Let the assistant open it with arguments | the `explorer` component and its `input_schema` (file, AI Table, fields, chart) |
| Use Docsie's capabilities from the screen | `docsie_tools`: list data sources, load rows, save an Excel export |
| Talk back to the assistant | **Write a report** posts the current view to the chat |
| Remember the user's view | the view is saved with the chat message and restored when the chat redraws |

## Folder layout

```
apps/data-explorer/
├── SKILL.md          instructions for the assistant
├── app.json          the manifest: the screen and the Docsie tools it uses
└── ui/
    └── explorer.html the screen: pivot engine, charts and exports, no outside libraries
```

## The manifest

```json
{
  "manifest_version": 1,
  "name": "Data Explorer",
  "components": [
    {
      "name": "explorer",
      "title": "Data Explorer",
      "entry": "ui/explorer.html",
      "input_schema": {"type": "object", "properties": {
        "file_id": {"type": "string"}, "sheet": {"type": "string"},
        "table_id": {"type": "string"}, "sample": {"type": "boolean"},
        "rows": {"type": "array", "items": {"type": "string"}},
        "columns": {"type": "array", "items": {"type": "string"}},
        "values": {"type": "array", "items": {"type": "string"}},
        "chart": {"type": "string"}}},
      "prefers_border": false
    }
  ],
  "docsie_tools": ["data_sources", "data_load_rows", "data_export_view"]
}
```

- `components`: the app has one screen. Installing the app gives the assistant the tool `app__data-explorer__explorer`, whose arguments come from `input_schema`.
- `docsie_tools`: the Docsie tools the screen may call. Docsie refuses any other tool. Each call runs as the person using the screen, with the same permissions and audit log as when the assistant calls a tool.
- No `tables`: the Data Explorer reads data that is already in the workspace and keeps nothing of its own. An app that needs to store records declares AI Tables here (see `apps/feedback-tracker`).

## How the screen works

The screen runs in a sandboxed frame inside the chat. It can't read files, cookies or the internet. It talks to Docsie with JSON-RPC messages over `postMessage`, following the open MCP Apps standard (protocol `2026-01-26`). The script in `ui/explorer.html` is organized in labelled sections; the ones below are the parts to read first.

### 1. Connect (`JSON-RPC client`, `boot`)

The screen sends `ui/initialize` and gets the host context back: theme, display mode and the user's saved view, if any. It then sends `ui/notifications/initialized`.

### 2. Find out what to open (`tool result & loading`)

Docsie sends the assistant's arguments (`ui/notifications/tool-input`) and the tool result (`ui/notifications/tool-result`).

- Opened by Docsie's built-in `explore_data` tool, the result carries a signed dataset reference.
- Opened as this app, the result carries the arguments: a `file_id`, a `table_id`, `sample`, or nothing. With nothing to open, the screen shows a picker, filled by the `data_sources` tool.

### 3. Load the rows

```js
const r = await request('tools/call', {name: 'data_load_rows', arguments: {table_id: 'boo_…', view: {rows: ['Sentiment']}}});
// r.structuredContent = {dataset_ref, title, source, columns: [{name, type}], rows: [[…]], total_rows, truncated, suggested_view}
```

Docsie reads the file or AI Table on the server, types each column (number, date or text) and returns up to 50,000 rows. The rows go to the screen only; the assistant never sees them. `dataset_ref` is a signed reference the screen uses for later calls.

### 4. Pivot and chart in the browser (`pivot engine`, `charts`)

Everything after loading happens in the browser: grouping, totals and subtotals, filters, sorting, top N, date grains and the ten chart types, drawn as inline SVG.

### 5. Export (`export payloads`)

```js
const r = await request('tools/call', {name: 'data_export_view', arguments: {dataset_ref, format: 'xlsx', title, view, table, chart}});
// r.structuredContent = {file_id, filename, download_url}
```

Docsie builds the workbook on the server: a report sheet with the pivot table, a native Excel chart, the filtered data and the view definition. It saves it as a private workspace file. The screen then asks the host to download it with `ui/download-file`.

### 6. Hand the view to the assistant (`report brief`)

**Write a report** sends a `ui/message` with a short brief: the view, its filters and the numbers. The assistant writes the report and exports it with the workspace's Word template, as `SKILL.md` tells it to.

### 7. Remember the view (`view state`)

When the user changes the view, the screen sends `docsie/notifications/view-state`. Docsie keeps it with the chat message and returns it in the host context the next time the screen opens, so the chat can redraw without losing the user's work.

## Docsie tools a screen can use

List any of these in `docsie_tools`:

| Tool | What it does |
|---|---|
| `data_sources` | Lists the workspace's CSV, Excel and JSON files and AI Tables |
| `data_load_rows` | Reads the rows of a workspace file, an AI Table or the sample dataset |
| `data_export_view` | Saves a table and chart as a formatted Excel or CSV file in the workspace |
| `job_status` | Follows a job the screen started, such as a Word export, and returns its file |
| `search_articles`, `list_shelves`, `list_books`, `list_articles`, `get_article_raw` | Find and read documentation |
| `create_article` | Creates an article |
| `list_files`, `get_file_info` | Find workspace files |
| `export_document` | Exports Markdown as a Word, PDF or PowerPoint file with the workspace template |

A screen calls them with `tools/call`. The answer's `structuredContent` holds the result. If the call fails, `isError` is `true` and `content[0].text` says why.

## Make your own

1. Copy the folder: `cp -R apps/data-explorer apps/my-analysis`.
2. Change `name` in `app.json`, and the screen in `ui/explorer.html`. For example, ask Claude Code: *"In apps/my-analysis, turn the Data Explorer into a sales dashboard that opens on a fixed set of KPIs. Keep the JSON-RPC client and the data_load_rows call."*
3. Zip the folder and upload it in Enterprise Portal → **Skills & Agents → Apps**, then choose **Install**.
4. In the chat, ask: *"Open my-analysis on the sales CSV."*
