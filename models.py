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

Police_Report = Document("005", "Police Report", 
"At approximately 8:57 PM, officers responded to a reported hit-and-run collision at the intersection of Fulton Street and Mercer Avenue. The victim stated that a dark-colored sedan struck their vehicle while making a fast right turn and fled the scene without stopping. Debris recovered from the roadway included fragments of a front-right headlight housing and dark blue paint transfer. No immediate plate information was obtained at the scene, but nearby traffic cameras and witness interviews were flagged for follow-up review.",
["accident timeline"], ["witness testimony", "traffic camera footage"], ["Collision occurred at 8:57 PM at Fulton and Mercer", "Debris indicates damage to a front-right headlight", "Dark blue paint transfer was found at the scene", "Traffic cameras and witnesses were identified as leads"],
False)

Witness_Statement = Document("006", "Witness Statement", "Witness Emily Carter reported hearing the crash and seeing a dark blue TOHOTA PRIS speed away from the intersection moments later. She stated the vehicle had visible damage near the front-right headlight and remembered the driver looked like a man wearing a dark jacket. She was unable to identify the full plate number, but recalled seeing the characters \"7KQ\" before the car turned south onto Mercer Avenue.",
["witness testimony"], ["traffic camera footage", "vehicle registration database"], ["Witness saw a dark blue TOHOTA PRIS leave the scene", "Witness noticed front-right headlight damage", "Witness remembered the partial plate \"7KQ\"", "Witness stated the driver appeared to be a man in a dark jacket"],
False)

Traffic_Camera_Footage = Document("007", "Traffic Camera Footage", "City traffic camera C-14 captured a dark blue sedan traveling east on Mercer Avenue at 9:08 PM, approximately 11 seconds after the reported collision at the Fulton and Mercer intersection. The footage shows visible damage to the vehicle's front-right headlight housing and a partial license plate reading __7KQ_. The driver does not stop and continues southbound out of frame. Vehicle shape and trim are consistent with a 2017 TOHOTA PRIUS.",
["traffic camera footage"], ["vehicle registration database", "accident timeline"], ["Camera footage shows the suspect vehicle leaving the scene", "Partial plate visible: __7KQ_", "Front-right headlight damage visible", "Vehicle appears to be a dark blue 2017 TOHOTA PRIUS"],
False)

Car_Registration_Database = Document("008", "Car Registration Database", "A filtered search of the vehicle registration database was performed using the partial plate pattern __7KQ_, vehicle color dark blue, and model family TOHOTA PRIS. Only one local registration matched all available criteria: 2017 TOHOTA PRIS, plate JT7KQ4, registered to Tyler Smith, address 1148 Pine Hollow Drive. Registration status is active, and the recorded vehicle color matches the traffic camera footage.",
["vehicle registration database"], ["auto repair records", "witness testimony"], ["Registration links plate JT7KQ4 to Tyler Smith", "Registered vehicle is a 2017 TOHOTA PRIUS", "Vehicle color matches the camera footage", "Registration is the only local match for the observed plate pattern"],
False)
