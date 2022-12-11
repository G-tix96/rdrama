import requests
import time

from files.helpers.security import *
from files.helpers.config.const import EMAIL, MAILGUN_KEY

from urllib.parse import quote

from flask import render_template

def send_mail(to_address, subject, html):
	if MAILGUN_KEY == DEFAULT_CONFIG_VALUE: return
	url = f"https://api.mailgun.net/v3/{SITE}/messages"
	auth = ("api", MAILGUN_KEY)
	data = {"from": EMAIL,
			"to": [to_address],
			"subject": subject,
			"html": html,
			}
	requests.post(url, auth=auth, data=data)


def send_verification_email(user, email=None):
	if not email:
		email = user.email

	url = f"https://{SITE}/activate"
	now = int(time.time())
	token = generate_hash(f"{email}+{user.id}+{now}")
	params = f"?email={quote(email)}&id={user.id}&time={now}&token={token}"
	link = url + params
	send_mail(to_address=email,
			html=render_template("email/email_verify.html",
								action_url=link,
								v=user),
			subject=f"Verify your {SITE_NAME} account email"
			)
