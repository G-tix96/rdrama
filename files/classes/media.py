from sqlalchemy import *
from files.__main__ import Base
import time

class Media(Base):

	__tablename__ = "media"
	kind = Column(String, primary_key=True)
	filename = Column(String, primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"))
	created_utc = Column(Integer)
	size = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<Streamer(id={self.id})>"
