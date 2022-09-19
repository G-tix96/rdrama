from sqlalchemy import *
from sqlalchemy.orm import relationship
from files.__main__ import Base
import time

class Follow(Base):
	__tablename__ = "follows"
	target_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	created_utc = Column(Integer, default=int(time.time()))

	user = relationship("User", uselist=False, primaryjoin="User.id==Follow.user_id", back_populates="following")
	target = relationship("User", uselist=False, primaryjoin="User.id==Follow.target_id", back_populates="followers")

	def __repr__(self):
		return f"<Follow(id={self.id})>"