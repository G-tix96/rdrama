from sqlalchemy import *
from files.__main__ import Base
from files.helpers.lazy import lazy
from files.helpers.const import *
import time


class Casino_Game(Base):
	__tablename__ = "casino_games"

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"))
	created_utc = Column(Integer)
	active = Column(Boolean, default=True)
	currency = Column(String)
	wager = Column(Integer)
	winnings = Column(Integer)
	kind = Column(String)
	game_state = Column(JSON)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs:
			kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<CasinoGame(id={self.id})>"
