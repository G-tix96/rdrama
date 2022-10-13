from flask import *
from sqlalchemy import *
from sqlalchemy.orm import relationship
from .submission import Submission
from .comment import Comment
from files.__main__ import Base
from files.helpers.lazy import lazy
from files.helpers.const import *
import time

class OauthApp(Base):

	__tablename__ = "oauth_apps"

	id = Column(Integer, primary_key=True)
	client_id = Column(String)
	app_name = Column(String)
	redirect_uri = Column(String)
	description = Column(String)
	author_id = Column(Integer, ForeignKey("users.id"))
	created_utc = Column(Integer)

	author = relationship("User", back_populates="apps")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<OauthApp(id={self.id})>"


	@property
	@lazy
	def permalink(self):
		return f"{SITE_FULL}/admin/app/{self.id}"

	@lazy
	def idlist(self, page=1):

		posts = g.db.query(Submission.id).filter_by(app_id=self.id)
		
		posts=posts.order_by(Submission.created_utc.desc())

		posts=posts.offset(100*(page-1)).limit(101)

		return [x[0] for x in posts.all()]

	@lazy
	def comments_idlist(self, page=1):

		posts = g.db.query(Comment.id).filter_by(app_id=self.id)
		
		posts=posts.order_by(Comment.id.desc())

		posts=posts.offset(100*(page-1)).limit(101)

		return [x[0] for x in posts.all()]



class ClientAuth(Base):

	__tablename__ = "client_auths"

	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	oauth_client = Column(Integer, ForeignKey("oauth_apps.id"), primary_key=True)
	access_token = Column(String)
	created_utc = Column(Integer)

	user = relationship("User")
	application = relationship("OauthApp")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<ClientAuth(user_id={self.user_id}, oauth_client={self.oauth_client})>"
