# Git Workflow Rules

## Commit Messages
All commits MUST follow Conventional Commits format:
- `feat:` for new features
- `fix:` for bug fixes
- `chore:` for maintenance tasks
- `docs:` for documentation changes
- `refactor:` for code restructuring without behavior change
- `test:` for adding or updating tests
- `ci:` for CI/CD changes

Example: `feat(api): add PDF upload endpoint`

## Branch Naming
Branches MUST follow the pattern: `<type>/<short-description>`
- `feat/user-auth`
- `fix/login-redirect`
- `chore/deps-update`
- `docs/readme-setup`

## Protected Branches
- `main` and `develop` are **protected** — never push directly
- All changes go through Pull Requests with at least 1 approval
- CI must pass before merge

## Rebase vs Merge Policy
- **Feature branches**: rebase on `main` before opening a PR
- **Merge into main**: use `--no-ff` (no fast-forward) to preserve history
- **Never rebase shared branches** — only rebase your own local branches

## Before Opening a PR
1. Run `git fetch origin && git rebase -i origin/main` to clean up commits
2. Squash WIP / fixup commits into meaningful atomic commits
3. Ensure all tests pass locally
4. Use `git push --force-with-lease` if you need to force push your branch

## Git Workflow Master Skill
When any Git-related task arises (branching, committing, conflicts, CI, recovery),
activate the **git-workflow-master** skill located at `.agents/skills/git-workflow-master/SKILL.md`.
