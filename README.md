# Docsie skill examples

Example skills and workflows for the [Docsie](https://www.docsie.io) Workflow Builder.

A skill is a folder with a `SKILL.md` file that tells an AI agent how to do one job your way, plus optional reference files and scripts. The same folder works in three places:

- in your coding agent, such as Claude Code, Codex or Cursor;
- in an **Apply a skill** step of a Docsie workflow, where a Docsie agent does the step following the skill;
- in a **Python** step, which runs the skill's script in Docsie's isolated Python runtime.

## Skills in this repository

| Skill | What it does | Workflow |
|---|---|---|
| [`sop-writer`](skills/sop-writer) | Turns rough notes into a standard operating procedure in a fixed house format | [`notes-to-sop.json`](workflows/notes-to-sop.json) |
| [`release-notes`](skills/release-notes) | Turns a changelog CSV into release notes, one article per product area. Includes a script for a Python step | [`release-notes.json`](workflows/release-notes.json), [`release-notes-python.json`](workflows/release-notes-python.json) |
| [`style-reviewer`](skills/style-reviewer) | Checks an article against a house style guide and glossary, and saves a corrected copy next to it | [`style-review.json`](workflows/style-review.json) |
| [`meeting-notes-to-kb`](skills/meeting-notes-to-kb) | Turns meeting notes or a transcript into short knowledge base articles, one per question | [`meeting-notes-to-kb.json`](workflows/meeting-notes-to-kb.json) |

The style guide, glossary and formats in `references/` are examples. Replace them with your own rules.

## Use a skill in Docsie

You need the Workflow Builder turned on for your organization and a workspace administrator role.

### 1. Import the skill

In Enterprise Portal, open **Skills & Agents → Skill packages**, choose **Import from GitHub/GitLab** and enter:

| Field | Value |
|---|---|
| Repository URL | `https://github.com/LikaloLLC/docsie-skills` |
| Branch or tag | `main` |
| Path | `skills/sop-writer` (or another skill folder) |
| Name | `SOP writer` |

Or ask your coding agent, once it's connected to Docsie through a builder connection:

> Import skills/sop-writer from https://github.com/LikaloLLC/docsie-skills, branch main, into Docsie as "SOP writer".

The agent calls `packages_import_git(url=..., ref="main", path="skills/sop-writer", name="SOP writer")`. Every import creates a fixed revision with its own ID.

### 2. Save the workflow

Each file in `workflows/` is a workflow definition. Replace `doc_YOUR_SHELF_ID` with the shelf to write into and `YOUR_..._REVISION_ID` with the revision ID from step 1. Then save it:

- ask your coding agent to save it with `recipes_save`, or
- build the same steps by hand in **Skills & Agents → Workflows → New workflow**, using an **Apply a skill** step.

### 3. Run it

Run the workflow from the **Workflows** tab, from your coding agent (`runs_start`), from a script, or from a trigger such as "structured import finished".

## Try a skill in Claude Code first

Copy a skill into your project and ask Claude Code to use it:

```bash
mkdir -p .claude/skills && cp -R skills/sop-writer .claude/skills/
```

> Use the sop-writer skill to turn these notes into an SOP for "Changing the label roll": ...

Adjust the wording until the result is right, then import the skill into Docsie.

## Write your own skill

1. Copy one of the folders in `skills/`.
2. Update the front matter. Docsie shows the `description` on the skill's card, and agents read it to decide when to use the skill.
3. Describe when to use the skill, the exact output format, the rules and where to save the result.
4. Put long material such as style guides, glossaries and examples in `references/`. An agent step reads `SKILL.md` and the text files in the package, up to 60,000 characters.
5. Never put credentials in a skill. Scripts get a short-lived token from the environment when they run.

A skill only guides an agent. Everything it does is checked against the permissions of the connection that runs the workflow.

## Python client

[`sdk/docsie_workflows.py`](sdk/docsie_workflows.py) is a one-file client for the Workflow Builder, using only the Python standard library. Scripts in Python steps can import it directly. To use it on your own machine or in CI:

```bash
export DOCSIE_WORKFLOW_URL=https://app.docsie.io/api_v2/003/workflows
export DOCSIE_WORKFLOW_TOKEN=wb_...   # from a builder connection; keep it in a secret store
PYTHONPATH=sdk python skills/release-notes/scripts/main.py inputs.json out/
```

## Documentation

See **AI Skills & Workflow Builder** in the [Docsie help center](https://help.docsie.io): what skills are, a step-by-step guide to creating and managing a skill from your coding agent, workflow recipes, triggers and the security model.

## License

[MIT](LICENSE)
