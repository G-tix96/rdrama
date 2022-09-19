from sqlalchemy import *
from files.__main__ import Base
import time

class BannedDomain(Base):

	__tablename__ = "banneddomains"
	domain = Column(String, primary_key=True)
	reason = Column(String)
	created_utc = Column(Integer, default=int(time.time()))

	def __repr__(self):
		return f"<BannedDomain(domain={self.domain})>"