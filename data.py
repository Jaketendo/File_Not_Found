"""Static case data builders for the File Not Found.

All hard-coded case content lives here so it can be edited without
touching engine or validation logic.
"""

from __future__ import annotations

from models import CaseData, CaseSolution, Document, EvidenceItem

ALL_CASES = [
    "Hit and Run",
    "Dead Man's Message",
    "Ghost Employee",
    "Silent Witness",
]


def build_demo_case(case_index: int = 0) -> CaseData:
    """Create and return a case object by index (0-3)."""
    builders = [
        _build_case_hit_and_run,
        _build_case_dead_mans_message,
        _build_case_ghost_employee,
        _build_case_silent_witness,
    ]
    if case_index < 0 or case_index >= len(builders):
        case_index = 0
    return builders[case_index]()


def build_evidence_item(
    evidence_id: str,
    label: str,
    description: str,
    source_document_id: str,
    is_key_evidence: bool = False,
) -> EvidenceItem:
    """Create one evidence item."""
    return EvidenceItem(
        evidence_id=evidence_id,
        label=label,
        description=description,
        source_document_id=source_document_id,
        is_key_evidence=is_key_evidence,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CASE 0 — HIT AND RUN
# Keywords: accident timeline, traffic camera footage, witness testimony
#           -> vehicle registration database, auto repair records
# ═══════════════════════════════════════════════════════════════════════════════

def _build_case_hit_and_run() -> CaseData:
    return CaseData(
        title="Hit and Run",
        intro_text=(
            "A hit-and-run collision occurred at the intersection of Fulton Street "
            "and Mercer Avenue at 8:57 PM. The driver fled the scene without stopping. "
            "Debris at the scene points to a dark blue sedan with front-right headlight "
            "damage. Your job is to search available records, unlock documents, collect "
            "evidence, and identify the driver responsible. Submit your suspect and "
            "evidence when you are ready to close the case."
        ),
        suspects=["Tyler Smith", "Emily Carter", "Marcus Webb"],
        documents=[
            _har_police_report(),
            _har_accident_timeline(),
            _har_witness_statement(),
            _har_traffic_camera(),
            _har_location_data(),
            _har_insurance_claim(),
            _har_repair_receipt(),
            _har_registration(),
        ],
        starting_keywords=[
            "accident timeline",
            "traffic camera footage",
            "witness testimony",
        ],
        solution=CaseSolution(
            correct_suspect="Tyler Smith",
            required_evidence_ids={"EV-CAM", "EV-REG", "EV-REP"},
        ),
    )


def _har_police_report() -> Document:
    return Document(
        document_id="DOC-001", title="Police Report",
        text=(
            "At approximately 8:57 PM, officers responded to a reported hit-and-run "
            "collision at the intersection of Fulton Street and Mercer Avenue. The victim "
            "stated that a dark-colored sedan struck their vehicle while making a fast right "
            "turn and fled the scene without stopping. Debris recovered from the roadway "
            "included fragments of a front-right headlight housing and dark blue paint "
            "transfer. No immediate plate information was obtained at the scene, but nearby "
            "traffic cameras and witness interviews were flagged for follow-up review."
        ),
        unlock_keywords=["accident timeline"],
        discovered_keywords=["witness testimony", "traffic camera footage"],
        evidence_items=[build_evidence_item("EV-POL", "Police Report Summary",
            "Collision at 8:57 PM at Fulton and Mercer. Front-right headlight debris "
            "and dark blue paint transfer found at scene.", "DOC-001")],
    )


def _har_accident_timeline() -> Document:
    return Document(
        document_id="DOC-002", title="Accident Timeline Report",
        text=(
            "Compiled timeline of known events:\n"
            "- 8:57 PM: collision reported at Fulton and Mercer\n"
            "- 8:58 PM to 9:01 PM: witness observes damaged dark blue sedan leaving area\n"
            "- 9:08 PM: traffic camera C-14 records a dark blue vehicle with front-right "
            "damage traveling east on Mercer Avenue\n"
            "- Next day, 8:14 AM: repair order opened for a matching vehicle\n\n"
            "The timing of events strongly suggests continuity between the same vehicle and owner."
        ),
        unlock_keywords=["accident timeline", "traffic camera footage"],
        discovered_keywords=["auto repair records", "witness testimony"],
        evidence_items=[build_evidence_item("EV-TIM", "Accident Timeline",
            "Timeline links the crash at 8:57 PM, camera sighting at 9:08 PM, "
            "and repair visit the next morning.", "DOC-002")],
        is_unlocked=True,
    )


def _har_witness_statement() -> Document:
    return Document(
        document_id="DOC-003", title="Witness Statement",
        text=(
            "Witness Emily Carter reported hearing the crash and seeing a dark blue "
            "TOYOTA PRIUS speed away moments later. She stated the vehicle had visible "
            "damage near the front-right headlight and the driver looked like a man in "
            "a dark jacket. She recalled the partial plate characters \"7KQ\" before the "
            "car turned south onto Mercer Avenue."
        ),
        unlock_keywords=["witness testimony"],
        discovered_keywords=["traffic camera footage", "vehicle registration database"],
        evidence_items=[build_evidence_item("EV-WIT", "Witness Testimony",
            "Witness saw a dark blue 2017 TOYOTA PRIUS flee with front-right damage "
            "and partial plate \"7KQ\".", "DOC-003")],
    )


def _har_traffic_camera() -> Document:
    return Document(
        document_id="DOC-004", title="Traffic Camera Footage",
        text=(
            "City traffic camera C-14 captured a dark blue sedan traveling east on Mercer "
            "Avenue at 9:08 PM, approximately 11 seconds after the collision. The footage "
            "shows visible damage to the front-right headlight housing and a partial plate "
            "reading __7KQ_. Vehicle shape is consistent with a 2017 TOYOTA PRIUS."
        ),
        unlock_keywords=["traffic camera footage"],
        discovered_keywords=["vehicle registration database", "accident timeline"],
        evidence_items=[build_evidence_item("EV-CAM", "Camera Footage of Suspect Vehicle",
            "Footage shows a dark blue 2017 TOYOTA PRIUS fleeing with front-right damage "
            "and partial plate __7KQ_ at 9:08 PM.", "DOC-004", is_key_evidence=True)],
    )


def _har_location_data() -> Document:
    return Document(
        document_id="DOC-005", title="Location Data Summary",
        text=(
            "Cell location data for Tyler Smith's phone shows movement consistent with "
            "the suspect vehicle route. At 8:56 PM the device was near Fulton Street. "
            "At 9:09 PM it pinged a tower on Mercer Avenue southbound. The next morning "
            "it was recorded near Mercer Auto Body before the repair receipt timestamp."
        ),
        unlock_keywords=["witness testimony"],
        discovered_keywords=["auto repair records"],
        evidence_items=[build_evidence_item("EV-LOC", "Phone Location Data",
            "Tyler Smith's phone tracked near the crash at 8:56 PM, along the escape "
            "route at 9:09 PM, and near the repair shop before 8:14 AM.", "DOC-005")],
    )


def _har_insurance_claim() -> Document:
    return Document(
        document_id="DOC-006", title="Insurance Claim",
        text=(
            "Insurance claim filed by Tyler Smith the day after the collision reports "
            "damage to a 2017 TOYOTA PRIUS. Smith claims the vehicle was damaged after "
            "\"striking an animal\" late that night. The damage description and timing are "
            "consistent with the hit-and-run but the explanation does not match scene evidence."
        ),
        unlock_keywords=["vehicle registration database"],
        discovered_keywords=["auto repair records"],
        evidence_items=[build_evidence_item("EV-INS", "Insurance Claim",
            "Tyler Smith filed a claim for front-right headlight damage the day after "
            "the crash with an explanation inconsistent with scene evidence.", "DOC-006")],
    )


def _har_repair_receipt() -> Document:
    return Document(
        document_id="DOC-007", title="Auto Repair Shop Receipt",
        text=(
            "Repair order #88421 from Mercer Auto Body shows a walk-in service request "
            "for a 2017 TOYOTA PRIUS, plate JT7KQ4, the morning after the collision. "
            "The receipt lists replacement of the front-right headlight assembly and "
            "paint touch-up. Customer name: Tyler Smith. Payment at 8:14 AM."
        ),
        unlock_keywords=["auto repair records"],
        discovered_keywords=[],
        evidence_items=[build_evidence_item("EV-REP", "Auto Repair Receipt",
            "Repair receipt for plate JT7KQ4 registered to Tyler Smith — front-right "
            "headlight replaced at 8:14 AM the morning after the crash.",
            "DOC-007", is_key_evidence=True)],
    )


def _har_registration() -> Document:
    return Document(
        document_id="DOC-008", title="Car Registration Database",
        text=(
            "A search using partial plate __7KQ_, dark blue color, and TOYOTA PRIUS "
            "returned one local match: 2017 TOYOTA PRIUS, plate JT7KQ4, registered to "
            "Tyler Smith, 1148 Pine Hollow Drive. Vehicle color matches traffic camera footage."
        ),
        unlock_keywords=["vehicle registration database"],
        discovered_keywords=["auto repair records", "witness testimony"],
        evidence_items=[build_evidence_item("EV-REG", "Vehicle Registration",
            "Plate JT7KQ4 registered to Tyler Smith — dark blue 2017 TOYOTA PRIUS "
            "matching camera footage and witness partial plate.",
            "DOC-008", is_key_evidence=True)],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CASE 1 — DEAD MAN'S MESSAGE
# Keywords: autopsy report, draft article, phone call logs
#           -> apartment security logs, deleted notes, bank transactions
# ═══════════════════════════════════════════════════════════════════════════════

def _build_case_dead_mans_message() -> CaseData:
    return CaseData(
        title="Dead Man's Message",
        intro_text=(
            "A journalist was found dead in his apartment in what initially appeared "
            "to be a suicide. Investigators have since found signs that the death may "
            "have been staged. Search the available records, unlock documents, collect "
            "evidence, and identify who staged the death."
        ),
        suspects=["Victor Hale", "Sandra Orin", "James Pruett"],
        documents=[
            _dmm_police_report(),
            _dmm_autopsy_report(),
            _dmm_security_logs(),
            _dmm_phone_call_logs(),
            _dmm_draft_article(),
            _dmm_deleted_notes(),
            _dmm_laptop_activity(),
            _dmm_bank_transactions(),
        ],
        starting_keywords=[
            "autopsy report",
            "draft article",
            "phone call logs",
        ],
        solution=CaseSolution(
            correct_suspect="Victor Hale",
            required_evidence_ids={"EV-TOD", "EV-ART", "EV-KEY"},
        ),
    )


def _dmm_police_report() -> Document:
    return Document(
        document_id="DOC-001", title="Police Report",
        text=(
            "Officers responded to a welfare check at apartment 4B on Calloway Street "
            "at 7:42 AM. The journalist, Daniel Mercer, was found deceased at his desk. "
            "A typed note was present on the screen. Initial assessment suggested suicide "
            "but the medical examiner flagged inconsistencies in the body position and "
            "the absence of expected physical indicators. The case was escalated for "
            "further investigation."
        ),
        unlock_keywords=["autopsy report"],
        discovered_keywords=["apartment security logs", "phone call logs"],
        evidence_items=[build_evidence_item("EV-POL", "Police Report",
            "Initial scene report noting inconsistencies in body position flagged "
            "by the medical examiner.", "DOC-001")],
    )


def _dmm_autopsy_report() -> Document:
    return Document(
        document_id="DOC-002", title="Autopsy Report",
        text=(
            "Estimated time of death is between 11:00 PM and 1:00 AM based on body "
            "temperature and lividity. The typed suicide note on the laptop was timestamped "
            "at 2:17 AM — more than an hour after the latest estimated time of death. "
            "Toxicology found a sedative compound not consistent with self-administration "
            "at the levels detected. Cause of death: asphyxiation."
        ),
        unlock_keywords=["autopsy report"],
        discovered_keywords=["deleted notes", "bank transactions"],
        evidence_items=[build_evidence_item("EV-TOD", "Time of Death Discrepancy",
            "Time of death estimated between 11 PM and 1 AM. The suicide note was "
            "timestamped at 2:17 AM — after death. Sedative found in toxicology.",
            "DOC-002", is_key_evidence=True)],
    )


def _dmm_security_logs() -> Document:
    return Document(
        document_id="DOC-003", title="Apartment Security Logs",
        text=(
            "Building keycard logs show Daniel Mercer entered his apartment at 10:14 PM. "
            "At 11:52 PM a second entry was recorded using a visitor pass registered to "
            "Victor Hale. No exit was logged for Hale until 2:31 AM. The building's "
            "front camera was offline between 11:45 PM and 2:40 AM due to a reported "
            "maintenance issue submitted that same afternoon."
        ),
        unlock_keywords=["apartment security logs"],
        discovered_keywords=["phone call logs"],
        evidence_items=[build_evidence_item("EV-SEC", "Security Log Entry",
            "Victor Hale entered the building at 11:52 PM and did not exit until "
            "2:31 AM. Camera was offline during that window.", "DOC-003",
            is_key_evidence=True)],
    )


def _dmm_phone_call_logs() -> Document:
    return Document(
        document_id="DOC-004", title="Phone Call Logs",
        text=(
            "Daniel Mercer's phone records show a 14-minute call to an unregistered "
            "number at 9:58 PM the night of his death. The number was later traced to "
            "a burner device active only that week. Victor Hale's registered phone "
            "pinged a tower two blocks from the apartment at 11:49 PM. No outgoing "
            "calls were made from Mercer's phone after 10:12 PM."
        ),
        unlock_keywords=["phone call logs"],
        discovered_keywords=["apartment security logs", "deleted notes"],
        evidence_items=[build_evidence_item("EV-PHN", "Phone Call Log",
            "Mercer called an unregistered number at 9:58 PM. Hale's phone pinged "
            "two blocks away at 11:49 PM.", "DOC-004")],
    )


def _dmm_draft_article() -> Document:
    return Document(
        document_id="DOC-005", title="Draft Article",
        text=(
            "A recovered draft article titled 'The Hale Foundation Fraud' details "
            "allegations that Victor Hale diverted charitable funds into private accounts "
            "over a three year period totaling an estimated 2.4 million dollars. The "
            "article cites internal documents, a whistleblower, and bank records. A "
            "notation in the margin reads 'publish Friday — they know.' The article "
            "was never published."
        ),
        unlock_keywords=["draft article"],
        discovered_keywords=["bank transactions", "deleted notes"],
        evidence_items=[build_evidence_item("EV-ART", "Draft Article",
            "Unpublished article by Mercer directly accusing Victor Hale of "
            "diverting 2.4 million in charitable funds. Notation suggests "
            "Mercer felt threatened.", "DOC-005", is_key_evidence=True)],
    )


def _dmm_deleted_notes() -> Document:
    return Document(
        document_id="DOC-006", title="Deleted Notes Recovery",
        text=(
            "Forensic recovery of deleted files from Mercer's phone found 11 voice "
            "memos recorded over the final two weeks. The most recent memo, recorded "
            "at 8:44 PM the night of his death, states: 'Hale knows about the article. "
            "He called me and said if I publish it my career is over. I think he means "
            "more than that.' The memo was deleted remotely at 3:01 AM."
        ),
        unlock_keywords=["deleted notes"],
        discovered_keywords=["bank transactions"],
        evidence_items=[build_evidence_item("EV-DEL", "Deleted Voice Memo",
            "Mercer recorded a memo at 8:44 PM saying Hale threatened him over the "
            "article. Memo was deleted remotely at 3:01 AM.", "DOC-006")],
    )


def _dmm_laptop_activity() -> Document:
    return Document(
        document_id="DOC-007", title="Laptop Activity Report",
        text=(
            "Keystroke analysis of Mercer's laptop shows the final note was typed "
            "between 2:09 AM and 2:17 AM. Mercer's average typing speed across "
            "recovered documents was 94 words per minute. The final note was typed "
            "at 31 words per minute with irregular key intervals inconsistent with "
            "his established patterns. Three typos were corrected with backspace — "
            "Mercer had autocorrect enabled and no prior backspace usage was recorded."
        ),
        unlock_keywords=["draft article"],
        discovered_keywords=["deleted notes", "apartment security logs"],
        evidence_items=[build_evidence_item("EV-KEY", "Keyboard Activity Analysis",
            "Final note typed at 31 WPM versus Mercer's 94 WPM average, with "
            "irregular patterns inconsistent with his established typing behavior.",
            "DOC-007", is_key_evidence=True)],
    )


def _dmm_bank_transactions() -> Document:
    return Document(
        document_id="DOC-008", title="Bank Transactions",
        text=(
            "Mercer's bank records show a 5,000 dollar deposit two days before his "
            "death from an account linked to the Hale Foundation. No invoice or "
            "contract on file explains the payment. A second transfer of 12,000 dollars "
            "was scheduled for the day after his death and was cancelled at 3:14 AM "
            "the night he died — 43 minutes after Hale's keycard exit from the building."
        ),
        unlock_keywords=["bank transactions"],
        discovered_keywords=["apartment security logs"],
        evidence_items=[build_evidence_item("EV-BNK", "Bank Transaction Record",
            "Unexplained 5,000 dollar deposit from Hale Foundation. A 12,000 dollar "
            "transfer scheduled for the next day was cancelled at 3:14 AM — 43 minutes "
            "after Hale left the building.", "DOC-008")],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CASE 2 — GHOST EMPLOYEE
# Keywords: payroll records, audit report, login access logs
#           -> employee database, badge entry logs, approval email
# ═══════════════════════════════════════════════════════════════════════════════

def _build_case_ghost_employee() -> CaseData:
    return CaseData(
        title="Ghost Employee",
        intro_text=(
            "A company has discovered that someone has been receiving paychecks for "
            "months on behalf of an employee who does not exist. Investigators must "
            "determine who created the fake worker and stole the money. Search the "
            "available records, unlock documents, collect evidence, and identify "
            "the person responsible."
        ),
        suspects=["Rachel Voss", "Tom Greer", "Diane Falk"],
        documents=[
            _ge_audit_report(),
            _ge_employee_database(),
            _ge_payroll_records(),
            _ge_login_access_logs(),
            _ge_badge_entry_logs(),
            _ge_email_approval(),
            _ge_it_maintenance(),
            _ge_finance_review(),
        ],
        starting_keywords=[
            "payroll records",
            "audit report",
            "login access logs",
        ],
        solution=CaseSolution(
            correct_suspect="Rachel Voss",
            required_evidence_ids={"EV-PAY", "EV-BAD", "EV-FOR"},
        ),
    )


def _ge_audit_report() -> Document:
    return Document(
        document_id="DOC-001", title="Audit Report",
        text=(
            "An internal audit flagged employee ID 7741, listed as Marcus Finley, "
            "after six months of payroll disbursements with no HR onboarding record, "
            "no tax documentation, and no performance reviews on file. Total payments "
            "made: 47,200 dollars. The account receiving the payments was opened three "
            "days before the first paycheck was issued. The audit was triggered by an "
            "anonymous tip submitted through the company ethics hotline."
        ),
        unlock_keywords=["audit report"],
        discovered_keywords=["payroll records", "employee database"],
        evidence_items=[build_evidence_item("EV-AUD", "Audit Report Finding",
            "Employee ID 7741 received 47,200 dollars over six months with no HR "
            "records, tax documents, or onboarding on file.", "DOC-001")],
    )


def _ge_employee_database() -> Document:
    return Document(
        document_id="DOC-002", title="Employee Database Snapshot",
        text=(
            "The employee database snapshot taken at the time of the audit shows "
            "Marcus Finley listed under the finance department with a start date of "
            "eight months ago. The entry was created by user account RVoss — "
            "corresponding to Rachel Voss, Senior Finance Manager. No approval "
            "workflow was completed for the entry. The record was last modified "
            "four days before the audit was opened."
        ),
        unlock_keywords=["employee database"],
        discovered_keywords=["approval email", "login access logs"],
        evidence_items=[build_evidence_item("EV-EMP", "Database Entry",
            "Ghost employee record created by user account RVoss with no approval "
            "workflow completed.", "DOC-002")],
    )


def _ge_payroll_records() -> Document:
    return Document(
        document_id="DOC-003", title="Payroll Records",
        text=(
            "Payroll records show Marcus Finley received bi-weekly direct deposits "
            "to account ending 8847 for six consecutive pay cycles. Each deposit "
            "required a finance-level override to bypass the standard new-hire hold "
            "period. Override approvals were all submitted by the same finance "
            "workstation between 7:14 AM and 7:31 AM on Mondays — before most "
            "staff arrived at the office."
        ),
        unlock_keywords=["payroll records"],
        discovered_keywords=["badge entry logs", "approval email"],
        evidence_items=[build_evidence_item("EV-PAY", "Payroll Override Records",
            "Six finance-level overrides bypassing the new-hire hold — all submitted "
            "from the same workstation early Monday mornings.",
            "DOC-003", is_key_evidence=True)],
    )


def _ge_login_access_logs() -> Document:
    return Document(
        document_id="DOC-004", title="Login Access Logs",
        text=(
            "System login logs show that Rachel Voss's credentials were used to access "
            "the payroll system on each of the six Monday mornings in question. Login "
            "times range from 7:09 AM to 7:28 AM. Badge entry logs do not show Voss "
            "entering the building before 8:30 AM on any of those dates. Remote access "
            "was not enabled for her account during that period."
        ),
        unlock_keywords=["login access logs"],
        discovered_keywords=["badge entry logs", "employee database"],
        evidence_items=[build_evidence_item("EV-LOG", "Login Access Log",
            "Voss's credentials used in payroll system on six Monday mornings before "
            "her badge shows her entering the building.", "DOC-004")],
    )


def _ge_badge_entry_logs() -> Document:
    return Document(
        document_id="DOC-005", title="Badge Entry Logs",
        text=(
            "Badge entry records confirm Rachel Voss did not enter the building before "
            "8:30 AM on any of the six dates the payroll overrides were submitted. "
            "However, Tom Greer, IT Systems Administrator, badged in between 6:50 AM "
            "and 7:05 AM on all six dates. Greer's workstation is located in the same "
            "room as the finance terminals."
        ),
        unlock_keywords=["badge entry logs"],
        discovered_keywords=["approval email", "login access logs"],
        evidence_items=[build_evidence_item("EV-BAD", "Badge Entry Discrepancy",
            "Voss not in building during override submissions. Greer badged in early "
            "on all six dates and has access to finance terminals.",
            "DOC-005", is_key_evidence=True)],
    )


def _ge_email_approval() -> Document:
    return Document(
        document_id="DOC-006", title="Email Approval Thread",
        text=(
            "An email thread recovered from the finance system shows approval messages "
            "for the ghost employee's setup sent from Rachel Voss's email address. "
            "Header analysis by IT shows the messages originated from an internal IP "
            "address assigned to a terminal in the IT server room — not Voss's workstation. "
            "The emails were sent on a Saturday when Voss was confirmed out of the country."
        ),
        unlock_keywords=["approval email"],
        discovered_keywords=["login access logs"],
        evidence_items=[build_evidence_item("EV-FOR", "Forged Approval Emails",
            "Approval emails sent from Voss's account originated from the IT server "
            "room on a Saturday when Voss was out of the country.",
            "DOC-006", is_key_evidence=True)],
    )


def _ge_it_maintenance() -> Document:
    return Document(
        document_id="DOC-007", title="IT Maintenance Report",
        text=(
            "IT maintenance logs show Tom Greer performed scheduled maintenance on "
            "the finance workstation cluster on the Saturday the forged emails were "
            "sent. Maintenance records note that Greer had temporary elevated access "
            "to all finance accounts for a four hour window. The maintenance request "
            "was submitted and approved by Greer himself under an automated approval "
            "rule for low-priority tasks."
        ),
        unlock_keywords=["login access logs"],
        discovered_keywords=["approval email"],
        evidence_items=[build_evidence_item("EV-IT", "IT Maintenance Log",
            "Greer had elevated access to all finance accounts on the day the forged "
            "emails were sent. Maintenance request was self-approved.", "DOC-007")],
    )


def _ge_finance_review() -> Document:
    return Document(
        document_id="DOC-008", title="Finance Review Summary",
        text=(
            "A review of the receiving bank account shows it was opened in the name "
            "of a shell entity with no verifiable address. Withdrawals were made in "
            "cash at ATMs within two miles of the company office. Surveillance from "
            "one ATM location shows Tom Greer making a withdrawal on the same day "
            "as the second paycheck deposit. Greer has not provided an explanation "
            "for his presence at that location."
        ),
        unlock_keywords=["audit report"],
        discovered_keywords=["badge entry logs"],
        evidence_items=[build_evidence_item("EV-ATM", "ATM Surveillance",
            "Greer photographed at ATM withdrawing from the ghost employee's account "
            "on the same day as the second paycheck deposit.", "DOC-008")],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CASE 3 — SILENT WITNESS
# Keywords: traffic incident report, smart home audio, doorbell camera log
#           -> vehicle damage report, delivery route history, system settings log
# ═══════════════════════════════════════════════════════════════════════════════

def _build_case_silent_witness() -> CaseData:
    return CaseData(
        title="Silent Witness",
        intro_text=(
            "A driver struck a pedestrian and fled the scene. Nearby smart home and "
            "camera records initially seemed to support one timeline, but investigators "
            "suspect the recorded times were manipulated. Search the available records, "
            "unlock documents, collect evidence, and identify the real driver."
        ),
        suspects=["Carl Denning", "Priya Nath", "Owen Marsh"],
        documents=[
            _sw_incident_report(),
            _sw_witness_statement(),
            _sw_smart_home_audio(),
            _sw_doorbell_camera(),
            _sw_delivery_route(),
            _sw_vehicle_damage(),
            _sw_phone_call_logs(),
            _sw_system_settings(),
        ],
        starting_keywords=[
            "traffic incident report",
            "smart home audio",
            "doorbell camera log",
        ],
        solution=CaseSolution(
            correct_suspect="Carl Denning",
            required_evidence_ids={"EV-AUD", "EV-CLK", "EV-DAM"},
        ),
    )


def _sw_incident_report() -> Document:
    return Document(
        document_id="DOC-001", title="Traffic Incident Report",
        text=(
            "A pedestrian was struck at the corner of Birch Lane and Holloway Drive "
            "at an estimated time of 9:20 PM based on the 911 call received. The victim "
            "sustained serious injuries and was transported to Mercy General. No driver "
            "remained at the scene. A neighbor reported hearing the impact but the "
            "doorbell camera across the street showed no vehicle at 9:20 PM. "
            "Investigators noted the discrepancy and flagged smart home records for review."
        ),
        unlock_keywords=["traffic incident report"],
        discovered_keywords=["smart home audio", "vehicle damage report"],
        evidence_items=[build_evidence_item("EV-INC", "Incident Report",
            "Pedestrian struck at Birch Lane and Holloway Drive. 911 call at 9:20 PM "
            "but doorbell camera showed no vehicle at that time.", "DOC-001")],
    )


def _sw_witness_statement() -> Document:
    return Document(
        document_id="DOC-002", title="Witness Statement",
        text=(
            "A resident of Birch Lane stated she heard a loud impact and the sound of "
            "a vehicle accelerating away at approximately 9:08 PM. She noted the time "
            "because her television program had just ended. She described the vehicle "
            "as a dark SUV. She did not see the plate but said the vehicle turned north "
            "onto Holloway Drive immediately after the impact."
        ),
        unlock_keywords=["traffic incident report"],
        discovered_keywords=["doorbell camera log", "delivery route history"],
        evidence_items=[build_evidence_item("EV-WIT", "Witness Statement",
            "Witness heard impact at 9:08 PM and saw a dark SUV turn north on "
            "Holloway Drive.", "DOC-002")],
    )


def _sw_smart_home_audio() -> Document:
    return Document(
        document_id="DOC-003", title="Smart Home Audio Transcript",
        text=(
            "A smart speaker in the residence at 14 Birch Lane recorded an audio event "
            "at 9:07 PM described by forensic analysis as consistent with a vehicle "
            "impact — a sharp collision sound followed by acceleration. The device "
            "timestamp is drawn from an internet time server and cannot be manually "
            "overridden by the homeowner. The recording ends with the sound of tires "
            "on pavement heading north."
        ),
        unlock_keywords=["smart home audio"],
        discovered_keywords=["doorbell camera log", "system settings log"],
        evidence_items=[build_evidence_item("EV-AUD", "Smart Home Audio Recording",
            "Smart speaker recorded a collision sound at 9:07 PM on a server-synced "
            "clock that cannot be manually changed.",
            "DOC-003", is_key_evidence=True)],
    )


def _sw_doorbell_camera() -> Document:
    return Document(
        document_id="DOC-004", title="Doorbell Camera Footage Log",
        text=(
            "The doorbell camera at 17 Birch Lane shows no vehicle at 9:20 PM, which "
            "was initially used to suggest no incident occurred at that time. However "
            "the camera's internal clock was found to be 14 minutes behind actual time. "
            "Adjusting for this offset places the camera's negative result at 9:06 PM — "
            "before the incident — and shows a dark SUV passing at 9:21 PM adjusted "
            "time, consistent with 9:07 PM actual."
        ),
        unlock_keywords=["doorbell camera log"],
        discovered_keywords=["system settings log", "vehicle damage report"],
        evidence_items=[build_evidence_item("EV-CAM", "Doorbell Camera Log",
            "Camera clock was 14 minutes slow. Adjusted footage shows a dark SUV "
            "consistent with the 9:07 PM impact time.", "DOC-004")],
    )


def _sw_delivery_route() -> Document:
    return Document(
        document_id="DOC-005", title="Delivery Route History",
        text=(
            "GPS route history for a delivery driver active in the area shows no "
            "vehicles matching the described dark SUV on Birch Lane between 9:00 PM "
            "and 9:30 PM except one: a vehicle registered to Carl Denning that made "
            "an unscheduled stop near Holloway Drive at 9:06 PM and then traveled "
            "north at high speed. Denning is not listed as a delivery driver and has "
            "no documented reason to be in that area."
        ),
        unlock_keywords=["delivery route history"],
        discovered_keywords=["vehicle damage report", "system settings log"],
        evidence_items=[build_evidence_item("EV-RTE", "Delivery Route GPS Data",
            "Carl Denning's vehicle made an unscheduled stop near Holloway Drive at "
            "9:06 PM and accelerated north — no documented reason to be in the area.",
            "DOC-005")],
    )


def _sw_vehicle_damage() -> Document:
    return Document(
        document_id="DOC-006", title="Vehicle Damage Report",
        text=(
            "Carl Denning's dark SUV was inspected following an anonymous tip. The "
            "vehicle had fresh damage to the front-left bumper consistent with a "
            "pedestrian impact — soft tissue transfer, paint scraping at hip height, "
            "and a cracked fog light housing. Denning claimed the damage occurred in "
            "a parking lot the previous week but no claim was filed and no witnesses "
            "support this account."
        ),
        unlock_keywords=["vehicle damage report"],
        discovered_keywords=["delivery route history"],
        evidence_items=[build_evidence_item("EV-DAM", "Vehicle Damage Report",
            "Denning's SUV had fresh front-left damage consistent with a pedestrian "
            "impact at hip height. No prior claim or witnesses support his parking "
            "lot explanation.", "DOC-006", is_key_evidence=True)],
    )


def _sw_phone_call_logs() -> Document:
    return Document(
        document_id="DOC-007", title="Phone Call Logs",
        text=(
            "Carl Denning's phone records show a call placed at 9:09 PM lasting "
            "three minutes to a number registered to Owen Marsh, Denning's brother-in-law. "
            "Cell tower data places Denning's phone near Holloway Drive at 9:07 PM. "
            "Marsh has not cooperated with investigators. A text message sent at "
            "9:13 PM from Denning's phone reads: 'Need you to say I was at yours tonight.'"
        ),
        unlock_keywords=["smart home audio"],
        discovered_keywords=["delivery route history", "vehicle damage report"],
        evidence_items=[build_evidence_item("EV-PHN", "Phone Call and Text Records",
            "Denning's phone near Holloway Drive at 9:07 PM. Text to Marsh at 9:13 PM "
            "asks him to provide a false alibi.", "DOC-007")],
    )


def _sw_system_settings() -> Document:
    return Document(
        document_id="DOC-008", title="System Settings Log",
        text=(
            "The system settings log for the doorbell camera at 17 Birch Lane shows "
            "the device clock was manually set back 14 minutes at 9:31 PM — after the "
            "incident. The change was made via the homeowner app logged into the account "
            "of Priya Nath. Nath states she did not make the change and that her phone "
            "was stolen earlier that day. A police report for the stolen phone was filed "
            "at 6:15 PM."
        ),
        unlock_keywords=["system settings log"],
        discovered_keywords=["doorbell camera log"],
        evidence_items=[build_evidence_item("EV-CLK", "Clock Manipulation Log",
            "Doorbell camera clock manually set back 14 minutes at 9:31 PM via Priya "
            "Nath's account — after the incident. Nath reported her phone stolen at 6:15 PM.",
            "DOC-008", is_key_evidence=True)],
    )
