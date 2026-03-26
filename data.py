"""Static case data builders for the File Not Found demo.

This module should define the full demo case, including suspects, keywords,
documents, and evidence items. Keep all hard-coded case content here so that
it is easy to edit without touching engine logic.
"""

from __future__ import annotations

from models import CaseData, CaseSolution, Document, EvidenceItem


# TODO: Add the agreed demo story details once the team finalizes the case.
DEMO_CASE_TITLE = "File Not Found"


def build_demo_case() -> CaseData:
    """Create and return the full demo case object.

    This should assemble the intro text, suspects, documents, starting
    keywords, and the winning solution into one CaseData instance.
    """
    pass


def build_intro_text() -> str:
    """Return the opening text shown when the player starts the demo.

    This should briefly explain the case and tell the player what they are
    trying to prove.
    """
    return "Welcome to FileNotFound\nA document search mystery game\n\n\n\nMade by Jacob, Joshua, and Abdelrahman"

def build_suspects() -> list[str]:
    """Return the list of suspects for the demo case.

    Keep the suspect list short and easy to present during the class demo.
    """
    pass


def build_starting_keywords() -> list[str]:
    """Return the keywords available to the player at the start of the game.

    These keywords should unlock the first wave of documents.
    """
    return []



def build_documents() -> list[Document]:
    """Return all documents used in the demo case.

    Each document should include its unlock keywords, discovered keywords,
    visible text, and evidence items.
    """

    return [Document.Auto_Repair_Shop_Receipt, Document.Accident_Timeline_Report, Document.Location_Data_Summary, Document.Insurance_Claim, Document.Police_Report, Document.Witness_Statement, Document.Traffic_Camera_Footage, Document.Car_Registration_Database]



def build_solution() -> CaseSolution:
    """Return the correct suspect and required evidence for a win.

    This should reflect the final answer the player is meant to reach.
    """
    pass


def build_evidence_item(
    evidence_id: str,
    label: str,
    description: str,
    source_document_id: str,
    is_key_evidence: bool = False,
) -> EvidenceItem:
    """Create one evidence item for reuse while building documents.

    This helper should keep evidence creation consistent across the data file.
    """
    pass

