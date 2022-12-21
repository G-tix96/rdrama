import time
import secrets

from random import randint
from typing import Optional, Union

from flask import g, session

from files.classes import Alt, Comment, User, Submission
from files.helpers.config.const import *
from files.helpers.security import generate_hash, validate_hash

def get_raw_formkey(u:User):
	if not session.get("session_id"):
		session.permanent = True
		session["session_id"] = secrets.token_hex(49)

	return f"{session['session_id']}+{u.id}+{u.login_nonce}"

def get_formkey(u:Optional[User]):
	if not u: return "" # if no user exists, give them a blank formkey
	return generate_hash(get_raw_formkey(u))

def validate_formkey(u:User, formkey:Optional[str]) -> bool:
	if not formkey: return False
	return validate_hash(get_raw_formkey(u), formkey)

def check_for_alts(current:User, include_current_session=True):
	current_id = current.id
	if current_id in (1691,6790,7069,36152) and include_current_session:
		session["history"] = []
		return
	ids = [x[0] for x in g.db.query(User.id).all()]
	past_accs = set(session.get("history", [])) if include_current_session else set()

	def add_alt(user1:int, user2:int):
		if SITE == 'rdrama.net' and (user1 in DONT_LINK_ALTS or user2 in DONT_LINK_ALTS): return
		li = [user1, user2]
		existing = g.db.query(Alt).filter(Alt.user1.in_(li), Alt.user2.in_(li)).one_or_none()
		if not existing:
			new_alt = Alt(user1=user1, user2=user2)
			g.db.add(new_alt)
			g.db.flush()

	for past_id in list(past_accs):
		if past_id not in ids:
			past_accs.remove(past_id)
			continue

		if past_id == current_id: continue

		li = [past_id, current_id]
		add_alt(past_id, current_id)
		other_alts = g.db.query(Alt).filter(Alt.user1.in_(li), Alt.user2.in_(li)).all()
		for a in other_alts:
			if a.deleted:
				if include_current_session:
					try: session["history"].remove(a.user1)
					except: pass
					try: session["history"].remove(a.user2)
					except: pass
				continue # don't propagate deleted alt links
			if a.user1 != past_id: add_alt(a.user1, past_id)
			if a.user1 != current_id: add_alt(a.user1, current_id)
			if a.user2 != past_id: add_alt(a.user2, past_id)
			if a.user2 != current_id: add_alt(a.user2, current_id)
	
	past_accs.add(current_id)
	if include_current_session:
		session["history"] = list(past_accs)
	g.db.flush()
	for u in current.alts_unique:
		if u._alt_deleted: continue
		if u.shadowbanned:
			current.shadowbanned = u.shadowbanned
			current.ban_reason = u.ban_reason
			g.db.add(current)
		elif current.shadowbanned:
			u.shadowbanned = current.shadowbanned
			u.ban_reason = current.ban_reason
			g.db.add(u)

def execute_shadowban_viewers_and_voters(v:Optional[User], target:Union[Submission, Comment]):
	if not v or not v.shadowbanned: return
	if not target: return
	if v.id != target.author_id: return
	if not (86400 > time.time() - target.created_utc > 60): return
	ti = max(int((time.time() - target.created_utc)/60), 1)
	max_upvotes = min(ti, 13)
	rand = randint(0, max_upvotes)
	if target.upvotes >= rand: return
	
	amount = randint(0, 3)
	if amount != 1: return

	target.upvotes += amount
	if isinstance(target, Submission):
		target.views += amount*randint(3, 5)
	g.db.add(target)
