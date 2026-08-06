from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    BigInteger,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    message_id = Column(
        Integer,
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
    )

    attachment_type = Column(
        String(50),
        nullable=False,
    )

    mime_type = Column(
        String(255),
        nullable=False,
    )

    original_name = Column(
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

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    message = relationship(
        "Message",
        back_populates="attachments",
    )