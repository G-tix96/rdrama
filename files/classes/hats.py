from sqlalchemy import *
from sqlalchemy.orm import relationship
from files.__main__ import Base
from files.helpers.lazy import lazy
from files.helpers.regex import censor_slurs
from flask import g

class HatDef(Base):
	__tablename__ = "hat_defs"

	id = Column(Integer, primary_key=True)
	name = Column(String)
	description = Column(String)
	author_id = Column(Integer, ForeignKey('users.id'))
	price = Column(Integer)

	author = relationship("User", primaryjoin="HatDef.author_id == User.id", back_populates="designed_hats")

	@property
	@lazy
	def number_sold(self):
		return g.db.query(Hat).filter_by(hat_id=self.id).count()

	@lazy
	def censored_description(self, v):
		return censor_slurs(self.description, v)

class Hat(Base):
	__tablename__ = "hats"

	user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
	hat_id = Column(Integer, ForeignKey('hat_defs.id'), primary_key=True)