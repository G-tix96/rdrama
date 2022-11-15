import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.const import *
from files.helpers.lazy import lazy

class Lottery(Base):
	__tablename__ = "lotteries"

	id = Column(Integer, primary_key=True)
	is_active = Column(Boolean, default=False)
	ends_at = Column(Integer)
	prize = Column(Integer, default=0)
	tickets_sold = Column(Integer, default=0)
	winner_id = Column(Integer, ForeignKey("users.id"))
	created_utc = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<Lottery(id={self.id})>"

	@property
	@lazy
	def timeleft(self):
		if not self.is_active:
			return 0

		epoch_time = int(time.time())
		remaining_time = self.ends_at - epoch_time

		return 0 if remaining_time < 0 else remaining_time

	@property
	@lazy
	def stats(self):
		return {"active": self.is_active, "timeLeft": self.timeleft, "prize": self.prize, "ticketsSoldThisSession": self.tickets_sold,}
