from sqlalchemy import *
from sqlalchemy.orm import relationship
from files.__main__ import Base
import time

class Exile(Base):

	__tablename__ = "exiles"
	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	sub = Column(String, ForeignKey("subs.name"), primary_key=True)
	exiler_id = Column(Integer, ForeignKey("users.id"))
	created_utc = Column(Integer)

	exiler = relationship("User", primaryjoin="User.id==Exile.exiler_id")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<Exile(user_id={self.user_id}, sub={self.sub})>"