# Scripts

These scripts manage the nested package repositories inside `micro-dev` and are used to prepare, review, merge, and clean releases for all Micro packages listed in [`repository.json`](../repository.json).

## Prerequisites

- Run all commands from the `micro-dev` repository root.
- Install Python dependencies with `make venv`.
- Install GitHub CLI (`gh`) and make sure `gh auth status` succeeds.
- Make sure every package listed in `repository.json` has been initialized with `make init`.
- Know the two branches you want to use:
  - `BASE_BRANCH`: the branch packages are released onto, for example `2.x`
  - `RELEASE_BRANCH`: the release branch or PR head, for example `release/2026-03-19`

## Initialize Package Repositories

Initialize all nested package repositories:

```bash
make init
```

This creates or updates git metadata in the package directories and switches each package to the current monorepo branch when possible.

If the current monorepo branch does not exist in the package repositories, you can create the missing branch from an existing remote branch:

```bash
make init INIT_ARGS="--from-branch=2.x"
```

Current init fallback behavior:

- The target branch defaults to the current monorepo branch.
- If that target branch already exists in a package repository, init checks it out.
- If it does not exist and `--from-branch=<branch-name>` is provided, init creates the target branch from `origin/<branch-name>`.
- If the fallback branch does not exist remotely, the package is reported as blocked.

If you also want newly created missing branches to be pushed to GitHub, use the opt-in push flag:

```bash
make init INIT_ARGS="--from-branch=2.x --push-missing-branches"
```

Equivalent direct script usage:

```bash
python ./scripts/init.py --config=./repository.json --from-branch=2.x
python ./scripts/init.py --config=./repository.json --from-branch=2.x --push-missing-branches
```

If you want to remove that nested git metadata and return to a clean non-initialized state:

```bash
make clean
```

`make clean` removes the package-level `.git` metadata, removes the Python virtualenv, and deletes Python cache files.

## Release Flow

Use the Make targets below. They are thin wrappers around `scripts/release.py`.

### 1. Inspect Current State

Show the current per-package release status without mutating anything:

```bash
make release-status BASE_BRANCH=2.x RELEASE_BRANCH=release/2026-03-19 RELEASE_NAME=v2.4.0
```

This reports whether each package is blocked, already released, has an open PR, or would create a missing release.

### 2. Preview the Exact Actions

Show what the release script would do without mutating git or GitHub:

```bash
make release-dry-run BASE_BRANCH=2.x RELEASE_BRANCH=release/2026-03-19 RELEASE_NAME=v2.4.0
```

Use this before every real run. It shows the action for each package, for example:

- `would merge PR ... and create release ...`
- `would create missing release ...`
- `noop: merged PR already released ...`
- `blocked: remote base branch ... is missing`
- `blocked: local changes or untracked files are present`

### 3. Prepare the Release

Prepare all package release branches and open PRs:

```bash
make release-prepare BASE_BRANCH=2.x RELEASE_BRANCH=release/2026-03-19 RELEASE_NAME=v2.4.0
```

Current prepare-mode behavior:

- It requires the remote `BASE_BRANCH` and `RELEASE_BRANCH` checks to pass for all packages before processing starts.
- It fails early if any package repository has local tracked changes or untracked files.
- If package processing succeeds, it commits with the message `Update <RELEASE_NAME> for <package>`, pushes the release branch, and opens a PR when one is not already open.

### 4. Merge PRs and Publish Releases

Merge the open release PRs and create GitHub releases for all packages:

```bash
make release-merge BASE_BRANCH=2.x RELEASE_BRANCH=release/2026-03-19 RELEASE_NAME=v2.4.0
```

Current merge-mode behavior:

- It verifies `gh` is installed and authenticated before starting.
- It verifies remote branch state before package processing starts.
- It fetches tags before computing the next package version.
- It merges open PRs with squash merge.
- It creates GitHub release notes from commit subjects since the previous release tag.
- If a PR was already merged but the release was not created, it can recover by creating the missing release.

### 5. Optional Merge Variants

Merge PRs but skip creating GitHub releases:

```bash
python ./scripts/release.py --config=./repository.json --merge --no-release --base-branch 2.x --release-branch release/2026-03-19 v2.4.0
```

Preview merge behavior without mutating anything:

```bash
python ./scripts/release.py --config=./repository.json --merge --dry-run --base-branch 2.x --release-branch release/2026-03-19 v2.4.0
```

## Script Help

Every script in this folder supports `--help`, for example:

```bash
python ./scripts/init.py --help
python ./scripts/release.py --help
python ./scripts/clean.py --help
```

## Recommended Operator Sequence

Use this order for a full release:

1. `make init`
2. `make release-status BASE_BRANCH=... RELEASE_BRANCH=... RELEASE_NAME=...`
3. `make release-dry-run BASE_BRANCH=... RELEASE_BRANCH=... RELEASE_NAME=...`
4. `make release-prepare BASE_BRANCH=... RELEASE_BRANCH=... RELEASE_NAME=...`
5. Review the created PRs in GitHub
6. `make release-merge BASE_BRANCH=... RELEASE_BRANCH=... RELEASE_NAME=...`

If you need to undo the nested package initialization afterward:

```bash
make clean
```
