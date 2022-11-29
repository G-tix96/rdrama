from sqlalchemy import *
from sqlalchemy.orm import relationship

from files.classes import Base

class EventUser(Base):
	__tablename__ = "event"
	id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	user = relationship("User", primaryjoin="EventUser.id == User.id", lazy="joined")
	event_music = Column(Boolean, default=True, nullable=False)

	# start event specific columns

	# end event specific columns

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<Event(id={self.id})>"
