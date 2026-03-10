"""
Agent Session Manager
Manages multi-turn diagnostic Agent state: tracks what info we have,
decides when to ask follow-up questions vs. when to run full analysis.
"""
import uuid
import time
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# ── What info we need before running full analysis ──────────────────────
REQUIRED_FIELDS = ["symptoms", "age", "sex"]
OPTIONAL_FIELDS = ["family_history", "duration", "variants"]

FOLLOWUP_QUESTIONS = {
    "age": {
        "question": "What is the patient's age?",
        "options": ["Child (0-12)", "Teenager (13-17)", "Young Adult (18-35)", "Adult (36-60)", "Senior (60+)"],
        "field": "age",
        "required": True,
    },
    "sex": {
        "question": "What is the patient's biological sex?",
        "options": ["Male", "Female", "Other / Prefer not to say"],
        "field": "sex",
        "required": True,
    },
    "duration": {
        "question": "How long have these symptoms been present?",
        "options": ["Less than 1 week", "1-4 weeks", "1-6 months", "6-12 months", "More than 1 year", "Since birth / lifelong"],
        "field": "duration",
        "required": False,
    },
    "family_history": {
        "question": "Is there any relevant family history of genetic or rare diseases?",
        "options": ["Yes, known family history", "Possible / unsure", "No known family history", "Adopted / unknown family history"],
        "field": "family_history",
        "required": False,
    },
    "severity": {
        "question": "How would you describe the overall symptom severity?",
        "options": ["Mild — manageable day to day", "Moderate — affecting daily life", "Severe — significantly debilitating", "Progressive — worsening over time"],
        "field": "severity",
        "required": False,
    },
}


class AgentSession:
    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.created_at = time.time()
        self.updated_at = time.time()

        # Collected clinical data
        self.symptoms: List[str] = []
        self.variants: List[Dict] = []
        self.patient_info: Dict = {}
        self.report_summary: str = ""

        # Conversation history
        self.messages: List[Dict] = []  # {role, content, type, ts}

        # Agent state
        self.state: str = "greeting"
        # greeting → collecting → questioning → analyzing → complete
        self.questions_asked: List[str] = []
        self.followup_count: int = 0
        self.max_followups: int = 3

        # Analysis results
        self.trace: List[Dict] = []
        self.report: Optional[Dict] = None
        self.clinvar_results: List[Dict] = []
        self.hpo_terms: List[Dict] = []

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "state": self.state,
            "symptoms": self.symptoms,
            "variants": self.variants,
            "patient_info": self.patient_info,
            "report_summary": self.report_summary,
            "messages": self.messages,
            "questions_asked": self.questions_asked,
            "followup_count": self.followup_count,
            "trace": self.trace,
            "report": self.report,
            "clinvar_results": self.clinvar_results,
            "hpo_terms": self.hpo_terms,
        }

    def add_message(self, role: str, content: str, msg_type: str = "text",
                    options: List[str] = None, metadata: dict = None):
        msg = {
            "id": str(uuid.uuid4())[:8],
            "role": role,
            "content": content,
            "type": msg_type,
            "ts": time.time(),
        }
        if options:
            msg["options"] = options
        if metadata:
            msg["metadata"] = metadata
        self.messages.append(msg)
        self.updated_at = time.time()
        return msg

    def update_from_user_input(self, text: str, selected_option: str = None):
        """Parse user message and extract clinical info"""
        value = selected_option or text

        # Try to map to a pending question field
        if self.questions_asked:
            last_q = self.questions_asked[-1]
            q_def = FOLLOWUP_QUESTIONS.get(last_q)
            if q_def:
                field = q_def["field"]
                self.patient_info[field] = value
                logger.info(f"[Session {self.session_id}] Set {field} = {value}")

        # Extract symptoms if in collecting state
        if self.state == "collecting" or not self.symptoms:
            # Parse comma/semicolon separated symptoms
            raw = text.replace(";", ",")
            parts = [p.strip() for p in raw.split(",") if len(p.strip()) > 2]
            if parts:
                self.symptoms.extend(parts)
                self.symptoms = list(dict.fromkeys(self.symptoms))  # dedup

    def get_next_question(self) -> Optional[Dict]:
        """Decide what to ask next. Returns None if we have enough info."""
        if self.followup_count >= self.max_followups:
            return None

        for key, q_def in FOLLOWUP_QUESTIONS.items():
            field = q_def["field"]
            already_asked = key in self.questions_asked
            already_have = self.patient_info.get(field)
            if not already_have and not already_asked:
                return {"key": key, **q_def}
        return None

    def is_ready_for_analysis(self) -> bool:
        """Check if we have enough info to run the full diagnostic pipeline."""
        has_symptoms = len(self.symptoms) > 0
        has_variants = len(self.variants) > 0
        has_basic = self.patient_info.get("age") and self.patient_info.get("sex")
        # Need symptoms OR variants, plus basic patient info
        return (has_symptoms or has_variants) and has_basic

    def add_trace_step(self, step: str, detail: str, data: dict = None):
        entry = {"step": step, "detail": detail, "ts": round(time.time() - self.created_at, 2)}
        if data:
            entry["data"] = data
        self.trace.append(entry)


# ── In-memory session store ──────────────────────────────────────────────
_sessions: Dict[str, AgentSession] = {}
SESSION_TTL = 3600  # 1 hour


def get_or_create_session(session_id: str = None) -> AgentSession:
    # Cleanup old sessions
    now = time.time()
    expired = [k for k, v in _sessions.items() if now - v.updated_at > SESSION_TTL]
    for k in expired:
        del _sessions[k]

    if session_id and session_id in _sessions:
        return _sessions[session_id]

    session = AgentSession(session_id)
    _sessions[session.session_id] = session
    return session


def get_session(session_id: str) -> Optional[AgentSession]:
    return _sessions.get(session_id)
