from sqlalchemy import *
from sqlalchemy.orm import relationship

from files.classes import Base
from files.helpers.const import *

if SITE_NAME == 'WPD': default_darkmode = True
else: default_darkmode = False

class EventUser(Base):
	__tablename__ = "event_users"
	id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	user = relationship("User", primaryjoin="EventUser.id == User.id")
	event_music = Column(Boolean, default=True, nullable=False)

	# start event specific columns
	event_darkmode = Column(Boolean, default=default_darkmode, nullable=False)
	# end event specific columns

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"
