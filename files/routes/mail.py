import time

from files.classes import *
from files.helpers.const import *
from files.helpers.get import *
from files.helpers.mail import *
from files.helpers.useractions import *
from files.routes.wrappers import *
from files.__main__ import app, limiter

@app.post("/verify_email")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@auth_required
@ratelimit_user()
def verify_email(v):
	send_verification_email(v)
	return {"message": "Email has been sent (ETA ~5 minutes)"}


@app.get("/activate")
@auth_required
def activate(v):
	email = request.values.get("email", "").strip().lower()

	if not email_regex.fullmatch(email):
		return render_template("message.html", v=v, title="Invalid email.", error="Invalid email."), 400

	id = request.values.get("id", "").strip()
	timestamp = int(request.values.get("time", "0"))
	token = request.values.get("token", "").strip()

	if int(time.time()) - timestamp > 3600:
		return render_template("message.html", v=v, title="Verification link expired.",
							message="This link has expired. Visit your settings to send yourself another verification email."), 410

	user = get_account(id)

	if not validate_hash(f"{email}+{id}+{timestamp}", token):
		abort(403)

	if user.is_activated and user.email == email:
		return render_template("message_success.html", v=v, title="Email already verified.", message="Email already verified."), 404

	user.email = email
	user.is_activated = True

	badge_grant(user=user, badge_id=2)

	g.db.add(user)

	return render_template("message_success.html", v=v, title="Email verified.", message=f"Your email {email} has been verified. Thank you.")
