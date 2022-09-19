from sqlalchemy import *
from sqlalchemy.orm import relationship
from files.__main__ import Base
from files.helpers.lazy import lazy
from files.helpers.const import *
import time

class AwardRelationship(Base):

	__tablename__ = "award_relationships"

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"))
	submission_id = Column(Integer, ForeignKey("submissions.id"))
	comment_id = Column(Integer, ForeignKey("comments.id"))
	kind = Column(String)
	awarded_utc = Column(Integer)
	granted = Column(Boolean)
	created_utc = Column(Integer)

	user = relationship("User", primaryjoin="AwardRelationship.user_id==User.id", back_populates="awards")
	post = relationship("Submission", primaryjoin="AwardRelationship.submission_id==Submission.id", back_populates="awards")
	comment = relationship("Comment", primaryjoin="AwardRelationship.comment_id==Comment.id", back_populates="awards")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<AwardRelationship(id={self.id})>"

	@property
	@lazy
	def type(self):
		if self.kind in AWARDS: return AWARDS[self.kind]
		else: return HOUSE_AWARDS[self.kind]

	@property
	@lazy
	def title(self):
		return self.type['title']

	@property
	@lazy
	def class_list(self):
		return self.type['icon']+' '+self.type['color']
