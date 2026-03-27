"""Static case data builders for the File Not Found demo.

All hard-coded case content lives here so it can be edited without
touching engine or validation logic.
"""

from __future__ import annotations

from models import CaseData, CaseSolution, Document, EvidenceItem

DEMO_CASE_TITLE = "Hit and Run"


def build_demo_case() -> CaseData:
    """Create and return the full demo case object."""
    return CaseData(
        title=DEMO_CASE_TITLE,
        intro_text=build_intro_text(),
        suspects=build_suspects(),
        documents=build_documents(),
        starting_keywords=build_starting_keywords(),
        solution=build_solution(),
    )


def build_intro_text() -> str:
    """Return the opening text shown when the player starts the demo."""
    return (
        "A hit-and-run collision occurred at the intersection of Fulton Street "
        "and Mercer Avenue at 8:57 PM. The driver fled the scene without stopping. "
        "Debris at the scene points to a dark blue sedan with front-right headlight "
        "damage. Your job is to search available records, unlock documents, collect "
        "evidence, and identify the driver responsible. Submit your suspect and "
        "evidence when you are ready to close the case."
    )


def build_suspects() -> list[str]:
    """Return the list of suspects for the demo case."""
    return [
        "Tyler Smith",
        "Emily Carter",
        "Marcus Webb",
    ]


def build_starting_keywords() -> list[str]:
    """Return the keywords available to the player at the start of the game."""
    return [
        "accident timeline",
        "traffic camera footage",
        "witness testimony",
    ]


def build_documents() -> list[Document]:
    """Return all documents used in the demo case."""
    return [
        _build_police_report(),
        _build_accident_timeline_report(),
        _build_witness_statement(),
        _build_traffic_camera_footage(),
        _build_location_data_summary(),
        _build_insurance_claim(),
        _build_auto_repair_shop_receipt(),
        _build_car_registration_database(),
    ]


def build_solution() -> CaseSolution:
    """Return the correct suspect and required evidence for a win."""
    return CaseSolution(
        correct_suspect="Tyler Smith",
        required_evidence_ids={"EV-CAM", "EV-REG", "EV-REP"},
    )


def build_evidence_item(
    evidence_id: str,
    label: str,
    description: str,
    source_document_id: str,
    is_key_evidence: bool = False,
) -> EvidenceItem:
    """Create one evidence item for reuse while building documents."""
    return EvidenceItem(
        evidence_id=evidence_id,
        label=label,
        description=description,
        source_document_id=source_document_id,
        is_key_evidence=is_key_evidence,
    )


# ── Private document builders ─────────────────────────────────────────────────
# Each function builds one document with its own evidence items inline.
# Unlock keywords must exactly match entries in starting_keywords or the
# discovered_keywords of another document so the search flow can find them.
#
# Keyword chain overview:
#   Starting keywords unlock:
#     "accident timeline"      -> Police Report, Accident Timeline Report
#     "traffic camera footage" -> Accident Timeline Report, Traffic Camera Footage
#     "witness testimony"      -> Witness Statement, Location Data Summary
#   Discovered keywords unlock:
#     "vehicle registration database" (from Witness Statement, Traffic Camera)
#                              -> Car Registration Database, Insurance Claim
#     "auto repair records"    (from Accident Timeline, Location Data,
#                               Car Registration Database)
#                              -> Auto Repair Shop Receipt


def _build_police_report() -> Document:
    return Document(
        document_id="DOC-001",
        title="Police Report",
        text=(
            "At approximately 8:57 PM, officers responded to a reported hit-and-run "
            "collision at the intersection of Fulton Street and Mercer Avenue. The "
            "victim stated that a dark-colored sedan struck their vehicle while making "
            "a fast right turn and fled the scene without stopping. Debris recovered "
            "from the roadway included fragments of a front-right headlight housing "
            "and dark blue paint transfer. No immediate plate information was obtained "
            "at the scene, but nearby traffic cameras and witness interviews were "
            "flagged for follow-up review."
        ),
        unlock_keywords=["accident timeline"],
        discovered_keywords=["witness testimony", "traffic camera footage"],
        evidence_items=[
            build_evidence_item(
                "EV-POL",
                "Police Report Summary",
                "Collision at 8:57 PM at Fulton and Mercer. Debris indicates "
                "front-right headlight damage. Dark blue paint transfer found at scene.",
                "DOC-001",
            )
        ],
    )


