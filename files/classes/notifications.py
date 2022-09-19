from sqlalchemy import *
from sqlalchemy.orm import relationship
from files.__main__ import Base
import time

class Notification(Base):

	__tablename__ = "notifications"

	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	comment_id = Column(Integer, ForeignKey("comments.id"), primary_key=True)
	read = Column(Boolean, default=False)
	created_utc = Column(Integer, default=int(time.time()))

	comment = relationship("Comment")
	user = relationship("User")

	def __repr__(self):
		return f"<Notification(id={self.id})>"