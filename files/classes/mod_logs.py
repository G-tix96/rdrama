import time
from copy import deepcopy

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.const import *
from files.helpers.lazy import lazy
from files.helpers.regex import censor_slurs
from files.helpers.sorting_and_time import make_age_string

class ModAction(Base):
	__tablename__ = "modactions"
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"))
	kind = Column(String)
	target_user_id = Column(Integer, ForeignKey("users.id"))
	target_submission_id = Column(Integer, ForeignKey("submissions.id"))
	target_comment_id = Column(Integer, ForeignKey("comments.id"))
	_note=Column(String)
	created_utc = Column(Integer)

	user = relationship("User", primaryjoin="User.id==ModAction.user_id")
	target_user = relationship("User", primaryjoin="User.id==ModAction.target_user_id")
	target_post = relationship("Submission")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<ModAction(id={self.id})>"

	@property
	@lazy
	def age_string(self):
		return make_age_string(self.created_utc)

	@property
	def note(self):
		if self.kind=="ban_user":
			if self.target_post: return f'for <a href="{self.target_post.permalink}">post</a>'
			elif self.target_comment_id: return f'for <a href="/comment/{self.target_comment_id}">comment</a>'
			else: return self._note
		else:
			return self._note or ""

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
		return f"{SITE_FULL}/log/{self.id}"

