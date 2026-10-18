# Feedback Tracker: an example Docsie app

An app is a skill package with an `app.json` manifest. Installing it gives the Docsie AI assistant three things:

- **Custom UI.** A component the chat shows in a sandboxed frame. Here it is the feedback board.
- **Storage.** An AI Table that Docsie creates when you install the app. Here it holds the feedback rows.
- **Instructions.** `SKILL.md` tells the agent when to use the app and how to fill in the table.

Use this folder as a starting point for your own app.

## What the board does

- **Board and List layouts.**
  - Board: one column per status. Drag a card to another column to change its status, or use the card's menu or Shift+Left and Shift+Right.
  - List: a sortable table.
- **Filters.** Sentiment chips, product area, status and a text search.
- **Add, edit and delete.** A form with validation. Changes show at once and are rolled back with an error message if Docsie refuses them.
- **Summary strip.** The total, a sentiment bar, the share of negative feedback and the newest item.
- **Summarize in chat.** Sends a short brief of the visible items to the chat and asks the agent to summarize it.
- **Display.** Light and dark themes, inline and full-screen views, and narrow widths down to 560 px.

## Folder layout

```
apps/feedback-tracker/
├── SKILL.md        instructions for the Docsie agent
├── app.json        manifest: components and tables
└── ui/
    └── board.html  the board component, one self-contained HTML file
```

## The manifest

```json
{
  "manifest_version": 1,
  "name": "Feedback Tracker",
  "description": "Collect, triage and summarize customer feedback right in the chat.",
  "components": [ ... ],
  "tables": [ ... ]
}
```

| Field | What it does |
|---|---|
| `manifest_version` | Always `1`. |
| `name` | The app's name. Its slug (`feedback-tracker`) names the agent's tools. Keep it short: the slug is cut at 24 characters. |
| `description` | Shown on the app's card in Docsie. |
| `components` | 1 to 10 UI components. Each becomes a tool that opens it in the chat. |
| `tables` | Up to 10 tables. Docsie creates each one as an AI Table when you install the app. |

A component:

```json
{"name": "board", "title": "Feedback board", "entry": "ui/board.html",
 "description": "Open the feedback board: every feedback item with its sentiment and status, a quick-add form and a summary. Use when the user wants to see, add, triage or review feedback.",
 "input_schema": {"type": "object", "properties": {
   "status": {"type": "string", "enum": ["New", "Planned", "In progress", "Done", "Won't do"], "description": "Show only this status"},
   "highlight": {"type": "string", "description": "Row id to highlight, e.g. one just added"}}},
 "prefers_border": false}
```

- `name`: lowercase letters, digits, `-` or `_`, up to 24 characters. It can't be `data`, which is reserved for the data tool.
- `entry`: the HTML file in the package.
- `description`: the agent reads it to decide when to open the component. Say what it shows and when to use it.
- `input_schema`: the arguments the agent can pass. The component receives them in `tool-input`.
- `prefers_border`: `false` because the board draws its own background.

A table:

```json
{"key": "feedback", "name": "Customer feedback",
 "fields": [
   {"key": "title", "label": "Title", "type": "text", "required": true},
   {"key": "sentiment", "label": "Sentiment", "type": "select", "config": {"options": ["Positive", "Neutral", "Negative"]}},
   {"key": "received", "label": "Received", "type": "date"}
 ]}
```

- Field types: `text`, `number`, `select`, `date`, `checkbox`, `email`, `url`.
- A `select` field needs `config.options`.
- Field keys start with a lowercase letter and use only lowercase letters, digits and `_`. A table has 1 to 60 fields.

## What installing does

1. Docsie creates each table as an AI Table on the shelf you choose. Its columns are the fields.
2. The agent gets one tool per component and one data tool:
   - `app__feedback-tracker__board` opens the board. Its parameters come from `input_schema`.
   - `app__feedback-tracker__data` lists, adds, updates and deletes rows.
3. The `description` in `SKILL.md` joins the agent's list of skills, with the first 1,200 characters of the instructions. Keep `SKILL.md` short and put the rules first.

Uninstalling removes the tools. The tables and their rows stay on the shelf.

A typical turn: the user pastes notes from a customer call. The agent adds a row with the data tool:

```json
{"action": "add", "table": "feedback",
 "data": {"title": "PDF export drops table borders", "customer": "Northwind Labs",
          "sentiment": "Negative", "status": "New", "area": "Export", "received": "2026-10-16"}}
```

Then it opens the board with `{"highlight": "<the new row id>"}`.

## How the data is stored

Each row is JSON keyed by field key:

```json
{"id": "trw_8f3k2a",
 "data": {"title": "PDF export drops table borders", "details": "Tables lose their borders in exported PDFs.",
          "customer": "Northwind Labs", "sentiment": "Negative", "status": "New",
          "area": "Export", "received": "2026-10-16"},
 "created": "2026-10-16T09:15:00Z", "updated": null, "created_by": "Ines Varga"}
```

