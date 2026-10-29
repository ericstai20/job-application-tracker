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

## Day 4

Added a "Show" dropdown that filters the applications table by status.

**Filtering in SQL vs Python** - Could get every row and filter in Python, but asking the database for only the matching rows (`WHERE`) is how real apps handle lots of data.

**SQL I used**
- `SELECT * FROM applications WHERE status = ? ORDER BY date_applied DESC` - only the rows with that status, newest first.
- Clause order matters: `SELECT -> FROM -> WHERE -> ORDER BY` (pick the table, filter, then sort).

**`WHERE` again** - Same idea as Day 3, but for reading instead of changing rows.

**Default parameters** - `def get_applications(status=None)` makes `status` optional. Calling it with no argument uses `None`, so old code like the Update section's `get_applications()` still works and still gets every application.

**Truthiness** - `if status:` is false when `status` is `None` (or empty), true when it's something like `"Applied"`.

**Every branch must set the variable** - Both the `if` and the `else` set `rows`, otherwise the `return` line fails. VS Code warned me with `"rows" is not defined`.

**`if` / `elif` / `else`** - `elif` = "else if". Used it to show a different empty message: "No applications yet" vs "No applications with status Offer".

**Joining lists** - `["All"] + database.STATUSES` makes one list. Reusing `STATUSES` means a new status shows up in the filter automatically.

**Triple quotes `"""`** - Let a string span several lines, which keeps longer SQL readable.

## Day 5

Added a summary row of number tiles: Total, plus one tile per status.

**Counting in SQL vs Python** - Could loop through every row in Python, but letting the database count is faster with lots of data.

**SQL I used**
- `SELECT status, COUNT(*) FROM applications GROUP BY status` - `GROUP BY` sorts rows into piles by status, `COUNT(*)` counts each pile. Returns one row per pile, like `("Applied", 2)`.

**The missing-pile catch** - A status with 0 applications has no pile, so it doesn't come back at all. Fixed by starting every status at 0 in Python, then overwriting with the real counts.

**Dictionaries** - `{}` is an empty dictionary: labels with values, like `"Applied" -> 2`. `counts[status] = 0` sets a value. `.values()` gives just the values, `.items()` gives label/value pairs.

**Tuple unpacking** - `for status, count in rows:` splits each `("Applied", 2)` into two variables at once.

**Streamlit layout** - `st.columns(5)` makes side-by-side columns. `st.metric(label, number)` draws a number tile.

**Built-ins I used**
- `sum(...)` - adds up numbers.
- `len(...)` - how many items.
- `columns[1:]` - a slice: everything except the first item.
- `zip(a, b)` - like a zipper, pairs up two lists item by item.

**Order matters (third time!)** - The summary goes below the Add and Update sections, so the numbers are drawn after any change and are always current.

## Day 6

Split the page into three tabs: Overview (summary + table), Add, and Update / Delete. The data I look at most is now the first thing I see, without scrolling past the form.

**Layout options I compared**
- Expanders (`st.expander`) - fold a section up until clicked. Smallest change.
- Tabs (`st.tabs`) - one page, several labeled sections. Picked this one.
- Sidebar (`st.sidebar`) - a panel on the left. Too narrow for the form.
- Multipage app - one `.py` file per page. Too much for an app this size.

**Creating tabs** - `overview_tab, add_tab, manage_tab = st.tabs(["Overview", "Add", "Update / Delete"])`. The first label is the tab that's open when the app starts. Three names on the left is unpacking again (like Day 5), one tab per name.

**`with` blocks** - `with add_tab:` means "put everything indented under here in this tab". That's why most of `app.py` moved one indent to the right; the code inside didn't change.

**Tabs only hide things** - Streamlit still runs every tab's code, top to bottom, on every click. Tabs just decide what's visible.

**Order matters (fourth time!)** - Overview is first on screen but last in the file. Add and Update / Delete run first, so the table and tiles are drawn after any change and are always current. File order and screen order don't have to match.