ACTIONTYPES = {
	'chud': {
		"str": 'chudded {self.target_link}', 
		"icon": 'fa-snooze', 
		"color": 'bg-danger'
	},
	'approve_app': {
		"str": 'approved an application by {self.target_link}', 
		"icon": 'fa-robot', 
		"color": 'bg-success'
	},
	'badge_grant': {
		"str": 'granted badge to {self.target_link}', 
		"icon": 'fa-badge', 
		"color": 'bg-success'
	},
	'badge_remove': {
		"str": 'removed badge from {self.target_link}', 
		"icon": 'fa-badge', 
		"color": 'bg-danger'
	},
	'ban_comment': {
		"str": 'removed {self.target_link}', 
		"icon": 'fa-comment', 
		"color": 'bg-danger'
	},
	'ban_domain': {
		"str": 'banned a domain', 
		"icon": 'fa-globe', 
		"color": 'bg-danger'
	},
	'ban_post': {
		"str": 'removed post {self.target_link}', 
		"icon": 'fa-feather-alt', 
		"color": 'bg-danger'
	},
	'ban_user': {
		"str": 'banned user {self.target_link}', 
		"icon": 'fa-user-slash', 
		"color": 'bg-danger'
	},
	'club_allow': {
		"str": 'allowed user {self.target_link} into the {cc}', 
		"icon": 'fa-golf-club', 
		"color": 'bg-success'
	},
	'club_ban': {
		"str": 'disallowed user {self.target_link} from the {cc}', 
		"icon": 'fa-golf-club', 
		"color": 'bg-danger'
	},
	'delete_report': {
		"str": 'deleted report on {self.target_link}', 
		"icon": 'fa-flag', 
		"color": 'bg-danger'
	},
	'disable_Bots': {
		"str": 'disabled Bots', 
		"icon": 'fa-robot', 
		"color": 'bg-danger'
	},
	'disable_Fart mode': {
		"str": 'disabled fart mode', 
		"icon": 'fa-gas-pump-slash', 
		"color": 'bg-danger'
	},
	'disable_Read-only mode': {
		"str": 'disabled readonly mode', 
		"icon": 'fa-book', 
		"color": 'bg-danger'
	},
	'disable_Signups': {
		"str": 'disabled Signups', 
		"icon": 'fa-users', 
		"color": 'bg-danger'
	},
	'disable_login_required': {
		"str": 'disabled Login Required', 
		"icon": 'fa-users', 
		"color": 'bg-danger'
	},
	'disable_under_attack': {
		"str": 'disabled under attack mode', 
		"icon": 'fa-shield', 
		"color": 'bg-muted'
	},
	'distinguish_comment': {
		"str": 'distinguished {self.target_link}', 
		"icon": 'fa-crown', 
		"color": 'bg-success'
	},
	'distinguish_post': {
		"str": 'distinguished {self.target_link}', 
		"icon": 'fa-crown', 
		"color": 'bg-success'
	},
	'distribute': {
		"str": 'distributed bet winnings to voters on {self.target_link}', 
		"icon": 'fa-dollar-sign', 
		"color": 'bg-success'
	},
	'clear_internal_cache': {
		"str": 'cleared internal cache', 
		"icon": 'fa-trash-alt', 
		"color": 'bg-muted'
	},
	'edit_post': {
		"str": 'edited {self.target_link}', 
		"icon": 'fa-edit', 
		"color": 'bg-primary'
	},
	'enable_Bots': {
		"str": 'enabled Bots', 
		"icon": 'fa-robot', 
		"color": 'bg-success'
	},
	'enable_Fart mode': {
		"str": 'enabled fart mode', 
		"icon": 'fa-gas-pump', 
		"color": 'bg-success'
	},
	'enable_Read-only mode': {
		"str": 'enabled readonly mode', 
		"icon": 'fa-book', 
		"color": 'bg-success'
	},
	'enable_Signups': {
		"str": 'enabled Signups', 
		"icon": 'fa-users', 
		"color": 'bg-success'
	},
	'enable_login_required': {
		"str": 'enabled Login Required', 
		"icon": 'fa-users', 
		"color": 'bg-success'
	},
	'enable_under_attack': {
		"str": 'enabled under attack mode', 
		"icon": 'fa-shield', 
		"color": 'bg-success'
	},
	'flair_post': {
		"str": 'set a flair on {self.target_link}', 
		"icon": 'fa-tag', 
		"color": 'bg-primary'
	},
	'link_accounts': {
		"str": 'linked {self.target_link}', 
		"icon": 'fa-link', 
		"color": 'bg-success'
	},
	'delink_accounts': {
		"str": 'delinked {self.target_link}',
		"icon": 'fa-link-slash',
		"color": 'bg-danger'
	},
	'make_admin': {
		"str": 'made {self.target_link} an admin', 
		"icon": 'fa-user-crown', 
		"color": 'bg-success'
	},
	'mod_mute_user': {
		"str": 'muted reports from user {self.target_link}',
		"icon": 'fa-file-signature',
		"color": 'bg-danger'
	},
	'mod_unmute_user': {
		"str": 'unmuted reports from user {self.target_link}',
		"icon": 'fa-file-signature',
		"color": 'bg-success'
	},
	'monthly': {
		"str": 'distributed monthly marseybux', 
		"icon": 'fa-sack-dollar', 
		"color": 'bg-success'
	},
	'move_hole': {
		"str": 'changed hole of {self.target_link}', 
		"icon": 'fa-manhole', 
		"color": 'bg-primary'
	},
	'nuke_user': {
		"str": 'removed all content of {self.target_link}', 
		"icon": 'fa-radiation-alt', 
		"color": 'bg-danger'
	},
	'pin_comment': {
		"str": 'pinned {self.target_link}', 
		"icon": 'fa-thumbtack fa-rotate--45', 
		"color": 'bg-success'
	},
	'pin_post': {
		"str": 'pinned post {self.target_link}', 
		"icon": 'fa-thumbtack fa-rotate--45', 
		"color": 'bg-success'
	},
	'clear_cloudflare_cache': {
		"str": 'cleared cloudflare cache', 
		"icon": 'fa-cloudflare', 
		"color": 'bg-muted'
	},
	'reject_app': {
		"str": 'rejected an application request by {self.target_link}', 
		"icon": 'fa-robot', 
		"color": 'bg-muted'
	},
	'remove_admin': {
		"str": 'removed {self.target_link} as admin', 
		"icon": 'fa-user-crown', 
		"color": 'bg-danger'
	},
	'revert': {
		"str": 'reverted {self.target_link} mod actions', 
		"icon": 'fa-history', 
		"color": 'bg-danger'
	},
	'revoke_app': {
		"str": 'revoked an application by {self.target_link}', 
		"icon": 'fa-robot', 
		"color": 'bg-muted'
	},
	'set_flair_locked': {
		"str": "set {self.target_link}'s flair (locked)", 
		"icon": 'fa-award', 
		"color": 'bg-primary'
	},
	'set_flair_notlocked': {
		"str": "set {self.target_link}'s flair (not locked)", 
		"icon": 'fa-award', 
		"color": 'bg-primary'
	},
	'set_nsfw': {
		"str": 'set nsfw on post {self.target_link}', 
		"icon": 'fa-eye-evil', 
		"color": 'bg-danger'
	},
	'set_nsfw_comment': {
		"str": 'set nsfw on a {self.target_link}', 
		"icon": 'fa-eye-evil', 
		"color": 'bg-danger'
	},
	'shadowban': {
		"str": 'shadowbanned {self.target_link}', 
		"icon": 'fa-eye-slash', 
		"color": 'bg-danger'
	},
	'unchud': {
		"str": 'unchudded {self.target_link}', 
		"icon": 'fa-snooze', 
		"color": 'bg-success'
	},
	'unban_comment': {
		"str": 'reinstated {self.target_link}', 
		"icon": 'fa-comment', 
		"color": 'bg-success'
	},
	'unban_domain': {
		"str": 'unbanned a domain', 
		"icon": 'fa-globe', 
		"color": 'bg-success'
	},
	'unban_post': {
		"str": 'reinstated post {self.target_link}', 
		"icon": 'fa-feather-alt', 
		"color": 'bg-success'
	},
	'unban_user': {
		"str": 'unbanned user {self.target_link}', 
		"icon": 'fa-user', 
		"color": 'bg-success'
	},
	'undistinguish_comment': {
		"str": 'un-distinguished {self.target_link}', 
		"icon": 'fa-crown', 
		"color": 'bg-muted'
	},
	'undistinguish_post': {
		"str": 'un-distinguished {self.target_link}', 
		"icon": 'fa-crown', 
		"color": 'bg-muted'
	},
	'unnuke_user': {
		"str": 'approved all content of {self.target_link}', 
		"icon": 'fa-radiation-alt', 
		"color": 'bg-success'
	},
	'unpin_comment': {
		"str": 'unpinned {self.target_link}', 
		"icon": 'fa-thumbtack fa-rotate--45', 
		"color": 'bg-muted'
	},
	'unpin_post': {
		"str": 'unpinned post {self.target_link}', 
		"icon": 'fa-thumbtack fa-rotate--45', 
		"color": 'bg-muted'
	},
	'unset_nsfw': {
		"str": 'un-set nsfw on post {self.target_link}', 
		"icon": 'fa-eye-evil', 
		"color": 'bg-success'
	},
	'unset_nsfw_comment': {
		"str": 'un-set nsfw on a {self.target_link}', 
		"icon": 'fa-eye-evil', 
		"color": 'bg-success'
	},
	'unshadowban': {
		"str": 'unshadowbanned {self.target_link}', 
		"icon": 'fa-eye', 
		"color": 'bg-success'
	},
	'update_hat': {
		"str": 'updated hat image', 
		"icon": 'fa-hat-cowboy', 
		"color": 'bg-success'
	},
	'update_marsey': {
		"str": 'updated marsey', 
		"icon": 'fa-cat', 
		"color": 'bg-success'
	},
	'club_post': {
		"str": 'moved post {self.target_link} to the {cc}', 
		"icon": 'fa-club', 
		"color": 'bg-success'
	},
	'unclub_post': {
		"str": 'removed post {self.target_link} from the {cc}', 
		"icon": 'fa-club', 
		"color": 'bg-muted'
	},
}

ACTIONTYPES2 = deepcopy(ACTIONTYPES)
ACTIONTYPES2.pop("shadowban")
ACTIONTYPES2.pop("unshadowban")
