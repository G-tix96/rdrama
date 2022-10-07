from sqlalchemy import *
from files.__main__ import Base
import time

class BannedDomain(Base):

	__tablename__ = "banneddomains"
	domain = Column(String, primary_key=True)
	reason = Column(String)
	created_utc = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<BannedDomain(domain={self.domain})>"
