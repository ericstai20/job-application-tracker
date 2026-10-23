# Learning Log

## Day 1

Set up the project: virtual environment, dependencies, starter files, and Git.

**Virtual environment (`.venv`)** - A separate set of Python packages just for this project, so versions don't clash with other projects. Activated with `.\.venv\Scripts\Activate.ps1`; `(.venv)` in the prompt means it's on.

**requirements.txt** - The list of packages the project needs. Anyone can install them with `pip install -r requirements.txt`.

**.gitignore** - Files Git should never save: `.venv/` (can be rebuilt), `.env` (secret API key), `__pycache__/` (auto-generated), `*.db` (local data), `.vscode/` (my editor settings).

**Running the app** - `streamlit run app.py` starts a local web server at `http://localhost:8501`. `localhost` = my own computer, `8501` = the port. `Ctrl + C` stops it.

**Git basics**
- `git init` - start tracking the folder (creates the hidden `.git` folder).
- `git status` - see what Git notices (red = not staged, green = staged).
- `git add .` - stage files (put them in the box).
- `git commit -m "message"` - save a snapshot (seal the box with a label).
- `git config --global user.name / user.email` - one-time setup so commits have an author.

**Mistakes I fixed**
- Two commands on one line -> run each command separately.
- Typed `gigit` -> PowerShell's "not recognized" error usually means a typo.
- `LF will be replaced by CRLF` warnings are harmless (Windows line endings).