**Empty tabs look broken** - The Update / Delete tab showed nothing when there were no applications. Added an `else` with `st.info("No applications yet. Add one in the Add tab.")`.

**Testing without clicking** - Streamlit's `AppTest` runs the app without a browser and can check it for errors, list the tabs and read the tile values.

## Day 7

Replaced "Update status" with a full edit form, so every field of an application can be changed, not just its status. Renamed the tab to "Edit / Delete".

**SQL I used**
- `UPDATE applications SET company = ?, role = ?, ... WHERE id = ?` - change several columns in one row at once. Same `WHERE` safety catch as Day 3.

**Removed `update_status`** - The new `update_application` changes status too, so nothing used the old function anymore. Unused code is clutter, and Git still has the old version if I ever need it.

**Pre-filled forms** - Each field starts on the application's current value, like `st.text_input("Company *", selected["company"])`.

**Translating between the database and the form**
- Dates are stored as text, but `st.date_input` needs a real date. `date.fromisoformat("2026-10-01")` turns text into a date; `.isoformat()` turns it back.
- Empty fields are `None` in the database, but text boxes need `""`. `selected["location"] or ""` means "the location, or an empty string if there isn't one".

**The jumping dropdown bug** - After saving an edit, the next click made the "Application" dropdown jump back to the first application. Easy to end up editing the wrong one without noticing.
- Why: the dropdown held whole application dictionaries, and Streamlit remembers my pick by its value. After editing the role, the remembered dictionary (with the old role) didn't match any option anymore, so Streamlit fell back to the first one.
- First try: giving the dropdown a `key`. Didn't fix it, because the value still didn't match.
- Real fix: the dropdown holds only ids, which never change, and looks up the full application from the id. Like a coat check: keep the ticket number, get the coat back with `by_id[ticket]`.

**Dictionary comprehension** - `{application["id"]: application for application in applications}` builds a dictionary in one line: "for each application, file it under its id".

**`lambda`** - A tiny unnamed function written in one line. `format_func=lambda app_id: describe(by_id[app_id])` turns an id into a readable label.

**Testing found the bug** - The bug only showed up when testing several steps in a row (save, then click again). Testing one action at a time wouldn't have caught it.

## Day 8

Added Claude to the app: a "Cover Letter" tab that adapts my example cover letter for each job posting.

**Picking the feature** - Thought about which part of job searching takes the most time. I tailor my cover letter for every application, so that's where Claude helps most.

**What an API is** - A way for one program to talk to another. My app sends a message to Anthropic's servers and gets Claude's reply back. Like a restaurant: my app is the customer, the API is the waiter, Claude is the kitchen.

**Claude Pro vs the API** - Billed separately. Pro is for me chatting with Claude; the API is for programs, pay-as-you-go with credits. Like a gym membership vs the gym's vending machine. Each letter costs a few cents.

**API key** - The password that proves requests come from me. Made in the Anthropic Console, shown only once (if lost, make a new one). Lives in `.env`, which `.gitignore` keeps off GitHub. Never paste it anywhere public.

**`load_dotenv()`** - Copies the key from `.env` into the environment, where the `anthropic` library looks for it. `.env` is only read at startup, so restart the app after changing it.

**Claude can't see my files** - My code reads `background.md` and sends its text in the request. Claude also doesn't remember earlier requests, so every request sends everything it needs, like mailing a packet.

**System prompt vs message**
- System prompt (`COVER_LETTER_INSTRUCTIONS`) - the standing rules, the same every time.
- Message - this job's packet: my background, the company, the role, and the posting.

**Prompt design** - The instructions decide the result. "Adapt" means keep my structure and wording and change only what's needed for the new job. "Only use facts from the background, never invent" stops Claude making up experience. Changing these words is how I tune the letters.

**Keeping personal info private** - `background.md` holds my resume and example letter, so it's in `.gitignore` too. Checked with `git check-ignore background.md`.

