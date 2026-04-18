#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import UTC, datetime
import os
from pathlib import Path
import shutil
import subprocess
import sys


DEFAULT_TEMPLATE_SOURCE = "https://github.com/sebbacon/gonzo.git"
DEFAULT_VCS_REF = "v0.1.0"
FALLBACK_GIT_NAME = "Codex Scaffold"
FALLBACK_GIT_EMAIL = "codex-scaffold@example.invalid"


def str_bool(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in {"true", "false"}:
        raise argparse.ArgumentTypeError("expected true or false")
    return normalized


def run(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    cp = subprocess.run(cmd, cwd=cwd, env=env, text=True)
    if cp.returncode != 0:
        raise SystemExit(cp.returncode)


def capture(cmd: list[str], *, cwd: Path | None = None) -> str:
    cp = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if cp.returncode != 0:
        return ""
    return cp.stdout.strip()


def copy_env_file(destination: Path) -> None:
    env_example = destination / ".env.example"
    env_file = destination / ".env"
    if env_example.exists() and not env_file.exists():
        shutil.copyfile(env_example, env_file)


def ensure_initial_commit(destination: Path) -> None:
    run(["git", "init", "-b", "main"], cwd=destination)
    run(["git", "add", "."], cwd=destination)

    author_name = capture(["git", "config", "--get", "user.name"], cwd=destination)
    author_email = capture(["git", "config", "--get", "user.email"], cwd=destination)
    env = os.environ.copy()
    env.setdefault("GIT_AUTHOR_NAME", author_name or FALLBACK_GIT_NAME)
    env.setdefault("GIT_AUTHOR_EMAIL", author_email or FALLBACK_GIT_EMAIL)
    env.setdefault("GIT_COMMITTER_NAME", env["GIT_AUTHOR_NAME"])
    env.setdefault("GIT_COMMITTER_EMAIL", env["GIT_AUTHOR_EMAIL"])

    run(["git", "commit", "-m", "Initial scaffold"], cwd=destination, env=env)


def verify_project(destination: Path) -> None:
    run(["uv", "sync"], cwd=destination)
    run(["uv", "run", "python", "manage.py", "check"], cwd=destination)
    run(["uv", "run", "pytest"], cwd=destination)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", required=True)
    parser.add_argument("--template-source")
    parser.add_argument("--vcs-ref")
    parser.add_argument("--project-slug", required=True)
    parser.add_argument("--site-name", required=True)
    parser.add_argument("--github-owner", default="example")
    parser.add_argument("--github-repo-name")
    parser.add_argument("--site-visibility", default="private", choices=["private", "public"])
    parser.add_argument("--sprite-name")
    parser.add_argument("--include-google-auth", type=str_bool, default="true")
    parser.add_argument("--google-hosted-domain", default="thedatalab.org")
    parser.add_argument("--include-ui-gallery", type=str_bool, default="true")
    parser.add_argument("--skip-git-init", action="store_true")
    parser.add_argument("--skip-copy-env", action="store_true")
    parser.add_argument("--skip-verify", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    destination = Path(args.destination).expanduser().resolve()
    template_source = (
        args.template_source
        or os.environ.get("GONZO_TEMPLATE_SOURCE")
        or DEFAULT_TEMPLATE_SOURCE
    )
    vcs_ref = args.vcs_ref or os.environ.get("GONZO_TEMPLATE_REF") or DEFAULT_VCS_REF
    github_repo_name = args.github_repo_name or args.project_slug
    sprite_name = args.sprite_name or args.project_slug

    copier_cmd = [
        "uvx",
        "--from",
        "copier",
        "copier",
        "copy",
        "--trust",
        "--defaults",
        "--vcs-ref",
        vcs_ref,
        "-d",
        f"project_slug={args.project_slug}",
        "-d",
        f"site_name={args.site_name}",
        "-d",
        f"github_owner={args.github_owner}",
        "-d",
        f"github_repo_name={github_repo_name}",
        "-d",
        f"site_visibility={args.site_visibility}",
        "-d",
        f"sprite_name={sprite_name}",
        "-d",
        f"include_google_auth={args.include_google_auth}",
        "-d",
        f"google_hosted_domain={args.google_hosted_domain}",
        "-d",
        f"include_ui_gallery={args.include_ui_gallery}",
        template_source,
        str(destination),
    ]
    run(copier_cmd)

    if not args.skip_copy_env:
        copy_env_file(destination)

    if not args.skip_git_init:
        ensure_initial_commit(destination)

    if not args.skip_verify:
        verify_project(destination)

    print(destination)
    print(f"template={template_source}@{vcs_ref}")
    print(f"generated_at={datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
