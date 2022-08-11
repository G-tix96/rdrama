from sqlalchemy import *
from sqlalchemy.orm import relationship
from files.__main__ import Base

class Category(Base):
	__tablename__ = "category"

	id = Column(Integer, primary_key=True, nullable=False)
	name = Column(String(128), nullable=False)
	sub = Column(String(20), ForeignKey("subs.name"))
	color_text = Column(String(6))
	color_bg = Column(String(6))

	def as_json(self):
		data = {
			'id': self.id,
			'name': self.name,
			'sub': self.sub if self.sub else '',
			'color_text': '#' + self.color_text,
			'color_bg': '#' + self.color_bg,
		}
		return data
