---
name: gonzo-site-from-scaffold
description: Create a new website repository from the Gonzo Copier scaffold on GitHub. Use when the user wants a fresh Gonzo website generated from the canonical template, with metadata and feature choices applied and the resulting project initialized and verified.
---

# Gonzo Site From Scaffold

Use this skill when the user wants a brand-new website repo based on the Gonzo scaffold, not edits to an existing app.

## Workflow

1. Decide the destination directory and project metadata.
2. Run `scripts/create_site.py` against the canonical scaffold GitHub repo.
3. Use the default pinned scaffold tag unless the user explicitly asks for another ref.
4. After generation:
   - copy `.env.example` to `.env` if missing
   - initialize git
   - create an initial commit so `/manifest.json` has git-derived timestamps
   - run `uv sync`
   - run `uv run python manage.py check`
   - run `uv run pytest`

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
- The skill should treat scaffold version changes as intentional updates, not silent defaults.
