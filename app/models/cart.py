"""
Cart SQLAlchemy model for temporary session-based storage.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from app.database import Base


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    items = Column(JSON, nullable=False, default=list)
    total_amount = Column(Float, nullable=False, default=0.0)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self):
        return f"<Cart session={self.session_id} total={self.total_amount}>"
