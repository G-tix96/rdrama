from sqlalchemy import *
from sqlalchemy.orm import relationship
from files.__main__ import Base
from files.helpers.lazy import lazy
from files.helpers.const import *
import time

class BadgeDef(Base):
	__tablename__ = "badge_defs"

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String)
	description = Column(String)
	created_utc = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<BadgeDef(id={self.id})>"

	@property
	@lazy
	def path(self):
		if 20 < self.id < 28: return f"/i/{SITE_NAME}/patron_badges/{self.id}.webp"
		return f"/i/badges/{self.id}.webp"

class Badge(Base):

	__tablename__ = "badges"

	user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
	badge_id = Column(Integer, ForeignKey('badge_defs.id'), primary_key=True)
	description = Column(String)
	url = Column(String)
	created_utc = Column(Integer)

	user = relationship("User", back_populates="badges")
	badge = relationship("BadgeDef", primaryjoin="Badge.badge_id == BadgeDef.id")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs:
			kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<Badge(user_id={self.user_id}, badge_id={self.badge_id})>"

	@property
	@lazy
	def until(self):
		if self.badge_id == 28 and self.user.agendaposter != 1: return self.user.agendaposter
		if self.badge_id == 94: return self.user.progressivestack
		if self.badge_id == 95: return self.user.bird
		if self.badge_id == 96: return self.user.flairchanged
		if self.badge_id == 97: return self.user.longpost
		if self.badge_id == 98: return self.user.marseyawarded
		if self.badge_id == 109: return self.user.rehab
		if self.badge_id == 167: return self.user.owoify
		if self.badge_id == 168: return self.user.bite
		if self.badge_id == 169: return self.user.earlylife
		if self.badge_id == 170: return self.user.marsify
		if self.badge_id == 171: return self.user.rainbow

		return None

	@property
	@lazy
	def text(self):
		if self.badge_id == 28:
			if self.until: text = self.badge.description + " until"
			else: text = self.badge.description + " permanently"
		elif self.until:
			text = self.badge.description + " until"
		elif self.description:
			text = self.description
		elif self.badge.description:
			text = self.badge.description
		else:
			return self.name
		
		return f'{self.name} - {text}'

	@property
	@lazy
	def name(self):
		return self.badge.name

	@property
	@lazy
	def path(self):
		return self.badge.path

	@property
	@lazy
	def json(self):
		return {'text': self.text,
				'name': self.name,
				'url': self.url,
				'icon_url':self.path
				}
