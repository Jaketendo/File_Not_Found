"""Entry point for the File Not Found terminal demo.

This module should wire together the case data, engine logic, and terminal UI.
Keep it small and focused on program startup plus the main loop.
"""

from __future__ import annotations

from models import GameState


def run_game() -> None:
    """Start the demo and keep the command loop running until the game ends.

    This should create the case data, initialize the game state, show the
    introduction, and repeatedly route player commands to the correct helper
    functions.
    """
    pass


def handle_search_action(state: GameState) -> None:
    """Run the full keyword-search interaction for one turn.

    This should gather user input, call the engine search flow, and display the
    search result in the terminal.
    """
    pass


def handle_read_action(state: GameState) -> None:
    """Run the document-reading interaction for one turn.

    This should ask which document to open and then display its contents.
    """
    pass


def handle_collect_action(state: GameState) -> None:
    """Run the evidence-collection interaction for one turn.

    This should open the chosen document context, ask which evidence to take,
    and update the game state through the engine.
    """
    pass


def handle_submit_action(state: GameState) -> None:
    """Run the final accusation and evidence-submission flow.

    This should collect the suspect and evidence choices, submit them to the
    engine, and show the final result.
    """
    pass


if __name__ == "__main__":
    run_game()
