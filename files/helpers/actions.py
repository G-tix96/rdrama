from flask import g, abort
from files.classes.user import User
from files.classes.badges import Badge, BadgeDef

# TODO: More sanity checks on passed parameters.
# TODO: Add `replace=False` parameter which, when set true, removes any 
#       existing badge with identical id & user and replaces with new one.
def badge_grant(user_id, badge_id, desc='', url=''):
	user = g.db.query(User).filter(User.id == int(user_id)).one_or_none()
	if not user:
		return False
	elif user.has_badge(badge_id):
		return True

	badge = Badge(
		badge_id=int(badge_id), 
		user_id=user.id,
		description=desc if desc != '' else None,
		url=url if url != '' else None,
	)

	g.db.add(badge)
	g.db.commit()
	return True
