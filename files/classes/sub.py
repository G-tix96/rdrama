from sqlalchemy import *
from sqlalchemy.orm import relationship
from files.__main__ import Base
from files.helpers.lazy import lazy
from files.helpers.const import *
from .sub_block import *


class Sub(Base):
	__tablename__ = "subs"
	name = Column(String, primary_key=True)
	sidebar = Column(String)
	sidebar_html = Column(String)
	sidebarurl = Column(String)
	bannerurl = Column(String)
	css = Column(String)

	blocks = relationship("SubBlock", primaryjoin="SubBlock.sub==Sub.name")
	followers = relationship("SubSubscription", primaryjoin="SubSubscription.sub==Sub.name")

	def __repr__(self):
		return f"<Sub(name={self.name})>"

	@property
	@lazy
	def sidebar_url(self):
		if self.sidebarurl: return SITE_FULL + self.sidebarurl
		return f'/i/{SITE_NAME}/sidebar.webp?v=2000'

	@property
	@lazy
	def banner_url(self):
		if self.bannerurl: return SITE_FULL + self.bannerurl
		return f'/i/{SITE_NAME}/banner.webp?v=2000'

	@property
	@lazy
	def subscription_num(self):
		return self.subscriptions.count()

	@property
	@lazy
	def block_num(self):
		return len(self.blocks)

	@property
	@lazy
	def follow_num(self):
		return len(self.followers)