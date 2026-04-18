---
name: gonzo-site-from-scaffold
description: Create or extend a website based on the Gonzo Copier scaffold on GitHub. Use when the user wants a fresh Gonzo website generated from the canonical template, or wants to iterate on a site that follows this baseline: Django, SQLite, optional Google OAuth, sprync-based Sprite sync, and a shared visual component library.
---

# Gonzo Site From Scaffold

Use this skill when the user wants a brand-new website repo based on the Gonzo scaffold, or when the current repo already follows that scaffold and should be extended consistently.

## Baseline Assumptions

Scaffolded sites use this baseline:

- Django application with stable internal modules `config` and `website`
- SQLite database by default
- optional Google OAuth gate for Google Workspace sign-in
- `scripts/sprync.py` for Sprite setup and deploy sync, including SSH-based push/pull workflow to and from a Sprite
- `/manifest.json` provenance contract
- vendored OpenSAFELY assets and a component-driven UI shell
- `slippers` template components

Treat this as the default mental model when working on one of these sites.

## Component Rule

Always inspect the existing component system before inventing new page markup.

- Prefer existing Slippers/OpenSAFELY components and local wrapped components
- Consult the component gallery and component templates before adding new UI
- Only add a new bespoke component when the existing library genuinely does not cover the need

For page changes, the component library is the first place to look, not raw handwritten HTML.

## Environment Detection

This skill may run:

- on a local machine
- inside a Sprite

Detect Sprite execution by checking for `/.sprite`.

If `/.sprite` exists:

- assume the agent is running inside the Sprite itself
- prefer Sprite-aware workflows where relevant
- use any available sprite-specific skills or tooling in the environment
- remember that local-machine assumptions about SSH setup or host-side file layout may not apply

If `/.sprite` does not exist, assume normal local development unless the repo state shows otherwise.

## Workflow

1. Decide whether the task is:
   - generating a new site from the scaffold, or
   - iterating on an existing scaffolded site
2. If generating a new site, run `scripts/create_site.py` against the canonical scaffold GitHub repo.
3. Use the default pinned scaffold tag unless the user explicitly asks for another ref.
4. After generation:
   - copy `.env.example` to `.env` if missing
   - initialize git
   - create an initial commit so `/manifest.json` has git-derived timestamps
   - run `uv sync`
   - run `uv run python manage.py check`
   - run `uv run pytest`
5. If iterating on an existing site:
   - inspect current templates and components first
   - preserve the Django/Sprite/provenance conventions already established by the scaffold

## Default Scaffold

- Template source: `https://github.com/sebbacon/gonzo.git`
- Default ref: `v0.1.0`

Override with `--template-source`, `--vcs-ref`, or env vars only for development or explicit user requests.

## Command

```bash
python scripts/create_site.py \
  --destination /path/to/new-site \
  --project-slug my-site \
  --site-name "My Site"
```

Useful flags:

- `--github-owner`
- `--github-repo-name`
- `--site-visibility`
- `--sprite-name`
- `--include-google-auth true|false`
- `--google-hosted-domain`
- `--include-ui-gallery true|false`
- `--template-source`
- `--vcs-ref`
- `--skip-verify`
- `--skip-git-init`
- `--skip-copy-env`

## Notes

- Prefer the pinned scaffold tag for normal use.
- If the user wants to develop the scaffold and skill together, point `--template-source` at a local checkout and use `--vcs-ref HEAD`.
- Treat scaffold version changes as intentional updates, not silent defaults.
- When changing frontend pages in scaffolded sites, consult the component system before designing new structures from scratch.
