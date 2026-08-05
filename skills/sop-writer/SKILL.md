---
name: sop-writer
description: Turn rough notes into a standard operating procedure in our house format.
---

# SOP writer

Turn rough notes into a standard operating procedure in our house format.

## When to use
Someone gives you a task name and rough notes (a chat message, meeting notes, a ticket) and wants a procedure people can follow on the floor.

## Output format
Write Markdown with exactly these sections, in this order:

1. **Purpose** — one sentence: what the procedure achieves.
2. **Scope** — who does it and when it applies.
3. **Safety and prerequisites** — bullet list. Write "None" if there are none.
4. **Procedure** — numbered steps. One action per step, starting with a verb. Put the expected result after an arrow: `→ The green light comes on.`
5. **Verification** — how the operator confirms it worked.
6. **Revision** — a one-row table: `| Version | Date | Change |` with `1.0`, today's date and `First issue`.

Follow `references/style.md` for wording.

## Saving
Save the SOP as one article in the book you are given, titled `SOP: <task name>`. Do not create shelves or books, and do not publish.
