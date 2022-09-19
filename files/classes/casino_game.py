from sqlalchemy import *
from files.__main__ import Base
import time


class Casino_Game(Base):
	__tablename__ = "casino_games"

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"))
	created_utc = Column(Integer, default=int(time.time()))
	active = Column(Boolean, default=True)
	currency = Column(String)
	wager = Column(Integer)
	winnings = Column(Integer)
	kind = Column(String)
	game_state = Column(JSON)

	def __repr__(self):
		return f"<CasinoGame(id={self.id})>"
