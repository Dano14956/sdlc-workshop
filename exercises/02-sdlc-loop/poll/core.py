"""Poll logic as plain functions over plain data.

Nothing here touches files or Streamlit. That's what makes it easy to test: every
function takes a poll and returns a value or a new poll.
"""

from __future__ import annotations

from datetime import datetime
from typing import TypedDict


class _PollFields(TypedDict):
    question: str
    options: list[str]
    votes: dict[str, int]


class Poll(_PollFields, total=False):
    created_at: str  # ISO 8601; missing on polls saved before it was recorded


def create_poll(question: str, options: list[str], created_at: datetime | None = None) -> Poll:
    """Return a new poll with zero votes. Surrounding whitespace and blank options are dropped.

    The caller passes `created_at` so this stays free of the clock.
    """
    question = question.strip()
    cleaned = [option.strip() for option in options if option.strip()]
    if not question:
        raise ValueError("A poll needs a question.")
    if len(cleaned) < 2:
        raise ValueError("A poll needs at least two options.")
    if len(set(cleaned)) != len(cleaned):
        raise ValueError("Options must be unique.")
    poll: Poll = {
        "question": question,
        "options": cleaned,
        "votes": {option: 0 for option in cleaned},
    }
    if created_at is not None:
        poll["created_at"] = created_at.isoformat()
    return poll


def vote(poll: Poll, option: str) -> Poll:
    """Return a copy of the poll with one more vote for `option`."""
    if option not in poll["votes"]:
        raise ValueError(f"Unknown option: {option!r}")
    votes = {**poll["votes"], option: poll["votes"][option] + 1}
    return {**poll, "votes": votes}


def tally(poll: Poll) -> list[tuple[str, int]]:
    """Vote counts per option, in the order the options were created."""
    return [(option, poll["votes"][option]) for option in poll["options"]]


def total_votes(poll: Poll) -> int:
    return sum(poll["votes"].values())


def created_label(poll: Poll) -> str | None:
    """'Created 7 Nov 2026, 09:05', or None when the poll has no creation time."""
    if "created_at" not in poll:
        return None
    created = datetime.fromisoformat(poll["created_at"])
    return f"Created {created.day} {created:%b %Y, %H:%M}"
