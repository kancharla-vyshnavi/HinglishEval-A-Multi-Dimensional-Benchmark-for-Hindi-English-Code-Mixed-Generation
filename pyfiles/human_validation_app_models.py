"""
SQLAlchemy ORM models for HinglishEval Human Validation Platform.
Enforces strict schema constraints, unique constraints, and audit logging.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index
)
from sqlalchemy.orm import relationship
from .database import Base


class Response(Base):
    """
    Stores benchmark stimulus items (4,000 total).
    Note: 'model' is securely stored for post-hoc analysis and export,
    and must NEVER be serialized or returned in the annotator-facing APIs.
    """
    __tablename__ = "responses"

    id = Column(String(32), primary_key=True, index=True)  # e.g., RESP_0001
    item_index = Column(Integer, unique=True, nullable=False, index=True)  # 1..4000 stable order
    prompt_id = Column(Integer, nullable=False, index=True)  # 1..1000
    model = Column(String(64), nullable=False)  # Blinded from annotators
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    source_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    annotations = relationship("Annotation", back_populates="response_item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Response {self.id} (Item #{self.item_index})>"


class Annotator(Base):
    """
    Authorized evaluation actors (Annotator A, Annotator B, and Admin).
    """
    __tablename__ = "annotators"

    id = Column(String(32), primary_key=True)  # 'annotator_a', 'annotator_b', 'admin'
    username = Column(String(64), unique=True, nullable=False)
    display_name = Column(String(64), nullable=False)
    role = Column(String(32), nullable=False, default="annotator")  # 'annotator' or 'admin'
    access_code_hash = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    annotations = relationship("Annotation", back_populates="annotator_user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Annotator {self.id} ({self.display_name})>"


class Annotation(Base):
    """
    Human rating record.
    Unique constraint ensures exactly one rating record per (response_id, annotator_id).
    Completion is defined as all 6 dimensions populated with valid integers (1-5).
    """
    __tablename__ = "annotations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    response_id = Column(String(32), ForeignKey("responses.id", ondelete="CASCADE"), nullable=False, index=True)
    annotator_id = Column(String(32), ForeignKey("annotators.id", ondelete="CASCADE"), nullable=False, index=True)

    fluency = Column(Integer, nullable=True)
    code_mixing_naturalness = Column(Integer, nullable=True)
    hindi_grammar = Column(Integer, nullable=True)
    prompt_adherence = Column(Integer, nullable=True)
    spelling_consistency = Column(Integer, nullable=True)
    overall = Column(Integer, nullable=True)

    notes = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False, index=True)

    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    response_item = relationship("Response", back_populates="annotations")
    annotator_user = relationship("Annotator", back_populates="annotations")

    __table_args__ = (
        UniqueConstraint("response_id", "annotator_id", name="uq_response_annotator"),
        Index("idx_annotator_completion", "annotator_id", "is_completed"),
    )

    def check_is_completed(self) -> bool:
        """Verify if all six dimensions contain valid integer ratings between 1 and 5."""
        dims = [
            self.fluency,
            self.code_mixing_naturalness,
            self.hindi_grammar,
            self.prompt_adherence,
            self.spelling_consistency,
            self.overall
        ]
        return all(isinstance(v, int) and 1 <= v <= 5 for v in dims)

    def __repr__(self):
        return f"<Annotation resp={self.response_id} annotator={self.annotator_id} completed={self.is_completed}>"


class AnnotationAudit(Base):
    """
    Immutable audit trail recording every rating creation or modification.
    """
    __tablename__ = "annotation_audits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    response_id = Column(String(32), nullable=False, index=True)
    annotator_id = Column(String(32), nullable=False, index=True)
    action = Column(String(32), nullable=False)  # 'CREATE' or 'UPDATE'
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Audit {self.action} on {self.response_id} by {self.annotator_id}>"
