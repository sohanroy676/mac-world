# Git Workflow

- `main` is frozen. Never commit to, merge into, or push `main`.
- `dev` is the long-lived integration branch (created from `main`, tracks `origin/dev`).
- Create a branch from `dev` for each piece of work: `feature/short-name`, `fix/short-name`, `docs/short-name`.
- Commit there with Conventional Commits, staging specific files.
- When the work is validated, merge into `dev` with `git merge --no-ff`, then push both the feature branch and `dev`.
  Standing user approval covers these merges and pushes; do not wait to be asked.
- Ask first before: force-push, rebase of pushed history, `reset --hard`, deleting branches or tags, creating tags,
  and anything that touches `main`.
- Never commit build outputs, venvs, `results/`, `wandb/`, `CW_data*`, `cw.csv`, pcaps or secrets.