Docsie checks every write:

- `select` values must be one of the options.
- Dates are `YYYY-MM-DD`.
- Required fields must be set when a row is added.
- Unknown field keys are rejected.
- `null` or `""` clears a field.

`rows.list` returns the newest rows first. Its `filter` matches exact values, and it returns at most 500 rows per call.

The component and the agent work on the same rows, as the signed-in user. Reading needs read access to the table's workspace and book. Writing needs create access.

## The component protocol

Docsie loads `board.html` into an iframe with `srcdoc` and `sandbox="allow-scripts allow-forms"`, and adds this Content Security Policy:

```
default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';
img-src 'self' data: blob:; font-src 'self' data:; media-src 'self' data: blob:;
connect-src 'none'; frame-src 'none'; worker-src 'self' blob:; base-uri 'self';
object-src 'none'; form-action 'none'
```

So the component:

- keeps all CSS, JavaScript and icons inline in the file;
- can't fetch anything, use `localStorage` or cookies, or submit a form;
- gets all of its data through the host.

It talks to Docsie with JSON-RPC 2.0 messages (MCP Apps, protocol `2026-01-26`) sent with `window.parent.postMessage(msg, '*')`. It accepts only messages where `event.source === window.parent`.

### 1. Handshake

The component asks first:

```js
const res = await bridge.request('ui/initialize', {
  protocolVersion: PROTOCOL_VERSION,
  appInfo: APP_INFO,
  appCapabilities: {availableDisplayModes: ['inline', 'fullscreen']}
}, 20000) || {};
```

The result is `{protocolVersion, hostInfo, hostCapabilities, hostContext}`. `hostContext` carries `theme`, `displayMode`, `availableDisplayModes`, `containerDimensions` and, if the user changed the view before, `docsieViewState`. The component then sends the notification `ui/notifications/initialized` with no params.

### 2. Messages from Docsie

| Method | Params | What the board does |
|---|---|---|
| `ui/notifications/tool-input` | `{arguments}` | The agent's arguments, such as `{"status": "New", "highlight": "trw_..."}`. |
| `ui/notifications/tool-result` | a CallToolResult | Reads `structuredContent` (below), then loads the rows. |
| `ui/notifications/host-context-changed` | part of the host context | Switches theme or display mode. |
| `ui/notifications/tool-cancelled` | `{reason?}` | Shows "Request cancelled" if the rows haven't loaded yet. |
| `ui/resource-teardown` | request | Sends any unsaved view state, then replies `{}`. |
| `ping` | request | Replies `{}`. |

The tool result's `structuredContent`:

```json
{"app": {"name": "Feedback Tracker", "install_id": "app_..."},
 "tables": [{"key": "feedback", "name": "Customer feedback", "book_id": "boo_...",
             "fields": [{"key": "title", "label": "Title", "type": "text", "required": true, "config": {}}, ...]}],
 "input": {"status": "New"}}
```

### 3. Messages to Docsie

Read and write rows with `tools/call`. Each answer is a CallToolResult: the data is in `structuredContent`. If the call fails, `isError` is `true` and the reason is in `content[0].text`.

| Tool name | Arguments | `structuredContent` |
|---|---|---|
| `rows.list` | `{table, limit?, offset?, filter?}` | `{rows: [...], total}` |
| `rows.add` | `{table, data}` | `{row}` |
| `rows.update` | `{table, id, data}` with only the changed fields | `{row}` |
| `rows.delete` | `{table, id}` | `{deleted: true}` |

```js
const sc = await bridge.callTool('rows.update', {table: S.table.key, id: row.id, data: patch});
```

The other requests and notifications:

| Method | Params | Used for |
|---|---|---|
| `ui/message` (request) | `{role: "user", content: {type: "text", text}}` | **Summarize in chat**: posts a brief to the chat as the user. |
| `ui/request-display-mode` (request) | `{mode: "fullscreen" \| "inline"}` | The full-screen button. It shows only if `availableDisplayModes` includes `fullscreen`. The result is `{mode}`. |
| `ui/notifications/size-changed` | `{width, height}` | Reports the inline height. The board uses 600 px and never more than 640. |
| `docsie/notifications/view-state` | `{state}` | A Docsie extension that remembers the user's view (below). |

The brief that **Summarize in chat** sends starts like this:

```
Summarize this customer feedback: main themes, what is most negative, and what to prioritise. Use only these items.

Feedback Tracker: 40 items.
By sentiment: Positive 10, Neutral 15, Negative 15 (38% negative).
By status: New 11, Planned 9, In progress 5, Done 12, Won't do 3.
By product area: Editor 8, Portal 6, Translation 4, Publishing 4, Export 3, Permissions 3, Search 2, AI chat 2, 6 more.

15 most recent:
- 2026-10-16 · Negative · Export · New: PDF export drops table borders
```

