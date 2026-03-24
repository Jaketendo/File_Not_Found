"""Command-line interface helpers for the File Not Found demo.

This module handles all printing and user input for the terminal demo.
Display logic lives here so the engine stays focused on game rules.
"""

from __future__ import annotations

from models import CaseData, Document, GameState

# ── Visual constants ─────────────────────────────────────────────────────────

WIDTH = 70
DIVIDER = "─" * WIDTH
THICK_DIVIDER = "═" * WIDTH


def _header(title: str) -> None:
    """Print a centred section header."""
    print(f"\n{THICK_DIVIDER}")
    print(f"  {title.upper()}")
    print(THICK_DIVIDER)


def _section(title: str) -> None:
    """Print a lighter sub-section separator."""
    print(f"\n  ── {title} ──")


def _wrap(text: str, indent: str = "  ") -> None:
    """Word-wrap and print a block of text at WIDTH."""
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            print()
            continue
        line = indent
        for word in words:
            if len(line) + len(word) + 1 > WIDTH - 2:
                print(line)
                line = indent + word
            else:
                line += (" " if line.strip() else "") + word
        if line.strip():
            print(line)


# ── Display functions ─────────────────────────────────────────────────────────


def display_welcome(case_data: CaseData) -> None:
    """Print the game title and introduction text to the terminal."""
    print(f"\n{THICK_DIVIDER}")
    print(f"  FILE NOT FOUND  |  {case_data.title.upper()}")
    print(THICK_DIVIDER)
    print()
    _wrap(case_data.intro_text)
    print()
    print(f"  {DIVIDER}")
    print("  Type  help  at any time to see available commands.")
    print(f"  {DIVIDER}\n")


def display_help() -> None:
    """Print the available commands and what each one does."""
    _header("available commands")
    commands = [
        ("search  (s)",  "Search for documents using a keyword or phrase"),
        ("read    (r)",  "Read an unlocked document"),
        ("collect (c)",  "Collect evidence from an unlocked document"),
        ("status  (st)", "Show your current progress"),
        ("submit",       "Accuse a suspect and submit your evidence"),
        ("help    (h)",  "Show this help screen"),
        ("quit    (q)",  "Exit the game"),
    ]
    for cmd, desc in commands:
        print(f"  {cmd:<16}  {desc}")
    print()


def display_status(state: GameState) -> None:
    """Print a summary of the player's current progress."""
    _header("case status")

    _section("Available Keywords")
    available = sorted(state.available_keywords - state.used_keywords)
    if available:
        for kw in available:
            print(f"    * {kw}")
    else:
        print("    (no unused keywords remaining)")

    _section("Keywords Already Searched")
    if state.used_keywords:
        for kw in sorted(state.used_keywords):
            print(f"    - {kw}")
    else:
        print("    (none yet)")

    _section("Unlocked Documents")
    if state.unlocked_document_ids:
        for doc_id in sorted(state.unlocked_document_ids):
            doc = state.case_data.get_document_by_id(doc_id)
            label = doc.title if doc else doc_id
            print(f"    [{doc_id}]  {label}")
    else:
        print("    (no documents unlocked yet)")

    _section("Collected Evidence")
    if state.collected_evidence_ids:
        for ev_id in sorted(state.collected_evidence_ids):
            print(f"    [*] {ev_id}")
    else:
        print("    (no evidence collected yet)")

    print()


def display_search_results(documents: list[Document], message: str) -> None:
    """Print the outcome of a keyword search."""
    _header("search results")
    print(f"  {message}")
    if documents:
        print()
        print("  Newly unlocked documents:")
        for doc in documents:
            print(f"    [{doc.document_id}]  {doc.title}")
    print()


def display_document(document: Document) -> None:
    """Print the title, text, and evidence options for a document."""
    _header(document.title)
    print(f"  Document ID: {document.document_id}")
    print(f"  {DIVIDER}")
    print()
    _wrap(document.text)
    print()
    if document.evidence_items:
        _section("Evidence Items in This Document")
        for item in document.evidence_items:
            tag = "  [KEY EVIDENCE]" if item.is_key_evidence else ""
            print(f"    [{item.evidence_id}]  {item.label}{tag}")
            print(f"           {item.description}")
    else:
        print("  (no collectible evidence in this document)")
    print()


def display_submission_result(player_won: bool, message: str) -> None:
    """Print the final game result after case submission."""
    print()
    print(THICK_DIVIDER)
    if player_won:
        print("  *** CASE CLOSED - YOU WIN ***")
    else:
        print("  *** CASE DISMISSED - YOU LOSE ***")
    print(THICK_DIVIDER)
    print()
    _wrap(message)
    print()
    print(THICK_DIVIDER)
    print()


# ── Prompt functions ──────────────────────────────────────────────────────────


def prompt_main_menu_action() -> str:
    """Ask the player for the next action and return their raw input."""
    try:
        return input("  > ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return "quit"


def prompt_keyword() -> str:
    """Ask the player to enter a keyword for searching."""
    print("  Enter keyword (or phrase) to search:")
    try:
        return input("  > ").strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def prompt_document_id() -> str:
    """Ask the player which document they want to open."""
    print("  Enter document ID:")
    try:
        return input("  > ").strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def prompt_evidence_ids() -> list[str]:
    """Ask the player which evidence items they want to collect.

    Accepts comma-separated or space-separated evidence IDs.
    """
    print("  Enter evidence ID(s) to collect (separate multiple with commas):")
    try:
        raw = input("  > ").strip()
    except (EOFError, KeyboardInterrupt):
        return []
    parts = [p.strip() for p in raw.replace(",", " ").split() if p.strip()]
    return parts


def prompt_suspect(case_data: CaseData) -> str:
    """Display the suspect list and ask the player who they want to accuse."""
    _section("Suspects")
    for i, name in enumerate(case_data.suspects, start=1):
        print(f"    {i}.  {name}")
    print()
    print("  Enter the name of the suspect you want to accuse:")
    try:
        return input("  > ").strip()
    except (EOFError, KeyboardInterrupt):
        return ""


# ── Utility helpers (also used by main.py) ───────────────────────────────────


def print_error(message: str) -> None:
    """Print a clearly marked error message."""
    print(f"\n  [!]  {message}\n")


def print_info(message: str) -> None:
    """Print a neutral informational message."""
    print(f"\n  [i]  {message}\n")
