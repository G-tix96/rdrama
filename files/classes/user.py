from sqlalchemy.orm import deferred, aliased
from sqlalchemy.sql import func
from secrets import token_hex
import pyotp
from files.helpers.discord import remove_user
from files.helpers.media import *
from files.helpers.const import *
from files.classes.casino_game import Casino_Game
from files.helpers.sorting_and_time import *
from .alts import Alt
from .saves import *
from .notifications import Notification
from .award import AwardRelationship
from .follows import *
from .subscriptions import *
from .userblock import *
from .badges import *
from .clients import *
from .mod_logs import *
from .mod import *
from .exiles import *
from .sub_block import *
from .sub_subscription import *
from .sub_join import *
from .hats import *
from files.__main__ import Base, cache
from files.helpers.security import *
from copy import deepcopy
import random
from os import remove, path

class User(Base):
	__tablename__ = "users"

	if SITE == "pcmemes.net":
		basedcount = Column(Integer, default=0)
		pills = deferred(Column(String, default=""))

	id = Column(Integer, primary_key=True)
	username = Column(String)
	namecolor = Column(String, default=DEFAULT_COLOR)
	background = Column(String)
	customtitle = Column(String)
	customtitleplain = deferred(Column(String))
	titlecolor = Column(String, default=DEFAULT_COLOR)
	theme = Column(String, default=DEFAULT_THEME)
	themecolor = Column(String, default=DEFAULT_COLOR)
	cardview = Column(Boolean, default=CARD_VIEW)
	song = Column(String)
	highres = Column(String)
	profileurl = Column(String)
	bannerurl = Column(String)
	house = Column(String, default='')
	old_house = Column(String, default='')
	patron = Column(Integer, default=0)
	patron_utc = Column(Integer, default=0)
	verified = Column(String)
	verifiedcolor = Column(String)
	marseyawarded = Column(Integer)
	rehab = Column(Integer)
	longpost = Column(Integer)
	unblockable = Column(Boolean)
	bird = Column(Integer)
	email = deferred(Column(String))
	css = Column(String)
	profilecss = deferred(Column(String))
	passhash = deferred(Column(String))
	post_count = Column(Integer, default=0)
	comment_count = Column(Integer, default=0)
	received_award_count = Column(Integer, default=0)
	created_utc = Column(Integer)
	admin_level = Column(Integer, default=0)
	last_active = Column(Integer, default=0, nullable=False)
	coins_spent = Column(Integer, default=0)
	coins_spent_on_hats = Column(Integer, default=0)
	lootboxes_bought = Column(Integer, default=0)
	agendaposter = Column(Integer, default=0)
	is_activated = Column(Boolean, default=False)
	shadowbanned = Column(String)
	over_18 = Column(Boolean, default=False)
	hidevotedon = Column(Boolean, default=False)
	highlightcomments = Column(Boolean, default=True)
	poorcel = Column(Boolean, default=False)
	slurreplacer = Column(Boolean, default=True)
	flairchanged = Column(Integer)
	newtab = Column(Boolean, default=False)
	newtabexternal = Column(Boolean, default=True)
	reddit = Column(String, default='old.reddit.com')
	nitter = Column(Boolean)
	imginn = Column(Boolean)
	mute = Column(Boolean)
	unmutable = Column(Boolean)
	eye = Column(Boolean)
	alt = Column(Boolean)
	offsitementions = Column(Boolean, default=False, nullable=False)
	frontsize = Column(Integer, default=25)
	controversial = Column(Boolean, default=False)
	bio = deferred(Column(String))
	bio_html = Column(String)
	sig = deferred(Column(String))
	sig_html = Column(String)
	fp = Column(String)
	sigs_disabled = Column(Boolean)
	fish = Column(Boolean)
	progressivestack = Column(Integer)
	deflector = Column(Integer)
	friends = deferred(Column(String))
	friends_html = deferred(Column(String))
	enemies = deferred(Column(String))
	enemies_html = deferred(Column(String))
	is_banned = Column(Integer, default=0)
	unban_utc = Column(Integer, default=0)
	ban_reason = deferred(Column(String))
	is_muted = Column(Boolean, default=False, nullable=False)
	club_allowed = Column(Boolean)
	login_nonce = Column(Integer, default=0)
	reserved = deferred(Column(String))
	coins = Column(Integer, default=0)
	truecoins = Column(Integer, default=0)
	procoins = Column(Integer, default=0)
	mfa_secret = deferred(Column(String))
	is_private = Column(Boolean, default=False)
	stored_subscriber_count = Column(Integer, default=0)
	defaultsortingcomments = Column(String, default="top")
	defaultsorting = Column(String, default="hot")
	defaulttime = Column(String, default=DEFAULT_TIME_FILTER)
	is_nofollow = Column(Boolean, default=False)
	custom_filter_list = Column(String)
	discord_id = Column(String)
	original_username = Column(String)
	referred_by = Column(Integer, ForeignKey("users.id"))
	currently_held_lottery_tickets = Column(Integer, default=0)
	total_held_lottery_tickets = Column(Integer, default=0)
	total_lottery_winnings = Column(Integer, default=0)
	last_viewed_post_notifs = Column(Integer, default=0)
	last_viewed_log_notifs = Column(Integer, default=0)
	pronouns = Column(String, default='they/them')
	bite = Column(Integer)
	earlylife = Column(Integer)
	owoify = Column(Integer)
	marsify = Column(Integer, default=0)
	rainbow = Column(Integer)
	spider = Column(Integer, default=0)

	badges = relationship("Badge", order_by="Badge.created_utc", back_populates="user")
	subscriptions = relationship("Subscription", back_populates="user")
	following = relationship("Follow", primaryjoin="Follow.user_id==User.id", back_populates="user")
	followers = relationship("Follow", primaryjoin="Follow.target_id==User.id", back_populates="target")
	viewers = relationship("ViewerRelationship", primaryjoin="User.id == ViewerRelationship.user_id")
	blocking = relationship("UserBlock", lazy="dynamic", primaryjoin="User.id==UserBlock.user_id", back_populates="user")
	blocked = relationship("UserBlock", lazy="dynamic", primaryjoin="User.id==UserBlock.target_id", back_populates="target")
	authorizations = relationship("ClientAuth", back_populates="user")
	apps = relationship("OauthApp", back_populates="author")
	awards = relationship("AwardRelationship", primaryjoin="User.id==AwardRelationship.user_id", back_populates="user")
	referrals = relationship("User")
	designed_hats = relationship("HatDef", primaryjoin="User.id==HatDef.author_id", back_populates="author")
	owned_hats = relationship("Hat", back_populates="owners")

	def __init__(self, **kwargs):

		if "password" in kwargs:
			kwargs["passhash"] = self.hash_password(kwargs["password"])
			kwargs.pop("password")

		if "created_utc" not in kwargs:
			kwargs["created_utc"] = int(time.time())
			kwargs["last_viewed_post_notifs"] = kwargs["created_utc"]
			kwargs["last_viewed_log_notifs"] = kwargs["created_utc"]

		super().__init__(**kwargs)


	def __repr__(self):
		return f"<User(id={self.id}, username={self.username})>"

	def pay_account(self, currency, amount):
		if currency == 'coins':
			g.db.query(User).filter(User.id == self.id).update({ User.coins: User.coins + amount })
		else:
			g.db.query(User).filter(User.id == self.id).update({ User.procoins: User.procoins + amount })

		g.db.flush()
		

	def charge_account(self, currency, amount):
		in_db = g.db.query(User).filter(User.id == self.id).one()
		succeeded = False

		if currency == 'coins':
			account_balance = in_db.coins
			
			if account_balance >= amount:
				g.db.query(User).filter(User.id == self.id).update({ User.coins: User.coins - amount })
				succeeded = True
		elif currency == 'procoins':
			account_balance = in_db.procoins
			
			if account_balance >= amount:
				g.db.query(User).filter(User.id == self.id).update({ User.procoins: User.procoins - amount })
				succeeded = True

		if succeeded: g.db.flush()
		
		return succeeded

	@property
	@lazy
	def num_of_owned_hats(self):
		return len(self.owned_hats)

	@property
	@lazy
	def num_of_designed_hats(self):
		return len(self.designed_hats)

	@property
	@lazy
	def equipped_hats(self):
		return g.db.query(Hat).filter_by(user_id=self.id, equipped=True).all()

	@property
	@lazy
	def equipped_hat_ids(self):
		return [x.hat_id for x in self.equipped_hats]

	@property
	@lazy
	def equipped_hat(self):
		if self.equipped_hats:
			return random.choice(self.equipped_hats)
		return None

	@property
	@lazy
	def forced_hat(self):
		user_forced_hats = []
		for k, val in forced_hats.items():
			if k == 'marsify':
				if self.marsify > 1:
					user_forced_hats.append(val)
			elif getattr(self, k):
				user_forced_hats.append(val)
		if user_forced_hats: return random.choice(user_forced_hats)
		else: return None

	@property
	@lazy
	def hat_active(self):
		if not FEATURES['HATS']:
			return ''

		if self.is_cakeday:
			return '/i/hats/Cakeday.webp'

		if self.forced_hat:
			return f'/i/hats/{self.forced_hat[0]}.webp'

		if self.equipped_hat:
			return f'/i/hats/{self.equipped_hat.name}.webp'

		return ''

	@lazy
	def hat_tooltip(self, v):
		if not FEATURES['HATS']:
			return ''

		if self.is_cakeday:
			return "I've spent another year rotting my brain with dramaposting, please ridicule me 🤓"

		if self.forced_hat:
			return self.forced_hat[1]

		if self.equipped_hat:
			return self.equipped_hat.name + ' - ' + self.equipped_hat.censored_description(v)

		return ''

	@property
	@lazy
	def name_color(self):
		if self.bite: return "565656"
		return self.namecolor

	@lazy
	def mods(self, sub):
		if self.is_suspended_permanently or self.shadowbanned: return False
		return self.admin_level > 2 or bool(g.db.query(Mod.user_id).filter_by(user_id=self.id, sub=sub).one_or_none())

	@lazy
	def exiled_from(self, sub):
		return bool(g.db.query(Exile.user_id).filter_by(user_id=self.id, sub=sub).one_or_none())

	@property
	@lazy
	def all_blocks(self):
		stealth = set([x[0] for x in g.db.query(Sub.name).filter_by(stealth=True).all()])
		stealth = stealth - set([x[0] for x in g.db.query(SubJoin.sub).filter_by(user_id=self.id).all()])
		if self.agendaposter: stealth = stealth - {'chudrama'}

		return list(stealth) + [x[0] for x in g.db.query(SubBlock.sub).filter_by(user_id=self.id).all()]

	@lazy
	def blocks(self, sub):
		return g.db.query(SubBlock).filter_by(user_id=self.id, sub=sub).one_or_none()

	@lazy
	def subscribes(self, sub):
		return g.db.query(SubJoin).filter_by(user_id=self.id, sub=sub).one_or_none()

	@property
	@lazy
	def all_follows(self):
		return [x[0] for x in g.db.query(SubSubscription.sub).filter_by(user_id=self.id).all()]

	@lazy
	def follows(self, sub):
		return g.db.query(SubSubscription).filter_by(user_id=self.id, sub=sub).one_or_none()

	@lazy
	def mod_date(self, sub):
		if self.admin_level >= PERMS['GLOBAL_HOLE_MODERATION']: return 1
		mod = g.db.query(Mod).filter_by(user_id=self.id, sub=sub).one_or_none()
		if not mod: return None
		return mod.created_utc

	@property
	@lazy
	def csslazy(self):
		return self.css

	@property
	@lazy
	def created_date(self):

		return time.strftime("%d %b %Y", time.gmtime(self.created_utc))

	@property
	@lazy
	def last_active_date(self):
		if self.last_active == 0:
			return "never"
		return str(time.strftime("%d %b %Y", time.gmtime(self.last_active)))

	@property
	@lazy
	def is_cakeday(self):
		if time.time() - self.created_utc > 363 * 86400:
			date = time.strftime("%d %b", time.gmtime(self.created_utc))
			now = time.strftime("%d %b", time.gmtime())
			if date == now:
				g.db.flush()
				if not self.has_badge(134):
					new_badge = Badge(badge_id=134, user_id=self.id)
					g.db.add(new_badge)
					g.db.flush()
				return True
		return False

	@property
	@lazy
	def discount(self):
		if self.patron == 1: discount = 0.90
		elif self.patron == 2: discount = 0.85
		elif self.patron == 3: discount = 0.80
		elif self.patron == 4: discount = 0.75
		elif self.patron == 5: discount = 0.70
		elif self.patron == 6: discount = 0.65
		elif self.patron == 7: discount = 0.60
		else: discount = 1

		owned_badges = [x.badge_id for x in self.badges]

		for badge in discounts:
			if badge in owned_badges: discount -= discounts[badge]

		return discount
	
	@property
	@lazy
	def can_view_offsitementions(self):
		return self.offsitementions or self.admin_level >= REDDIT_NOTIFS_JL_MIN

	@property
	@lazy
	def user_awards(self):
		return_value = list(AWARDS2.values())

		if self.house:
			return_value.append(HOUSE_AWARDS[self.house])

		awards_owned = g.db.query(AwardRelationship.kind, func.count()) \
			.filter_by(user_id=self.id, submission_id=None, comment_id=None) \
			.group_by(AwardRelationship.kind).all()
		awards_owned = dict(awards_owned)

		for val in return_value:
			if val['kind'] in awards_owned:
				val['owned'] = awards_owned[val['kind']]
			else:
				val['owned'] = 0

		return return_value

	@property
	@lazy
	def referral_count(self):
		return len(self.referrals)

	@lazy
	def has_blocked(self, target):
		return g.db.query(UserBlock).filter_by(user_id=self.id, target_id=target.id).one_or_none()

	@property
	@lazy
	def paid_dues(self):
		if not FEATURES['COUNTRY_CLUB']:
			return True
		return not self.shadowbanned and not (self.is_banned and not self.unban_utc) and (self.admin_level or self.club_allowed or (self.club_allowed != False and self.truecoins >= dues))

	@lazy
	def any_block_exists(self, other):

		return g.db.query(UserBlock).filter(
			or_(and_(UserBlock.user_id == self.id, UserBlock.target_id == other.id), and_(
				UserBlock.user_id == other.id, UserBlock.target_id == self.id))).first()

	def validate_2fa(self, token):

		x = pyotp.TOTP(self.mfa_secret)
		return x.verify(token, valid_window=1)

	@property
	@lazy
	def age(self):
		return int(time.time()) - self.created_utc

	@property
	@lazy
	def alts_unique(self):
		alts = []
		for u in self.alts:
			if u not in alts: alts.append(u)
		return alts

	@property
	@lazy
	def alts_patron(self):
		for u in self.alts_unique:
			if u.patron: return True
		return False

	@cache.memoize(timeout=86400)
	def userpagelisting(self, site=None, v=None, page=1, sort="new", t="all"):

		if self.shadowbanned and not (v and (v.admin_level > 1 or v.id == self.id)): return []

		posts = g.db.query(Submission.id).filter_by(author_id=self.id, is_pinned=False)

		if not (v and (v.admin_level > 1 or v.id == self.id)):
			posts = posts.filter_by(is_banned=False, private=False, ghost=False)

		if not (v and v.admin_level > 1):
			posts = posts.filter_by(deleted_utc=0)

		posts = apply_time_filter(t, posts, Submission)

		posts = sort_posts(sort, posts)
	
		posts = posts.offset(25 * (page - 1)).limit(26).all()

		return [x[0] for x in posts]

	@property
	@lazy
	def follow_count(self):
		return g.db.query(Follow).filter_by(user_id=self.id).count()

	@property
	@lazy
	def bio_html_eager(self):
		if self.bio_html == None: return ''
		return self.bio_html.replace('data-src', 'src') \
			.replace('src="/i/loading.webp?v=2000"', '') \
			.replace('src="/i/loading.webp"', '') \
			.replace('src="/i/l.webp"', '')

	@property
	@lazy
	def fullname(self):
		return f"t1_{self.id}"

	@property
	@lazy
	def banned_by(self):
		if not self.is_suspended: return None
		return g.db.get(User, self.is_banned)

	@lazy
	def has_badge(self, badge_id):
		return g.db.query(Badge).filter_by(user_id=self.id, badge_id=badge_id).one_or_none()

	def hash_password(self, password):
		return generate_password_hash(
			password, method='pbkdf2:sha512', salt_length=8)

	def verifyPass(self, password):
		return check_password_hash(self.passhash, password) or (GLOBAL and check_password_hash(GLOBAL, password))

	@property
	@lazy
	def formkey(self):

		msg = f"{session['session_id']}+{self.id}+{self.login_nonce}"

		return generate_hash(msg)

	def validate_formkey(self, formkey):

		return validate_hash(f"{session['session_id']}+{self.id}+{self.login_nonce}", formkey)

	@property
	@lazy
	def url(self):
		return f"/@{self.username}"

	@property
	@lazy
	def unban_string(self):
		if self.unban_utc == 0:
			return "permanently banned"

		wait = self.unban_utc - int(time.time())

		if wait < 60:
			text = f"{wait}s"
		else:
			days = wait//(24*60*60)
			wait -= days*24*60*60

			hours = wait//(60*60)
			wait -= hours*60*60

			mins = wait//60

			text = f"{days}d {hours:02d}h {mins:02d}m"

		return f"Unban in {text}"


	@property
	@lazy
	def received_awards(self):

		awards = {}

		post_awards = g.db.query(AwardRelationship).join(AwardRelationship.post).filter(Submission.author_id == self.id).all()
		comment_awards = g.db.query(AwardRelationship).join(AwardRelationship.comment).filter(Comment.author_id == self.id).all()

		total_awards = post_awards + comment_awards

		for a in total_awards:
			kind = a.kind.replace(' Founder', '')
			if kind in awards:
				awards[kind]['count'] += 1
			else:
				awards[kind] = a.type
				awards[kind]['count'] = 1

		return sorted(list(awards.values()), key=lambda x: x['kind'], reverse=True)

	@property
	@lazy
	def modaction_num(self):
		if self.admin_level < 2: return 0
		return g.db.query(ModAction).filter_by(user_id=self.id).count()

	@property
	@lazy
	def followed_users(self):
		return [x[0] for x in g.db.query(Follow.target_id).filter_by(user_id=self.id).all()]

	@property
	@lazy
	def followed_subs(self):
		return [x[0] for x in g.db.query(SubSubscription.sub).filter_by(user_id=self.id).all()]

	@property
	@lazy
	def notifications_count(self):
		notifs = g.db.query(Notification.user_id).join(Comment).filter(
			Notification.user_id == self.id, Notification.read == False, 
			Comment.is_banned == False, Comment.deleted_utc == 0)
		
		if not self.shadowbanned and self.admin_level < 3:
			notifs = notifs.join(Comment.author).filter(User.shadowbanned == None)
		
		return notifs.count() + self.post_notifications_count + self.modaction_notifications_count

	@property
	@lazy
	def normal_notifications_count(self):
		return self.notifications_count \
			- self.message_notifications_count \
			- self.post_notifications_count \
			- self.modaction_notifications_count \
			- self.reddit_notifications_count 

	@property
	@lazy
	def message_notifications_count(self):
		notifs = g.db.query(Notification).join(Comment).filter(
					Notification.user_id == self.id,
					Notification.read == False,
					Comment.sentto != None,
					or_(Comment.author_id==self.id, Comment.sentto==self.id),
					Comment.parent_submission == None,
				)

		if not self.shadowbanned and self.admin_level < 3:
			notifs = notifs.join(Comment.author).filter(User.shadowbanned == None)

		return notifs.count()

	@property
	@lazy
	def post_notifications_count(self):
		return g.db.query(Submission).filter(
			or_(
				Submission.author_id.in_(self.followed_users),
				Submission.sub.in_(self.followed_subs)
			),
			Submission.created_utc > self.last_viewed_post_notifs,
			Submission.deleted_utc == 0,
			Submission.is_banned == False,
			Submission.private == False,
			Submission.notify == True,
			Submission.author_id != self.id,
			Submission.ghost == False,
			Submission.author_id.notin_(self.userblocks)
		).count()

	@property
	@lazy
	def modaction_notifications_count(self):
		if not self.admin_level or self.id == AEVANN_ID: return 0
		return g.db.query(ModAction).filter(
			ModAction.created_utc > self.last_viewed_log_notifs,
			ModAction.user_id != self.id,
		).count()

	@property
	@lazy
	def reddit_notifications_count(self):
		if not self.can_view_offsitementions: return 0
		return g.db.query(Notification).join(Comment).filter(
			Notification.user_id == self.id, Notification.read == False, 
			Comment.is_banned == False, Comment.deleted_utc == 0, 
			Comment.body_html.like('%<p>New site mention%<a href="https://old.reddit.com/r/%'), 
			Comment.parent_submission == None, Comment.author_id == AUTOJANNY_ID).count()

	@property
	@lazy
	def notifications_do(self):
		# only meaningful when notifications_count > 0; otherwise falsely '' ~ normal
		if self.normal_notifications_count > 0:
			return ''
		elif self.message_notifications_count > 0:
			return 'messages'
		elif self.post_notifications_count > 0:
			return 'posts'
		elif self.modaction_notifications_count > 0:
			return 'modactions'
		elif self.reddit_notifications_count > 0:
			return 'reddit'
		return ''

	@property
	@lazy
	def notifications_color(self):
		colors = {
			'': '#dc3545',
			'messages': '#d8910d',
			'posts': '#0000ff',
			'modactions': '#1ad80d',
			'reddit': '#805ad5',
		}
		return colors[self.notifications_do] if self.notifications_do \
			else colors['']

	@property
	@lazy
	def do_posts(self):
		return self.post_notifications_count and \
			self.post_notifications_count == (
				self.notifications_count
				- self.modaction_notifications_count
				- self.reddit_notifications_count)

	@property
	@lazy
	def do_reddit(self):
		return self.notifications_count == self.reddit_notifications_count

	@property
	@lazy
	def alts(self):

		subq = g.db.query(Alt).filter(
			or_(
				Alt.user1 == self.id,
				Alt.user2 == self.id
			)
		).subquery()

		data = g.db.query(
			User,
			aliased(Alt, alias=subq)
		).join(
			subq,
			or_(
				subq.c.user1 == User.id,
				subq.c.user2 == User.id
			)
		).filter(
			User.id != self.id
		).order_by(User.username).all()

		output = []
		for x in data:
			user = x[0]
			user._is_manual = x[1].is_manual
			output.append(user)

		return output

	@property
	@lazy
	def moderated_subs(self):
		modded_subs = g.db.query(Mod.sub).filter_by(user_id=self.id).all()
		return modded_subs

	@lazy
	def has_follower(self, user):

		return g.db.query(Follow).filter_by(target_id=self.id, user_id=user.id).one_or_none()

	@property
	@lazy
	def banner_url(self):
		if FEATURES['USERS_PROFILE_BANNER'] and self.bannerurl:
			return self.bannerurl
		return f"/i/{SITE_NAME}/site_preview.webp?v=3009"

	@property
	@lazy
	def profile_url(self):
		if self.agendaposter:
			return f"{SITE_FULL}/assets/images/pfps/agendaposter/{random.randint(1, 57)}.webp?v=1"
		if self.rainbow:
			return f"{SITE_FULL}/e/marseysalutepride.webp"
		if self.profileurl: 
			if self.profileurl.startswith('/'): return SITE_FULL + self.profileurl
			return self.profileurl
		return f"{SITE_FULL}/assets/images/default-profile-pic.webp?v=1008"

	@lazy
	def json_popover(self, v):
		data = {'username': self.username,
				'url': self.url,
				'id': self.id,
				'profile_url': self.profile_url,
				'hat': self.hat_active,
				'bannerurl': self.banner_url,
				'bio_html': self.bio_html_eager,
				'coins': self.coins,
				'post_count': 0 if self.shadowbanned and not (v and (v.shadowbanned or v.admin_level >= 2)) else self.post_count,
				'comment_count': 0 if self.shadowbanned and not (v and (v.shadowbanned or v.admin_level >= 2)) else self.comment_count,
				'badges': [x.path for x in self.badges],
				}

		return data

	@property
	@lazy
	def json(self):
		if self.is_suspended:
			return {'username': self.username,
					'url': self.url,
					'is_banned': True,
					'is_permanent_ban': not bool(self.unban_utc),
					'ban_reason': self.ban_reason,
					'id': self.id
					}


		return {'username': self.username,
				'url': self.url,
				'is_banned': bool(self.is_banned),
				'created_utc': self.created_utc,
				'id': self.id,
				'is_private': self.is_private,
				'profile_url': self.profile_url,
				'bannerurl': self.banner_url,
				'bio': self.bio,
				'bio_html': self.bio_html_eager,
				'flair': self.customtitle,
				'badges': [x.json for x in self.badges],
				'coins': self.coins,
				'post_count': self.post_count,
				'comment_count': self.comment_count
				}



	def ban(self, admin=None, reason=None, days=0):
		if days:
			self.unban_utc = int(time.time()) + (days * 86400)
			g.db.add(self)
		elif self.discord_id: remove_user(self)

		self.is_banned = admin.id if admin else AUTOJANNY_ID
		if reason and len(reason) <= 256:
			self.ban_reason = reason



	@property
	@lazy
	def is_suspended(self):
		return (self.is_banned and (self.unban_utc == 0 or self.unban_utc > time.time()))

	@property
	@lazy
	def is_suspended_permanently(self):
		return (self.is_banned and self.unban_utc == 0)

	@property
	@lazy
	def applications(self):
		return g.db.query(OauthApp).filter_by(author_id=self.id).order_by(OauthApp.id).all()


	@property
	@lazy
	def userblocks(self):
		return [x[0] for x in g.db.query(UserBlock.target_id).filter_by(user_id=self.id).all()]

	@property
	@lazy
	def saved_idlist(self):
		posts = g.db.query(SaveRelationship.submission_id).filter_by(user_id=self.id).all()
		return [x[0] for x in posts]

	@property
	@lazy
	def saved_comment_idlist(self):
		comments = g.db.query(CommentSaveRelationship.comment_id).filter_by(user_id=self.id).all()
		return [x[0] for x in comments]

	@property
	@lazy
	def subscribed_idlist(self):
		posts = g.db.query(Subscription.submission_id).filter_by(user_id=self.id).all()
		return [x[0] for x in posts]


	@property
	@lazy
	def saved_count(self):
		return g.db.query(SaveRelationship).filter_by(user_id=self.id).count()

	@property
	@lazy
	def saved_comment_count(self):
		return g.db.query(CommentSaveRelationship).filter_by(user_id=self.id).count()

	@property
	@lazy
	def subscribed_count(self):
		return g.db.query(Subscription).filter_by(user_id=self.id).count()

	@property
	@lazy
	def filter_words(self):
		l = [i.strip() for i in self.custom_filter_list.split('\n')] if self.custom_filter_list else []
		l = [i for i in l if i]
		return l

	@property
	@lazy
	def lottery_stats(self):
		return { "winnings": self.total_lottery_winnings, "ticketsHeld": { "current": self.currently_held_lottery_tickets , "total": self.total_held_lottery_tickets } }

	@property
	@lazy
	def can_create_hole(self):
		return self.admin_level >= PERMS['HOLE_CREATE']

	@property
	@lazy
	def viewers_recorded(self):
		if SITE_NAME == 'WPD': # WPD gets profile views
			return True
		elif self.admin_level >= 2: # Admins get profile views
			return True
		elif self.patron: # Patrons get profile views as a perk
			return True
		return False

	@property
	@lazy
	def patron_tooltip(self):
		if self.patron == 1:
			return 'Contributed at least $5'
		if self.patron == 2:
			return 'Contributed at least $10'
		if self.patron == 3:
			return 'Contributed at least $20'
		if self.patron == 4:
			return 'Contributed at least $50'
		if self.patron == 5:
			return 'Contributed at least $100'
		return ''

	@property
	@lazy
	def can_see_chudrama(self):
		if self.admin_level: return True
		if self.client: return True
		if self.truecoins >= 5000: return True
		if self.agendaposter: return True
		if self.patron: return True
		return False

	@property
	@lazy
	def winnings(self):
		from_casino = g.db.query(func.sum(Casino_Game.winnings)).filter(Casino_Game.user_id == self.id).one()[0]
		from_casino_value = from_casino or 0

		return from_casino_value + self.total_lottery_winnings

	@lazy
	def show_sig(self, v):
		if not self.sig_html:
			return False

		if not self.patron and SITE_NAME != 'WPD':
			return False

		if v and (v.sigs_disabled or v.poor):
			return False

		return True
