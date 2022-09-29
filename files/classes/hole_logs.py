from sqlalchemy import *
from sqlalchemy.orm import relationship
from files.__main__ import Base
import time
from files.helpers.lazy import lazy
from files.helpers.const import *
from files.helpers.regex import censor_slurs

class HoleAction(Base):
	__tablename__ = "holeactions"
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"))
	kind = Column(String)
	target_user_id = Column(Integer, ForeignKey("users.id"))
	target_submission_id = Column(Integer, ForeignKey("submissions.id"))
	_note=Column(String)
	created_utc = Column(Integer)

	user = relationship("User", primaryjoin="User.id==HoleAction.user_id")
	target_user = relationship("User", primaryjoin="User.id==HoleAction.target_user_id")
	target_post = relationship("Submission")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<HoleAction(id={self.id})>"

	@property
	@lazy
	def age_string(self):

		age = int(time.time()) - self.created_utc

		if age < 60:
			return "just now"
		elif age < 3600:
			minutes = int(age / 60)
			return f"{minutes}m ago"
		elif age < 86400:
			hours = int(age / 3600)
			return f"{hours}hr ago"
		elif age < 2678400:
			days = int(age / 86400)
			return f"{days}d ago"

		now = time.gmtime()
		ctd = time.gmtime(self.created_utc)

		months = now.tm_mon - ctd.tm_mon + 12 * (now.tm_year - ctd.tm_year)
		if now.tm_mday < ctd.tm_mday:
			months -= 1

		if months < 12:
			return f"{months}mo ago"
		else:
			years = int(months / 12)
			return f"{years}yr ago"

	@property
	def note(self):

		if self.kind=="ban_user":
			if self.target_post: return f'for <a href="{self.target_post.permalink}">post</a>'
			else: return self._note
		else:
			return self._note or ""

	@note.setter
	def note(self, x):
		self._note=x

	@property
	@lazy
	def string(self):

		output = ACTIONTYPES[self.kind]["str"].format(self=self, cc=CC_TITLE)

		if self.note: output += f" <i>({self.note})</i>"

		return output

	@property
	@lazy
	def target_link(self):
		if self.target_user: return f'<a href="{self.target_user.url}">{self.target_user.username}</a>'
		elif self.target_post:
			if self.target_post.club: return f'<a href="{self.target_post.permalink}">{CC} ONLY</a>'
			return censor_slurs(f'<a href="{self.target_post.permalink}">{self.target_post.title_html}</a>', None)

	@property
	@lazy
	def icon(self):
		return ACTIONTYPES[self.kind]['icon']

	@property
	@lazy
	def color(self):
		return ACTIONTYPES[self.kind]['color']

	@property
	@lazy
	def permalink(self):
		return f"{SITE_FULL}/log/{self.id}"

ACTIONTYPES = {
	'ban_user': {
		"str": 'banned user {self.target_link}', 
		"icon": 'fa-user-slash', 
		"color": 'bg-danger'
	},
	'unban_user': {
		"str": 'unbanned user {self.target_link}', 
		"icon": 'fa-user', 
		"color": 'bg-success'
	},
	'make_admin': {
		"str": 'made {self.target_link} admin', 
		"icon": 'fa-user-crown', 
		"color": 'bg-success'
	},
	'remove_admin': {
		"str": 'removed {self.target_link} as admin', 
		"icon": 'fa-user-crown', 
		"color": 'bg-danger'
	},
	'ban_post': {
		"str": 'removed post {self.target_link}', 
		"icon": 'fa-feather-alt', 
		"color": 'bg-danger'
	},
	'flair_post': {
		"str": 'set a flair on {self.target_link}', 
		"icon": 'fa-tag', 
		"color": 'bg-primary'
	},
	'change_sidebar': {
		"str": 'changed the sidebar', 
		"icon": 'fa-columns', 
		"color": 'bg-primary'
	},
	'change_css': {
		"str": 'changed the css', 
		"icon": 'fa-columns', 
		"color": 'bg-primary'
	},
	'change_banner': {
		"str": 'changed the banner', 
		"icon": 'fa-columns', 
		"color": 'bg-primary'
	},
	'change_sidebar_image': {
		"str": 'changed the sidebar image', 
		"icon": 'fa-columns', 
		"color": 'bg-primary'
	},
	'change_marsey': {
		"str": 'changed the hole marsey', 
		"icon": 'fa-columns', 
		"color": 'bg-primary'
	},
	'pin_post': {
		"str": 'pinned post {self.target_link}', 
		"icon": 'fa-thumbtack fa-rotate--45', 
		"color": 'bg-success'
	},
	'unpin_post': {
		"str": 'un-pinned post {self.target_link}', 
		"icon": 'fa-thumbtack fa-rotate--45', 
		"color": 'bg-muted'
	},
	'enable_stealth': {
		"str": 'changed the banner', 
		"icon": 'fa-columns', 
		"color": 'bg-primary'
	},
	'disable_stealth': {
		"str": 'changed the banner', 
		"icon": 'fa-columns', 
		"color": 'bg-primary'
	}
}