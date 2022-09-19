from sqlalchemy import *
from sqlalchemy.orm import relationship
from files.__main__ import Base
import time

class Subscription(Base):
	__tablename__ = "subscriptions"
	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	submission_id = Column(Integer, ForeignKey("submissions.id"), primary_key=True)
	created_utc = Column(Integer, default=int(time.time()))

	user = relationship("User", uselist=False)
	post = relationship("Submission", uselist=False)

	def __repr__(self):
		return f"<Subscription(id={self.id})>"