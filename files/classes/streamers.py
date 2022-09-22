from files.helpers.const import SITE

if SITE == 'pcmemes.net':
	from sqlalchemy import *
	from files.__main__ import Base

	class Streamer(Base):

		__tablename__ = "streamers"
		id = Column(String, primary_key=True)

		def __repr__(self):
			return f"<Streamer(id={self.id})>"