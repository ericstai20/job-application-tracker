# ai_helper.py
# Responsible for talking to the Anthropic (Claude) API: loading the
# API key from the .env file and sending requests for AI features,
# such as summarizing job descriptions or drafting follow-up notes.
# Keeping AI code here keeps it separate from the UI and the database.

import json
import os

import anthropic
from dotenv import load_dotenv

# Copy ANTHROPIC_API_KEY from the .env file into the environment,
# where the anthropic library looks for it.
load_dotenv()

MODEL = "claude-opus-5-5"

# My resume and an example cover letter. It's listed in .gitignore
# so personal details never go to GitHub.
BACKGROUND_PATH = "background.md"

# background.md starts with this text. If it's still there, the file
# hasn't been filled in yet.
PLACEHOLDER = "PASTE"

# Instructions Claude follows for every cover letter. "Adapt" means
# keep my letter and change as little as possible.
COVER_LETTER_INSTRUCTIONS = """\
You adapt the user's example cover letter for a new job application.

Keep the example letter's structure, tone and wording. Change only what
has to change for the new job: the company name, the role, and the
sentences about why they want this job or which skills they highlight.
Point those sentences at what the job posting asks for.

Use only facts found in the user's background (their experience section
and example letter). Never invent experience, skills, numbers or
projects. If the posting asks for something the background doesn't
cover, leave it out rather than claiming it.

Reply with the finished cover letter only: no introduction, notes or
explanation before or after it."""

# Instructions for pulling application details out of a job posting.
EXTRACT_INSTRUCTIONS = """\
You read a job posting and pull out details for a job application tracker.

If you're given a link, fetch it with the web_fetch tool. If the page
can't be fetched, needs a login, or isn't a single job posting, set
found to false, explain why in one sentence in notes, and leave the
other fields empty.

Copy the company name and job title as the posting writes them. For
location, give the city and region, or "Remote" or "Hybrid" if the
posting says so. For notes, write a few short lines covering the
salary or pay range, the main requirements, and any application
deadline, leaving out anything the posting doesn't mention.

Use only what the posting says. If a detail isn't there, leave that
field as an empty string rather than guessing."""

# The shape Claude's reply must have. Structured outputs guarantee the
# reply is JSON with exactly these fields, so Python can read it safely.
JOB_DETAILS_SCHEMA = {
    "type": "object",
    "properties": {
        "found": {"type": "boolean"},
        "company": {"type": "string"},
        "role": {"type": "string"},
        "location": {"type": "string"},
        "notes": {"type": "string"},
    },
    "required": ["found", "company", "role", "location", "notes"],
    "additionalProperties": False,
}


class AIError(Exception):
    """A problem talking to Claude, with a message to show on the page."""


def has_api_key():
    """Return True if an API key was found in .env."""
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def load_background():
    """Return the text of background.md, or None if it's missing
    or hasn't been filled in yet."""
    if not os.path.exists(BACKGROUND_PATH):
        return None
    with open(BACKGROUND_PATH, encoding="utf-8") as file:
        background = file.read()
    if PLACEHOLDER in background:
        return None
    return background


def ask_claude(**request):
    """Send one request to Claude and return the response.
    Shared by every feature, so the error handling lives in one place."""
    client = anthropic.Anthropic()
    # Turn the library's errors into plain-English AIErrors, most
    # specific first, so app.py doesn't need to know about them.
    try:
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            # If Claude's safety checks wrongly decline the request, let
            # another Claude model try instead of giving up.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            **request,
        )
    except anthropic.AuthenticationError:
        raise AIError("Your API key was rejected. "
                      "Check ANTHROPIC_API_KEY in the .env file.")
    except anthropic.RateLimitError:
        raise AIError("Too many requests right now. Wait a minute and try again.")
    except anthropic.APIConnectionError:
        raise AIError("Couldn't reach Claude. Check your internet connection.")
    except anthropic.APIStatusError as error:
        # Covers everything else, such as running out of credits.
        raise AIError(f"Claude returned an error: {error.message}")

    if response.stop_reason == "refusal":
        raise AIError("Claude declined this request.")
    return response


def reply_text(response):
    """The reply is a list of blocks; join up the text ones."""
    return "".join(
        block.text for block in response.content if block.type == "text"
    )


def draft_cover_letter(background, company, role, job_posting):
    """Ask Claude to adapt the example cover letter for one job.
    Returns the letter as text."""
    # Claude can't see my files or remember earlier requests, so
    # everything it needs goes into this one message.
    message = (
        f"My background:\n\n{background}\n\n"
        f"Adapt my example cover letter for the {role} role at {company}.\n\n"
        f"The job posting:\n\n{job_posting}"
    )
    response = ask_claude(
        system=COVER_LETTER_INSTRUCTIONS,
        messages=[{"role": "user", "content": message}],
        # How hard Claude thinks. "medium" is plenty for a letter.
        output_config={"effort": "medium"},
    )
    return reply_text(response)


def extract_job_details(link="", posting_text=""):
    """Ask Claude for the company, role, location and notes of a job,
    from pasted posting text if there is any, otherwise from the link.
    Returns a dict with the schema's fields."""
    # Settings that only some requests need, added below.
    extra = {}
    if posting_text:
        # The text is already here, so Claude doesn't need to fetch anything.
        messages = [{"role": "user",
                     "content": f"The job posting:\n\n{posting_text}"}]
    else:
        messages = [{"role": "user", "content": f"The job posting: {link}"}]
        # web_fetch runs on Anthropic's servers: Claude downloads the page
        # itself, so this app doesn't need any scraping code. max_uses
        # stops it fetching more than one page.
        extra["tools"] = [{"type": "web_fetch_20260209", "name": "web_fetch",
                           "max_uses": 1}]

    # Fetching can take Claude several steps. If it pauses partway
    # ("pause_turn"), send its progress back so it can carry on.
    # The loop gives up after a few rounds so it can't run forever.
    for _ in range(3):
        response = ask_claude(
            system=EXTRACT_INSTRUCTIONS,
            messages=messages,
            **extra,
            # Reading a posting is simple, so "low" effort keeps it quick
            # and cheap.
            output_config={
                "effort": "low",
                "format": {"type": "json_schema", "schema": JOB_DETAILS_SCHEMA},
            },
        )
        if response.stop_reason != "pause_turn":
            break
        messages.append({"role": "assistant", "content": response.content})
    else:
        raise AIError("Claude took too long reading the page. "
                      "Try pasting the posting text instead.")

    # json.loads turns the JSON text into a Python dict.
    return json.loads(reply_text(response))