### 4. Saved view

About 400 ms after the user changes the layout, a filter, the search or the sort, the board sends:

```json
{"state": {"version": 1, "table": "feedback",
           "filters": {"status": null, "sentiment": ["Negative"], "area": null, "q": "portal"},
           "layout": {"view": "list", "sort": {"field": "title", "dir": "asc"}}}}
```

When the message renders again, Docsie returns that object as `hostContext.docsieViewState`. The board checks every part of it against the current fields and ignores anything that doesn't fit. A saved view wins over the agent's `status`, because the user changed it later.

### The bridge

Section 1 of the script in `board.html` is a small JSON-RPC client you can copy into your own component:

```js
bridge.request(method, params)   // -> Promise of the host's result
bridge.notify(method, params)    // one-way message
bridge.on(method, handler)       // handle a host notification or request; a request's reply is the handler's return value
bridge.callTool(name, args)      // -> Promise of structuredContent; throws with the host's error text
```

The board registers its handlers like this:

```js
bridge.on('ui/notifications/tool-input', (p) => applyInput(p.arguments));
bridge.on('ui/notifications/tool-result', onToolResult);
bridge.on('ui/notifications/host-context-changed', applyContext);
bridge.on('ui/resource-teardown', () => { flushView(); S.torn = true; return {}; });
bridge.on('ping', () => ({}));
```

## Change the fields, and the UI follows

The board reads labels, types and options from the fields in the tool result, not from its own code. Only the defaults in section 2 of the script name fields, to decide which field plays which part on a card:

```js
const ROLE_KEYS = {title: 'title', details: 'details', customer: 'customer', sentiment: 'sentiment', status: 'status', area: 'area', date: 'received'};
```

If a key is missing, the board falls back by type. For example, the first required text field becomes the title and the first date field becomes the date.

- **Add a field to `app.json`.** For example, `{"key": "priority", "label": "Priority", "type": "select", "config": {"options": ["Low", "Medium", "High"]}}`. It appears in the form, as a list column and in the search.
  - Select fields with up to 4 options get a segmented picker; longer ones get a dropdown.
  - `date`, `number`, `email` and `url` fields get the matching inputs, and `checkbox` fields get a checkbox.
- **Rename or add a status option.** The board's columns follow.
  - A row whose status is no longer an option shows in the first column.
- **Rename a sentiment option.** The chips and the sentiment bar follow.
  - Colors come from the names `Positive`, `Neutral` and `Negative`. Other names use the Folio chart palette in order.

After you change the tables, upload the new revision and install it again. Docsie adds the missing tables and fields; existing rows keep their data.

## Build your own app with Claude Code

1. Copy this folder and rename it:

   ```bash
   cp -R apps/feedback-tracker apps/vendor-risk
   ```

2. Ask Claude Code to adapt it, for example:

   > In apps/vendor-risk, turn the Feedback Tracker into a Vendor Risk register. Table `vendors` with fields name (required), owner, risk (Low/Medium/High), status (Assessing, Approved, Blocked), next_review (date) and notes. Rename the component to `register`, update app.json, SKILL.md and README.md, and keep section 1 (the bridge) of ui/board.html unchanged. No external scripts, fonts or requests: the component runs under a strict CSP.

3. Test it in a browser with a fake host before you upload it. The host only needs to:
   - put the HTML in an iframe with `srcdoc`, `sandbox="allow-scripts allow-forms"` and the CSP above in a `<meta http-equiv="Content-Security-Policy">` tag;
   - answer `ui/initialize`;
   - send `tool-input` and `tool-result` after `ui/notifications/initialized`;
   - answer `rows.*` from an in-memory array.

   Run it from a local web server. Check the console for CSP errors.

4. Push the folder to your repository.
5. In Enterprise Portal, open **Skills & Agents → Skill packages** and upload the folder (or import it from your repository). Then open the **Apps** tab, pick the workspace and shelf for its data and choose **Install**.
6. In the chat, try: *"Log this from today's call with Northwind Labs: their PDF exports lose table borders."*

## Checklist for your own component

- [ ] Everything is inline. No `fetch`, external fonts, scripts or images, `eval` or `localStorage`.
- [ ] Use `event.preventDefault()` on form submit.
- [ ] Reply to `ping` and `ui/resource-teardown`.
- [ ] Ignore messages that don't come from `window.parent`.
- [ ] Show loading, empty and error states, and show the host's error text.
- [ ] Undo a change the host refuses, and say why.
- [ ] Check `docsieViewState` before you use it.
- [ ] Follow `hostContext.theme`. Pair every color with a word.
- [ ] Keep `SKILL.md` instructions within 1,200 characters, and keep names, emails and phone numbers out of titles.
