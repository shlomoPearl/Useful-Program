from sqlalchemy import Column, Text, LargeBinary, DateTime
from db import Base
from sqlalchemy.sql import func


class GmailUser(Base):
    __tablename__ = "users"
    id = Column(Text, primary_key=True, index=True)
    token = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