def _build_accident_timeline_report() -> Document:
    return Document(
        document_id="DOC-002",
        title="Accident Timeline Report",
        text=(
            "Compiled timeline of known events related to the hit-and-run investigation:\n"
            "- 8:57 PM: collision reported at Fulton and Mercer\n"
            "- 8:58 PM to 9:01 PM: witness observes damaged dark blue sedan leaving area\n"
            "- 9:08 PM: traffic camera C-14 records a dark blue vehicle with front-right "
            "damage traveling east on Mercer Avenue\n"
            "- Next day, 8:14 AM: repair order opened for a matching vehicle with "
            "front-right damage\n\n"
            "The timing of the collision, witness observations, camera footage, and repair "
            "activity strongly suggests continuity between the same vehicle and owner."
        ),
        unlock_keywords=["accident timeline", "traffic camera footage"],
        discovered_keywords=["auto repair records", "witness testimony"],
        evidence_items=[
            build_evidence_item(
                "EV-TIM",
                "Accident Timeline",
                "Timeline links the crash at 8:57 PM, the camera sighting at 9:08 PM, "
                "and the repair visit the next morning into one connected sequence.",
                "DOC-002",
            )
        ],
        is_unlocked=True,
    )


def _build_witness_statement() -> Document:
    return Document(
        document_id="DOC-003",
        title="Witness Statement",
        text=(
            "Witness Emily Carter reported hearing the crash and seeing a dark blue "
            "TOYOTA PRIUS speed away from the intersection moments later. She stated "
            "the vehicle had visible damage near the front-right headlight and remembered "
            "the driver looked like a man wearing a dark jacket. She was unable to "
            "identify the full plate number, but recalled seeing the characters \"7KQ\" "
            "before the car turned south onto Mercer Avenue."
        ),
        unlock_keywords=["witness testimony"],
        discovered_keywords=["traffic camera footage", "vehicle registration database"],
        evidence_items=[
            build_evidence_item(
                "EV-WIT",
                "Witness Testimony",
                "Witness saw a dark blue 2017 TOYOTA PRIUS flee the scene with front-right "
                "damage. Recalled partial plate \"7KQ\" and a male driver in a dark jacket.",
                "DOC-003",
            )
        ],
    )


def _build_traffic_camera_footage() -> Document:
    return Document(
        document_id="DOC-004",
        title="Traffic Camera Footage",
        text=(
            "City traffic camera C-14 captured a dark blue sedan traveling east on Mercer "
            "Avenue at 9:08 PM, approximately 11 seconds after the reported collision at "
            "the Fulton and Mercer intersection. The footage shows visible damage to the "
            "vehicle's front-right headlight housing and a partial license plate reading "
            "__7KQ_. The driver does not stop and continues southbound out of frame. "
            "Vehicle shape and trim are consistent with a 2017 TOYOTA PRIUS."
        ),
        unlock_keywords=["traffic camera footage"],
        discovered_keywords=["vehicle registration database", "accident timeline"],
        evidence_items=[
            build_evidence_item(
                "EV-CAM",
                "Camera Footage of Suspect Vehicle",
                "Footage shows a dark blue 2017 TOYOTA PRIUS fleeing the scene with "
                "front-right damage and partial plate __7KQ_ at 9:08 PM.",
                "DOC-004",
                is_key_evidence=True,
            )
        ],
    )


