import time

from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class Streamer(Base):
	__tablename__ = "streamers"
	id = Column(String, primary_key=True)
	created_utc = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)
	
	def __repr__(self):
		return f"<Streamer(id={self.id})>"
