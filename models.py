"""Domain models for the File Not Found demo game.

This module should contain the core data structures used by the rest of the
project. Keep this file focused on data and model-related helper methods.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class EvidenceItem:
    """Represent one piece of evidence the player can collect."""

    evidence_id: str
    label: str
    description: str
    source_document_id: str
    is_key_evidence: bool = False


@dataclass(slots=True)
class Document:
    """Represent one in-game document that can be unlocked and read."""

    document_id: str
    title: str
    text: str
    unlock_keywords: list[str] = field(default_factory=list)
    discovered_keywords: list[str] = field(default_factory=list)
    evidence_items: list[EvidenceItem] = field(default_factory=list)
    is_unlocked: bool = False

    def matches_keyword(self, keyword: str) -> bool:
        """Return True when the given keyword unlocks this document.

        This should perform the keyword comparison logic used by the game
        search flow.
        """

        if keyword in self.unlock_keywords:
            return True
        return False

    def get_evidence_by_id(self, evidence_id: str) -> EvidenceItem | None:
        """Return the matching evidence item from this document, if present.

        This should help the engine find evidence inside a document without
        duplicating lookup logic in multiple places.
        """
        i=0
        while i < len(self.evidence_items):
            if evidence_id == self.evidence_items[i.evidence_id]:
                return self.evidence_items[i]
            i+=1



@dataclass(slots=True)
class CaseSolution:
    """Represent the correct suspect and evidence required to win."""

    correct_suspect: str
    required_evidence_ids: set[str] = field(default_factory=set)


@dataclass(slots=True)
class CaseData:
    """Represent all static data needed to run one case."""

    title: str
    intro_text: str
    suspects: list[str] = field(default_factory=list)
    documents: list[Document] = field(default_factory=list)
    starting_keywords: list[str] = field(default_factory=list)
    solution: CaseSolution | None = None

    def get_document_by_id(self, document_id: str) -> Document | None:
        """Return the document with the given ID, if it exists.

        This should provide one standard way to retrieve a document from the
        case data.
        """
        i=0
        while i < len(self.documents):
            if document_id == self.documents[i]:
                return self.doucuments[i]
            i+= 1



@dataclass(slots=True)
class GameState:
    """Track the current player progress for the active play session."""

    case_data: CaseData
    available_keywords: set[str] = field(default_factory=set)
    used_keywords: set[str] = field(default_factory=set)
    unlocked_document_ids: set[str] = field(default_factory=set)
    collected_evidence_ids: set[str] = field(default_factory=set)
    selected_suspect: str | None = None
    game_over: bool = False
    player_won: bool = False


    def unlock_document(self, document_id: str) -> None:
        """Mark a document as unlocked in the current game state.

        This should update both the state tracking and any related document
        status if needed.
        """
        Document.is_unlocked[document_id] = True

    def collect_evidence(self, evidence_id: str) -> None:
        """Add an evidence item to the player's collected evidence set.

        This should prevent duplicates and keep state updates in one place.
        """
        i=0
        while i < len(self.collected_evidence_ids):
            if evidence_id == self.collected_evidence_ids[i]:
                return
            i+=1
        self.collected_evidence_ids += evidence_id

#Document building for case 1
Auto_Repair_Shop_Receipt = Document("001", "Auto Repair Shop Receipt",
"Repair order #88421 from Mercer Auto Body shows a same-day walk-in service request for a 2017 TOHOTA PRIS, plate JT7KQ4, on the morning following the collision. The receipt lists replacement of the front-right headlight assembly, bumper clip repair, and paint touch-up for damage described as \"sudden front-corner impact.\" Customer name on file is Tyler Smith. Payment was made by personal debit card at 8:14 AM.",
["auto_repair_records"],["accident_timeline"],
["Repair receipt is tied to plate JT7KQ4", "Vehicle on receipt is a 2017 TOHOTA PRIUS", "Repairs include the front-right headlight assembly", "Customer listed is Tyler Smith", "Repair happened the morning after the crash at 8:14 AM"],
False)

Accident_Timeline_Report = Document("002", "Accident Timeline Report",
"Compiled timeline of known events related to the hit-and-run investigation:\n- 8:57 PM: collision reported at Fulton and Mercer\n" \
"- 8:58 PM to 9:01 PM: witness observes damaged dark blue sedan leaving area\n- 9:08 PM: traffic camera C-14 records a dark blue vehicle with front-right damage traveling east on Mercer Avenue\n" \
"- Next day, 8:14 AM: repair order opened for a matching vehicle with front-right damage\n\nThe timing of the collision, witness observations, camera footage, and repair activity strongly suggests continuity between the same vehicle and owner.",
["accident_timeline"], ["auto_repair_records", "witness_testimony"], 
["Camera footage happened shortly after the collision", "Witness and camera observations fit the same vehicle",
 "Repair activity occurred the next morning", "Timeline links the crash, escape, and repair into one sequence"], 
 True)

Location_Data_Summary = Document("003", "Location Data Summary",
"Cell location summary for Tyler Smith's phone shows movement consistent with the route taken by the suspect vehicle. At 8:56 PM, the device was active near Fulton Street. At 9:09 PM, it pinged a tower covering Mercer Avenue southbound, matching the direction seen in traffic footage. The next morning, the same device was recorded near Mercer Auto Body shortly before the repair receipt timestamp. No conflicting location activity was recorded during the relevant window.",
["witness_testimony"], ["auto repair records"], ["Tyler Smith's phone was near the crash area at 8:56 PM", "Phone movement matches the escape route seen on camera", "Phone was near Mercer Auto Body before the repair visit", "No conflicting location data appears during the relevant time period"],
False)

Insurance_Claim = Document("004", "Insurance Claim", 
"Insurance claim filed by Tyler Smith at 10:42 AM on the day after the collision reports damage to a 2017 TOHOTA PRIS. In the statement, Smith claims the vehicle was damaged after \"striking an animal\" late the previous night. Claim notes list damage to the front-right headlight area and bumper corner. The timing and damage description are consistent with the hit-and-run investigation, but the explanation does not match the collision evidence gathered from the scene.",
["vehicle registration database"], ["auto repair records"], ["Insurance claim was filed by Tyler Smith", "Claim vehicle is a 2017 TOHOTA PRIUS", "Claim describes damage to the front-right headlight area", "Smith gave an explanation that conflicts with the investigation evidence",],
False)
