# Job Application Tracker

A web app for keeping track of job applications in one place, built with Python, Streamlit, and SQLite. It uses Claude (Anthropic's AI) to adapt my cover letter for each job.

> **Status:** Work in progress. The core features work; more are being added step by step.

## Features

The app has four tabs:

- **Overview** - a summary of how many applications have each status, and a table of all applications that can be filtered by status
- **Add** - add an application (company, role, status, date applied, location, job link, notes)
- **Edit / Delete** - change any field of an application, or delete it (with a confirmation checkbox, since there's no undo)
- **Cover Letter** - pick an application, paste the job posting, and Claude adapts your example cover letter for that job

Statuses are Applied, Interviewing, Offer, and Rejected.

### How the cover letter feature works

You write your experience and an example cover letter once, in a file called `background.md`. For each job, Claude keeps your letter's structure and wording and only changes what's needed: the company, the role, and the sentences about why you want the job and which skills you highlight. It's told to use only facts from your background and never invent experience. The draft is a starting point, so always read it before sending.

## Tech stack

| Tool | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Builds the web interface in pure Python |
| SQLite | Lightweight database stored in a single local file |
| Anthropic API | Sends requests to Claude for the cover letter feature |
| python-dotenv | Loads secret settings (like API keys) from a `.env` file |

## Project structure

```
job-application-tracker/
├── app.py            # Streamlit app (the user interface)
├── database.py       # All SQLite database code
├── ai_helper.py      # All Anthropic API code, including the cover letter instructions
├── requirements.txt  # Python packages the project needs
├── LEARNING.md       # Daily notes on what I learned building this
├── .gitignore        # Files Git should not track
├── .env              # Your API key (you create this; not on GitHub)
└── background.md     # Your experience and example cover letter (you create this; not on GitHub)
```

## Getting started

These steps are for Windows PowerShell.

1. **Clone the repository**
   ```powershell
   git clone https://github.com/ericstai20/job-application-tracker.git
   cd job-application-tracker
   ```

2. **Create and activate a virtual environment**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```powershell
   streamlit run app.py
   ```
   It opens in your browser at `http://localhost:8501`. Everything except the Cover Letter tab works at this point.

## Setting up the cover letter feature

1. **Get an Anthropic API key.** Sign in to the [Anthropic Console](https://console.anthropic.com), add credits under Billing, then create a key under API Keys. The key is shown only once, so copy it right away.

   The API is billed separately from a Claude Pro subscription. Each cover letter draft costs a few cents.

2. **Create a `.env` file** in the project folder containing:
   ```
   ANTHROPIC_API_KEY=your-key-here
   ```
   No spaces or quotes. Never share this key or commit it.

3. **Create a `background.md` file** in the project folder with two sections:
   ```markdown
   # My experience
   (your resume text, or bullet points about your skills, projects, classes and jobs)

   # Example cover letter
   (a cover letter you've written before)
   ```
   The more real detail in the experience section, the better the letters, since Claude only uses facts from this file.

4. **Restart the app** (`Ctrl + C`, then `streamlit run app.py`). The `.env` file is only read at startup.

Both `.env` and `background.md` are listed in `.gitignore`, so your key and personal details never go to GitHub.

## What I'm learning

I'm documenting the build in [LEARNING.md](LEARNING.md).
