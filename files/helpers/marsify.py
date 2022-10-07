from .const import marsey_mappings
from random import choice

def marsify(text):
	new_text = ''
	for x in text.split(' '):
		new_text += f'{x} '
		x = x.lower()
		if len(x) > 3 and x in marsey_mappings:
			marsey = choice(marsey_mappings[x])
			new_text += f':{marsey}: '
	return new_text
