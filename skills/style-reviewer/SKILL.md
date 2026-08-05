---
name: style-reviewer
description: Check an article against the house style guide and glossary, then save a corrected copy next to it.
---

# Style and terminology reviewer

Check one article against the house style guide and glossary, and save a corrected copy so a person can compare the two.

## When to use

You are given the ID of an article to review. Replace `references/style-guide.md` and `references/glossary.csv` with your own house rules; the ones here are examples.

## Steps

1. Read the article.
2. Check it against every rule in `references/style-guide.md`.
3. Check every term against `references/glossary.csv`. The columns are `use`, `instead_of` and `note`: wherever the text says `instead_of`, write `use`.
4. Fix everything that breaks a rule or the glossary, including whole sentences: for example, rewrite "The user should click Save" as "Select **Save**". Keep everything else exactly as it is: facts, numbers, steps, order, links and images.
5. Save the corrected text as a new article in the same book. Title it with the corrected title, followed by ` (reviewed)`.
6. In your final message, list each change you made and the rule or glossary entry behind it.

## Rules

- Never change the original article.
- Never add information that isn't in the original.
- If a sentence is unclear but doesn't break a rule, leave it and mention it in your final message.
- Do not publish.