def _build_location_data_summary() -> Document:
    return Document(
        document_id="DOC-005",
        title="Location Data Summary",
        text=(
            "Cell location summary for Tyler Smith's phone shows movement consistent "
            "with the route taken by the suspect vehicle. At 8:56 PM, the device was "
            "active near Fulton Street. At 9:09 PM, it pinged a tower covering Mercer "
            "Avenue southbound, matching the direction seen in traffic footage. The next "
            "morning, the same device was recorded near Mercer Auto Body shortly before "
            "the repair receipt timestamp. No conflicting location activity was recorded "
            "during the relevant window."
        ),
        unlock_keywords=["witness testimony"],
        discovered_keywords=["auto repair records"],
        evidence_items=[
            build_evidence_item(
                "EV-LOC",
                "Phone Location Data",
                "Tyler Smith's phone tracked near the crash at 8:56 PM, along the escape "
                "route at 9:09 PM, and near the repair shop before the 8:14 AM receipt.",
                "DOC-005",
            )
        ],
    )


def _build_insurance_claim() -> Document:
    return Document(
        document_id="DOC-006",
        title="Insurance Claim",
        text=(
            "Insurance claim filed by Tyler Smith at 10:42 AM on the day after the "
            "collision reports damage to a 2017 TOYOTA PRIUS. In the statement, Smith "
            "claims the vehicle was damaged after \"striking an animal\" late the previous "
            "night. Claim notes list damage to the front-right headlight area and bumper "
            "corner. The timing and damage description are consistent with the hit-and-run "
            "investigation, but the explanation does not match the collision evidence "
            "gathered from the scene."
        ),
        unlock_keywords=["vehicle registration database"],
        discovered_keywords=["auto repair records"],
        evidence_items=[
            build_evidence_item(
                "EV-INS",
                "Insurance Claim",
                "Tyler Smith filed a claim for front-right headlight damage the day after "
                "the crash, claiming he hit an animal — inconsistent with scene evidence.",
                "DOC-006",
            )
        ],
    )


def _build_auto_repair_shop_receipt() -> Document:
    return Document(
        document_id="DOC-007",
        title="Auto Repair Shop Receipt",
        text=(
            "Repair order #88421 from Mercer Auto Body shows a same-day walk-in service "
            "request for a 2017 TOYOTA PRIUS, plate JT7KQ4, on the morning following the "
            "collision. The receipt lists replacement of the front-right headlight assembly, "
            "bumper clip repair, and paint touch-up for damage described as \"sudden "
            "front-corner impact.\" Customer name on file is Tyler Smith. Payment was made "
            "by personal debit card at 8:14 AM."
        ),
        unlock_keywords=["auto repair records"],
        discovered_keywords=[],
        evidence_items=[
            build_evidence_item(
                "EV-REP",
                "Auto Repair Receipt",
                "Repair receipt for plate JT7KQ4 — a 2017 TOYOTA PRIUS registered to "
                "Tyler Smith — shows front-right headlight replaced at 8:14 AM the morning "
                "after the crash.",
                "DOC-007",
                is_key_evidence=True,
            )
        ],
    )


def _build_car_registration_database() -> Document:
    return Document(
        document_id="DOC-008",
        title="Car Registration Database",
        text=(
            "A filtered search of the vehicle registration database was performed using "
            "the partial plate pattern __7KQ_, vehicle color dark blue, and model family "
            "TOYOTA PRIUS. Only one local registration matched all available criteria: "
            "2017 TOYOTA PRIUS, plate JT7KQ4, registered to Tyler Smith, address 1148 "
            "Pine Hollow Drive. Registration status is active, and the recorded vehicle "
            "color matches the traffic camera footage."
        ),
        unlock_keywords=["vehicle registration database"],
        discovered_keywords=["auto repair records", "witness testimony"],
        evidence_items=[
            build_evidence_item(
                "EV-REG",
                "Vehicle Registration",
                "Plate JT7KQ4 is registered to Tyler Smith — a dark blue 2017 TOYOTA PRIUS "
                "matching the camera footage and partial plate recalled by the witness.",
                "DOC-008",
                is_key_evidence=True,
            )
        ],
    )