**Custom errors** - `class AIError(Exception)` is my own error type. `ai_helper.py` turns the library's technical errors into plain-English `AIError`s, so `app.py` only catches one kind of error.

**Most specific error first** - `except` blocks are checked top to bottom, so specific ones (`AuthenticationError`, `RateLimitError`) go before the general `APIStatusError`. Otherwise the general one would catch everything first.

**Separation of concerns (again)** - `ai_helper.py` talks to Claude, `database.py` talks to SQLite, `app.py` only draws the page.

**Streamlit things I used**
- `st.spinner("...")` - a loading animation while Claude writes.
- `st.session_state` - Streamlit's memory between reruns. Without it, the draft would vanish on the next click, since every click re-runs `app.py`.

**Testing without spending money**
- No key / unfilled `background.md` / empty posting - checked each shows the right message.
- A fake key - a real request that gets rejected, to check the friendly error.
- A fake Claude - a stand-in function that returns a pretend letter, to check the draft shows and stays.
- Listing models - a free request that proves the real key works.

**Model choice** - The app uses Claude Opus 5.5. Claude Haiku 5.5 is about 40x cheaper but writes a little less polished. Changing `MODEL` in `ai_helper.py` switches between them.

**Read before sending** - The draft is a starting point. Always check it for anything that isn't true.

## Day 9

Added "Fill in from a job posting" to the Add tab: paste a link and Claude fills in the company, role, location and notes.

**Picking an approach** - Three ways to get the posting's text:
- Claude fetches the link itself (web fetch tool). Least code.
- My Python code downloads the page (`requests` + `BeautifulSoup`). More code, and many job sites block scripts or build the page with JavaScript, so it often gets back an almost empty page.
- I paste the text. Always works, but it's a manual step.
- Picked Claude fetching, with pasting as a backup for sites that block it.

**Tools** - An ability Claude can choose to use during a request. `web_fetch` runs on Anthropic's servers, so my app has no scraping code. `max_uses: 1` stops it fetching more than one page, which keeps the cost down.

**Structured outputs** - A schema (`JOB_DETAILS_SCHEMA`) describes the exact shape the reply must have. Like handing someone a printed form instead of asking for a paragraph. Claude always replies in that shape, as JSON, and `json.loads` turns it into a Python dict.

**JSON** - A text format for data that looks a lot like a Python dict: `{"company": "Acme", "found": true}`.

**The `found` field** - Claude replies in the schema's shape even when the page didn't load, so I added a yes/no field for "did you find a job posting?". When it's false, Claude explains why in `notes`, and the app shows that message.

**`pause_turn`** - Fetching can take Claude several steps, and it can pause partway. The loop sends its progress back so it can carry on, and gives up after 3 rounds so it can't run forever.

**`for ... else`** - The `else` on a `for` loop runs only if the loop finished without hitting `break`. Here, that means Claude never stopped pausing, so it raises an error.

**Refactoring** - Changing how code is organized without changing what it does. Both Claude features needed the same error handling, so I moved it into one shared function, `ask_claude`, instead of copying it.

**`**request`** - Lets a function take any keyword arguments and pass them along. `ask_claude(system=..., messages=...)` collects them into a dict, and `**request` unpacks them into the real API call.

**Filling in a form from code**
- A form only sends its values when its own submit button is pressed, so the "Fill in the form" button has to sit outside it, above.
- Each form box got a `key`, like `key="add_company"`. Setting `st.session_state["add_company"]` before the box is drawn makes it start with that value.
- That only works because the fill section is above the form. Streamlit won't let you change a box after it's already been drawn in the same run.

**Testing with real calls** - Tried pasted text, a careers page that lists many jobs, and a broken link. The careers page was a good catch: Claude saw it listed 679 jobs rather than one and said so, instead of making something up.

**Always check before saving** - Claude fills in the form, but nothing is saved until I review it and click "Add application".
