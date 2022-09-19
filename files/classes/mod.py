from sqlalchemy import *
from sqlalchemy.orm import relationship
from files.__main__ import Base
from files.helpers.lazy import *
import time

class Mod(Base):

	__tablename__ = "mods"
	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	sub = Column(String, ForeignKey("subs.name"), primary_key=True)
	created_utc = Column(Integer, default=int(time.time()))

	def __repr__(self):
		return f"<Mod(user_id={self.user_id}, sub={self.sub})>"