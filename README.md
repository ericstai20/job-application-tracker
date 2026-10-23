# Job Application Tracker

A web app for keeping track of job applications in one place, built with Python, Streamlit, and SQLite.

> **Status:** Work in progress. The project is set up and the app runs; features are being added step by step.

## Planned features

- Add job applications (company, role, date applied, link, notes)
- Track each application's status (Applied, Interviewing, Offer, Rejected)
- View, edit, and delete applications
- AI-assisted helpers using the Anthropic API (e.g. summarizing job descriptions)

## Tech stack

| Tool | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Builds the web interface in pure Python |
| SQLite | Lightweight database stored in a single local file |
| python-dotenv | Loads secret settings (like API keys) from a `.env` file |

## Project structure

```
job-application-tracker/
├── app.py            # Streamlit app (the user interface)
├── database.py       # All SQLite database code
├── ai_helper.py      # All Anthropic API code
├── requirements.txt  # Python packages the project needs
├── LEARNING.md       # Daily notes on what I learned building this
└── .gitignore        # Files Git should not track
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

4. **Create a `.env` file** in the project folder containing:
   ```
   ANTHROPIC_API_KEY=your-key-here
   ```
   (Only needed for the AI features.)

5. **Run the app**
   ```powershell
   streamlit run app.py
   ```
   It opens in your browser at `http://localhost:8501`.

## What I'm learning

I'm documenting the build in [LEARNING.md](LEARNING.md).
