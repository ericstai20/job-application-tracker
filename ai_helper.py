# ai_helper.py
# Responsible for talking to the Anthropic (Claude) API: loading the
# API key from the .env file and sending requests for AI features,
# such as summarizing job descriptions or drafting follow-up notes.
# Keeping AI code here keeps it separate from the UI and the database.

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


def draft_cover_letter(background, company, role, job_posting):
    """Ask Claude to adapt the example cover letter for one job.
    Returns the letter as text."""
    client = anthropic.Anthropic()
    # Claude can't see my files or remember earlier requests, so
    # everything it needs goes into this one message.
    message = (
        f"My background:\n\n{background}\n\n"
        f"Adapt my example cover letter for the {role} role at {company}.\n\n"
        f"The job posting:\n\n{job_posting}"
    )
    # Turn the library's errors into plain-English AIErrors, most
    # specific first, so app.py doesn't need to know about them.
    try:
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=COVER_LETTER_INSTRUCTIONS,
            messages=[{"role": "user", "content": message}],
            # How hard Claude thinks. "medium" is plenty for a letter.
            output_config={"effort": "medium"},
            # If Claude's safety checks wrongly decline the request, let
            # another Claude model try instead of giving up.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
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
        raise AIError("Claude declined to write this letter.")
    # The reply is a list of blocks; the letter is in the text blocks.
    return "".join(
        block.text for block in response.content if block.type == "text"
    )
