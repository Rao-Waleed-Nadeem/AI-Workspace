from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    original_name = Column(
        String(255),
        nullable=False,
    )

    mime_type = Column(
        String(255),
        nullable=False,
    )

    storage_path = Column(
        String(500),
        nullable=False,
    )

    size = Column(
        BigInteger,
        nullable=False,
    )

    page_count = Column(
        Integer,
        nullable=False,
    )

    extracted_text = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="documents",
    )