from sqlalchemy import *
from sqlalchemy.orm import relationship
from files.__main__ import Base

class HatDef(Base):
	__tablename__ = "hat_defs"

	id = Column(Integer, primary_key=True)
	name = Column(String)
	description = Column(String)
	author_id = Column(Integer, ForeignKey('users.id'))
	price = Column(Integer)

	author = relationship("User", primaryjoin="HatDef.author_id == User.id")

class Hat(Base):
	__tablename__ = "hats"

	user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
	hat_id = Column(Integer, ForeignKey('hat_defs.id'), primary_key=True)