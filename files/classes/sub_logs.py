import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.const import *
from files.helpers.lazy import lazy
from files.helpers.regex import censor_slurs
from files.helpers.sorting_and_time import make_age_string

class SubAction(Base):
	__tablename__ = "subactions"
	id = Column(Integer, primary_key=True)
	sub = Column(String, ForeignKey("subs.name"))
	user_id = Column(Integer, ForeignKey("users.id"))
	kind = Column(String)
	target_user_id = Column(Integer, ForeignKey("users.id"))
	target_submission_id = Column(Integer, ForeignKey("submissions.id"))
	target_comment_id = Column(Integer, ForeignKey("comments.id"))
	_note=Column(String)
	created_utc = Column(Integer)

	user = relationship("User", primaryjoin="User.id==SubAction.user_id")
	target_user = relationship("User", primaryjoin="User.id==SubAction.target_user_id")
	target_post = relationship("Submission")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def age_string(self):
		return make_age_string(self.created_utc)

	@property
	@lazy
	def string(self):
		output = ACTIONTYPES[self.kind]["str"].format(self=self)
		if self._note: output += f" <i>({self._note})</i>"
		return output

	@property
	@lazy
	def target_link(self):
		if self.target_user: return f'<a href="{self.target_user.url}">{self.target_user.username}</a>'
		elif self.target_post:
			return censor_slurs(f'<a href="{self.target_post.permalink}">{self.target_post.title_html}</a>', None)
		elif self.target_comment_id: return f'<a href="/comment/{self.target_comment_id}?context=8#context">comment</a>'

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
		return f"{SITE_FULL}/h/{self.sub}/log/{self.id}"

ACTIONTYPES = {
	'exile_user': {
		"str": 'exiled user {self.target_link}', 
		"icon": 'fa-user-slash', 
		"color": 'bg-danger'
	},
	'unexile_user': {
		"str": 'unexiled user {self.target_link}', 
		"icon": 'fa-user', 
		"color": 'bg-success'
	},
	'make_mod': {
		"str": 'made {self.target_link} a mod', 
		"icon": 'fa-user-crown', 
		"color": 'bg-success'
	},
	'remove_mod': {
		"str": 'removed {self.target_link} as mod', 
		"icon": 'fa-user-crown', 
		"color": 'bg-danger'
	},
	'kick_post': {
		"str": 'kicked post {self.target_link}', 
		"icon": 'fa-feather-alt', 
		"color": 'bg-danger'
	},
	'move_chudrama': {
		"str": 'moved post {self.target_link} to <a href="/h/chudrama">/h/chudrama</a>', 
		"icon": 'fa-feather-alt', 
		"color": 'bg-danger'
	},
	'flair_post': {
		"str": 'set a flair on {self.target_link}', 
		"icon": 'fa-tag', 
		"color": 'bg-primary'
	},
	'edit_sidebar': {
		"str": 'edited the sidebar', 
		"icon": 'fa-columns', 
		"color": 'bg-primary'
	},
	'edit_css': {
		"str": 'edited the css', 
		"icon": 'fa-css3-alt', 
		"color": 'bg-primary'
	},
	'change_banner': {
		"str": 'changed the banner', 
		"icon": 'fa-landscape', 
		"color": 'bg-primary'
	},
	'change_sidebar_image': {
		"str": 'changed the sidebar image', 
		"icon": 'fa-image', 
		"color": 'bg-primary'
	},
	'change_marsey': {
		"str": 'changed the hole marsey', 
		"icon": 'fa-cat', 
		"color": 'bg-primary'
	},
	'pin_post': {
		"str": 'pinned post {self.target_link}', 
		"icon": 'fa-thumbtack fa-rotate--45', 
		"color": 'bg-success'
	},
	'unpin_post': {
		"str": 'unpinned post {self.target_link}', 
		"icon": 'fa-thumbtack fa-rotate--45', 
		"color": 'bg-muted'
	},
	'pin_comment': {
		"str": 'pinned {self.target_link}', 
		"icon": 'fa-thumbtack fa-rotate--45', 
		"color": 'bg-success'
	},
	'unpin_comment': {
		"str": 'unpinned {self.target_link}', 
		"icon": 'fa-thumbtack fa-rotate--45', 
		"color": 'bg-muted'
	},
	'enable_stealth': {
		"str": 'enabled stealth mode', 
		"icon": 'fa-user-ninja', 
		"color": 'bg-primary'
	},
	'disable_stealth': {
		"str": 'disabled stealth mode', 
		"icon": 'fa-user-ninja', 
		"color": 'bg-muted'
	},
	'set_nsfw': {
		"str": 'set nsfw on post {self.target_link}', 
		"icon": 'fa-eye-evil', 
		"color": 'bg-danger'
	},
	'unset_nsfw': {
		"str": 'un-set nsfw on post {self.target_link}', 
		"icon": 'fa-eye-evil', 
		"color": 'bg-success'
	},
	'set_nsfw_comment': {
		"str": 'set nsfw on a {self.target_link}', 
		"icon": 'fa-eye-evil', 
		"color": 'bg-danger'
	},
	'unset_nsfw_comment': {
		"str": 'un-set nsfw on a {self.target_link}', 
		"icon": 'fa-eye-evil', 
		"color": 'bg-success'
	},
}
