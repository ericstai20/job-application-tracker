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
- Git = save points on my computer. GitHub = website that stores a copy online.
- `git remote add origin <url>` - connect my repo to GitHub. `git push` - upload my commits.

**Mistakes I fixed**
- Two commands on one line -> run each command separately.
- Typed `gigit` -> PowerShell's "not recognized" error usually means a typo.
- `LF will be replaced by CRLF` warnings are harmless (Windows line endings).

## Day 2

Built the database and connected it to the app. The app can now add and show applications.

**Database basics** - A table is like a spreadsheet: columns are fields (company, role...), rows are entries (one application). SQLite stores the whole database in one file, `applications.db`.

**My table** - `id` (filled in automatically), `company`, `role`, `status`, `date_applied` (required), `location`, `job_link`, `notes` (optional). Dates are stored as `YYYY-MM-DD` text so they sort correctly.

**Safety rules in the table**
- `NOT NULL` - the field is required.
- `CHECK` - status must be Applied, Interviewing, Offer, or Rejected. Tested it with "Aplied" and the database refused it.

**SQL I used**
- `CREATE TABLE` - make the table.
- `INSERT INTO` - add a row.
- `SELECT * FROM ... ORDER BY ... DESC` - get rows, newest first.

**`?` placeholders (parameterized queries)** - Values are passed separately from the SQL, so they're treated as data, never code. Prevents SQL injection and stops names like `McDonald's` from breaking the query.

**Separation of concerns** - `database.py` handles data, `app.py` handles the page. `app.py` never writes SQL itself.

**How Streamlit works** - Every click re-runs `app.py` from top to bottom, so order matters. A form waits until the submit button is clicked.

**Validation** - Check input before saving: company and role can't be empty, and status comes from a dropdown so it can't be misspelled.

**CRUD** - Create, Read, Update, Delete. Done: Create and Read. Next: Update and Delete.

## Day 3

Added Update and Delete. The app can now change an application's status and remove applications, so all four CRUD steps work.

**SQL I used**
- `UPDATE applications SET status = ? WHERE id = ?` - change one column in one row.
- `DELETE FROM applications WHERE id = ?` - remove one row.

**`WHERE` is the safety catch** - It picks which row to change, using the `id` column. Without `WHERE`, `UPDATE` changes every row and `DELETE` empties the whole table.

**One-item tuple `(app_id,)`** - Placeholder values must be a tuple. `(app_id)` is just `app_id` in brackets; the trailing comma is what makes it a tuple.

**`format_func`** - The dropdown holds whole application dictionaries, but `format_func` decides what's displayed ("Intern at Acme (2026-10-01)"). So the selected item still has its `id`.

**Widget `key`s** - Name tags Streamlit uses to tell widgets apart. Putting the id in the key (`status_3`) gives each application its own status dropdown.

**Order matters (again)** - The update section sits above the table. Since every click re-runs `app.py` top to bottom, the table is drawn after the change and shows the new data.

**Delete safety** - The Delete button stays disabled until a confirmation checkbox is ticked, because there's no undo.

**Manual testing** - Checked every path by hand: update, dropdown starting on the current status, the disabled delete button, and delete.

**Git** - `;` runs commands one after another in PowerShell, even if one fails. `&&` (only continue if it worked) doesn't exist in Windows PowerShell 5.1. In git output, `[main 58fb168]` means the commit worked and `old..new main -> main` means the push worked.

**CRUD** - Done: Create, Read, Update, Delete.
