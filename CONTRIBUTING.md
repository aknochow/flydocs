# Contributing

## Branch names

The branch name says what the change is. Use one conventional prefix and a short description:

| Prefix | Use for | Example |
|---|---|---|
| `feat/` | a new capability | `feat/readme-symlink-index` |
| `fix/` | a bugfix | `fix/spinner-no-wrap` |
| `docs/` | documentation only | `docs/branch-names` |
| `test/` | tests only | `test/readme-symlink` |
| `chore/` | tooling, dependencies, maintenance | `chore/lockfile` |
| `refactor/` | a behavior-preserving restructure | `refactor/theme-classes` |

Do not name a branch after the tool that opened it. `cursor/`, `claude/`, `codex/`, and any other agent or product prefix do not describe the change. Do not append a generated id (`-1bbb`, `-a491`, and the like) to force the name to be unique.

Cursor Cloud Agents default to `cursor/<name>-<id>` branches. This rule overrides that default.

Name the branch correctly before opening its pull request: renaming a branch closes any open pull request from it. If a pull request is already open on a misnamed branch, leave it and merge it as is. Do not open a second pull request for the same change.

## Commits

- Author and committer are `Adam Knochowski <aknochow@redhat.com>`.
- `Signed-off-by: Adam Knochowski <aknochow@redhat.com>` is the DCO trailer.
- AI assistance is `Assisted-by: Provider (model)`, using the tool and the user-facing model that did the work. Example: `Assisted-by: Cursor (Grok 4.7)`. Do not copy an attribution from another session, and do not use an internal model slug.
- Never add `Co-authored-by:`. It creates a phantom GitHub account.

Cloud agents must not use plain `git commit`. The platform defaults the author to `Cursor Agent <cursoragent@cursor.com>` and a commit-msg hook appends `Co-authored-by:`. Commit with `agent-commit.sh` from the private cloud-agent environment. It sets the owner, appends `Assisted-by` and `Signed-off-by`, signs with the owner SSH key, and skips those hooks.

```bash
/path/to/agent-commit.sh --model "Grok 4.7" -m "feat: summary

Body if needed." -- path/to/files
```

Pass `--model` as the user-facing name (`Grok 4.7`, `composer-2.5`), not an internal slug (`cursor-grok-4.6-high`).
