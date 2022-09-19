from sqlalchemy import *
from files.__main__ import Base
import time

class Marsey(Base):
	__tablename__ = "marseys"

	name = Column(String, primary_key=True)
	author_id = Column(Integer, ForeignKey("users.id"))
	tags = Column(String)
	count = Column(Integer, default=0)
	submitter_id = Column(Integer, ForeignKey("users.id"))
	created_utc = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<Marsey(name={self.name})>"